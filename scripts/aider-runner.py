#!/usr/bin/env python3
"""Hermes → Aider runner v2.2

Fixes from dual audit:
  - Lock: append mode + truncate after acquisition (no race)
  - Fail-closed git status (error = STOP)
  - Double allowed-root check (requested + git root)
  - Explicit 'origin' check for --push
  - Detached HEAD protection for --push
  - Dirty mode snapshot (pre_existing_changes)
  - Post-flight compile() — no __pycache__
  - killpg on timeout
"""
import argparse, fcntl, json, os, re, signal, subprocess, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import sys as _sys
_sys.path.insert(0, str(Path.home() / 'bin'))
import task_ledger

HOME = Path.home()
AIDER_BIN = HOME / ".aider" / "venv" / "bin" / "aider"
ENV_FILE = HOME / "ai-system" / ".env"
LOG_DIR = HOME / "ai-system" / "logs" / "aider"
LOCK_FILE = HOME / "ai-system" / "runtime" / "locks" / "aider.lock"
MODEL = "nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b"
ALLOWED_ROOTS = [
    HOME / "projects",      # Пользовательские проекты (основная рабочая область)
    HOME / "research",      # Результаты исследований
    HOME / "work",          # Рабочая папка
    HOME / "code",          # Код
    HOME / "dev",           # Разработка
    # Исключены по security policy:
    # HOME / "Desktop"    — системная папка, не для автономного кодинга
    # HOME / "Documents"  — системная папка с личными данными
    # HOME / "Downloads"  — небезопасно (может содержать малварь)
    # HOME / "tmp"        — временная, не нужна для Aider
]

# Критические компоненты системы — Aider НЕ должен их трогать
FORBIDDEN_ROOTS = [
    HOME / "ai-system",              # Сам репозиторий системы
    HOME / ".hermes",                 # Ядро Hermes Agent
    Path("/mnt/ai-ssd/hermes"),       # Физический путь Hermes
]
DEFAULT_TIMEOUT = 1800
MAX_OUTPUT = 12000

def utc_now(): return datetime.now(timezone.utc).isoformat()
def emit(d): print(json.dumps(d, ensure_ascii=False, indent=2))

def fail(tid, status, msg, **kw):
    # Log failure to task ledger (best-effort)
    try:
        ledger_kw = {k: v for k, v in kw.items() 
                    if k in ['elapsed_seconds', 'exit_code', 'dirty_before', 'error_message']}
        project = kw.get('project', 'unknown')
        task_ledger.log_task(tid, str(project), msg, status, 
                            error_message=msg, **ledger_kw)
    except Exception:
        pass
    emit({"ok": False, "task_id": tid, "status": status,
          "message": msg, "timestamp": utc_now(), **kw})
    sys.exit(1)

def run_git(proj, args, timeout=30):
    return subprocess.run(["git"] + args, cwd=proj, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         timeout=timeout, check=False)

def read_env_value(env_file, name):
    if not env_file.exists(): return None
    pat = re.compile(rf"^\s*{re.escape(name)}\s*=\s*(.*?)\s*$")
    with env_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.lstrip().startswith("#"): continue
            m = pat.match(line)
            if not m: continue
            v = m.group(1)
            if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
                v = v[1:-1]
            return v
    return None

def resolve_project(p, tid):
    raw = Path(p).expanduser()
    try: path = raw.resolve(strict=True)
    except FileNotFoundError: fail(tid, "INVALID_PROJECT", f"Not found: {raw}")
    if not path.is_dir(): fail(tid, "INVALID_PROJECT", f"Not dir: {path}")
    
    # CRITICAL: Check FORBIDDEN_ROOTS first (before allowed check)
    for forbidden in FORBIDDEN_ROOTS:
        try:
            path.relative_to(forbidden.expanduser().resolve())
            fail(tid, "INVALID_PROJECT", f"FORBIDDEN: {path} is inside critical system component {forbidden}")
        except ValueError:
            continue
    
    # First check: requested path (only if not forbidden)
    allowed = False
    for root in ALLOWED_ROOTS:
        r = root.expanduser().resolve()
        try: path.relative_to(r); allowed = True; break
        except ValueError: continue
    if not allowed:
        fail(tid, "INVALID_PROJECT", f"Outside allowed: {path}")
    
    # Git root
    r = run_git(path, ["rev-parse", "--show-toplevel"])
    if r.returncode != 0: fail(tid, "NOT_GIT_REPOSITORY", f"Not git: {path}")
    git_root = Path(r.stdout.strip()).resolve()
    
    # Second check: git root
    allowed = False
    for root in ALLOWED_ROOTS:
        r = root.expanduser().resolve()
        try: git_root.relative_to(r); allowed = True; break
        except ValueError: continue
    if not allowed:
        fail(tid, "INVALID_PROJECT", f"Git root outside: {git_root}")
    return git_root

def is_repo_dirty(proj, tid):
    """Fail-closed: error = STOP."""
    r = run_git(proj, ["status", "--porcelain=v1", "--untracked-files=no"])
    if r.returncode != 0:
        fail(tid, "GIT_STATUS_FAILED",
             "Cannot determine repo state", stderr=r.stderr[:1000])
    return bool(r.stdout.strip())

def get_dirty_snapshot(proj):
    r = run_git(proj, ["status", "--porcelain=v1"])
    return r.stdout.splitlines() if r.returncode == 0 else []

def get_head(proj):
    r = run_git(proj, ["rev-parse", "HEAD"])
    return r.stdout.strip() if r.returncode == 0 else None

def get_branch(proj):
    r = run_git(proj, ["rev-parse", "--abbrev-ref", "HEAD"])
    return r.stdout.strip() if r.returncode == 0 else None

def has_origin(proj):
    r = run_git(proj, ["remote", "get-url", "origin"])
    return r.returncode == 0

def get_changed_py(proj, base):
    if not base: return []
    r = run_git(proj, ["diff", "--name-only", f"{base}..HEAD"])
    return [f for f in r.stdout.splitlines() if f.endswith(".py")] if r.returncode == 0 else []

def get_changed_files(proj, base):
    if not base: return []
    r = run_git(proj, ["diff", "--name-status", f"{base}..HEAD"])
    if r.returncode != 0: return []
    out = []
    for line in r.stdout.splitlines():
        if not line.strip(): continue
        parts = line.split("\t")
        if len(parts) >= 2: out.append({"status": parts[0], "file": parts[-1]})
    return out

def post_flight_py_compile(proj, files):
    errors = []
    for f in files:
        full = Path(proj) / f
        if not full.exists(): continue
        try:
            src = full.read_text(encoding="utf-8")
            compile(src, str(full), "exec")
        except SyntaxError as e:
            errors.append({"file": f, "error": f"line {e.lineno}: {e.msg}"})
        except UnicodeDecodeError as e:
            errors.append({"file": f, "error": f"encoding: {e}"})
    return errors

def handle_lock(tid):
    """No race: append + truncate after acquisition. Never unlink/clear."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    h = LOCK_FILE.open("a+", encoding="utf-8")
    try:
        fcntl.flock(h.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        h.seek(0); existing = h.read().strip(); h.close()
        fail(tid, "AIDER_BUSY", "Another Aider task is running.",
             lock_info=existing or "unknown")
    h.seek(0); h.truncate()
    h.write(f"{tid}:{os.getpid()}:{utc_now()}")
    h.flush()
    return h

def main():
    p = argparse.ArgumentParser(description="Hermes → Aider runner v2.2")
    p.add_argument("project")
    p.add_argument("task")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    p.add_argument("--push", action="store_true")
    p.add_argument("--allow-dirty", action="store_true")
    p.add_argument("--task-id", default=None)
    args = p.parse_args()

    tid = args.task_id or str(uuid.uuid4())
    task_ledger.log_task(tid, args.project, args.task, "STARTED")
    t0 = time.monotonic()

    # СНАЧАЛА проверка безопасности (FORBIDDEN_ROOTS), ПОТОМ наличие бинарника
    # Это важно: нет смысла проверять наличие aider для запрещённых путей
    proj = resolve_project(args.project, tid)
    lock_h = handle_lock(tid)
    
    if not AIDER_BIN.exists():
        fail(tid, "AIDER_NOT_FOUND", f"Missing: {AIDER_BIN}")
    
    try:
        dirty = is_repo_dirty(proj, tid)
        dirty_before = dirty
        dirty_before_status = []
        if dirty:
            dirty_before_status = get_dirty_snapshot(proj)
            if not args.allow_dirty:
                r = run_git(proj, ["status", "--porcelain=v1"])
                fail(tid, "DIRTY_REPOSITORY",
                     "Uncommitted changes. Use --allow-dirty.",
                     git_status=r.stdout[:2000],
                     pre_existing_changes=dirty_before_status)

        init_head = get_head(proj)
        branch = get_branch(proj)

        if args.push:
            if not has_origin(proj):
                fail(tid, "NO_ORIGIN_REMOTE", "'origin' not configured")
            if not branch or branch == "HEAD":
                fail(tid, "DETACHED_HEAD", "Cannot push: detached HEAD")

        api_key = (os.environ.get("NVIDIA_API_KEY")
                   or read_env_value(ENV_FILE, "NVIDIA_API_KEY"))
        if not api_key:
            fail(tid, "NVIDIA_API_KEY_MISSING", f"Not in env or {ENV_FILE}")

        cmd = [str(AIDER_BIN), "--model", MODEL,
               "--yes-always", "--message", args.task,
               "--no-pretty", "--auto-commits"]
        if args.allow_dirty: cmd.append("--dirty-commits")

        env = os.environ.copy()
        env["NVIDIA_NIM_API_KEY"] = api_key  # через env, не виден в ps
        env["AIDER_YES_ALWAYS"] = "true"
        env["AIDER_CHECK_UPDATE"] = "false"
        env["AIDER_ANALYTICS"] = "false"

        proc = subprocess.Popen(cmd, cwd=proj, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True)
        try:
            so, se = proc.communicate(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            try: os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception: proc.kill()
            so, se = proc.communicate()
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            lf = LOG_DIR / f"{tid}.log"
            lf.write_text(f"task_id={tid}\nts={utc_now()}\nTIMEOUT\n"
                         f"==== STDOUT ====\n{so}\n==== STDERR ====\n{se}\n",
                         encoding="utf-8")
            fail(tid, "TIMEOUT", f"Killed after {args.timeout}s",
                 project=str(proj), log=str(lf),
                 elapsed_seconds=round(time.monotonic() - t0, 2))

        so, se = so or "", se or ""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        lf = LOG_DIR / f"{tid}.log"
        lf.write_text(f"task_id={tid}\nts={utc_now()}\nproject={proj}\n"
                     f"exit={proc.returncode}\n==== STDOUT ====\n{so}\n"
                     f"==== STDERR ====\n{se}\n", encoding="utf-8")

        r = run_git(proj, ["diff", "--name-only", "--diff-filter=U"])
        if r.stdout.strip():
            fail(tid, "GIT_CONFLICT", "Unmerged files", log=str(lf))

        final = get_head(proj)
        changed = init_head and final and init_head != final

        errs = []
        if changed:
            py_files = get_changed_py(proj, init_head)
            errs = post_flight_py_compile(proj, py_files)
            if errs:
                if not dirty:
                    run_git(proj, ["reset", "--hard", init_head])
                    # НЕ делаем git clean -fd — снесёт неотслеживаемые файлы пользователя
                fail(tid, "POST_FLIGHT_FAILED",
                     "Syntax errors" + ("" if dirty else "; rolled back"),
                     errors=errs, rolled_back=not dirty,
                     dirty_before=dirty_before, log=str(lf))

        elapsed = round(time.monotonic() - t0, 2)
        if proc.returncode != 0:
            fail(tid, "AIDER_FAILED", "Aider exited non-zero",
                 exit_code=proc.returncode, elapsed_seconds=elapsed,
                 log=str(lf), stdout_tail=so[-MAX_OUTPUT:],
                 stderr_tail=se[-MAX_OUTPUT:])

        commit_info, cfiles = None, []
        if changed:
            cfiles = get_changed_files(proj, init_head)
            r = run_git(proj, ["show", "-s", "--format=%H%n%s%n%an", final])
            if r.returncode == 0:
                lines = r.stdout.strip().splitlines()
                if len(lines) >= 2:
                    commit_info = {"hash": lines[0], "short_hash": lines[0][:12],
                                   "message": lines[1],
                                   "author": lines[2] if len(lines) > 2 else None}

        push_res = None
        if args.push and changed:
            r = run_git(proj, ["push", "origin", branch], timeout=60)
            push_res = {"success": r.returncode == 0, "branch": branch,
                       "output": (r.stdout + r.stderr)[:1000]}

        # Log to task ledger
        ledger_data = {
            "initial_head": init_head,
            "final_head": final,
            "exit_code": proc.returncode,
            "elapsed_seconds": elapsed
        }
        if commit_info:
            ledger_data["commit_hash"] = commit_info.get("hash")
            ledger_data["commit_message"] = commit_info.get("message")
        if cfiles:
            ledger_data["changed_files"] = cfiles
        if dirty_before:
            ledger_data["dirty_before"] = 1
            ledger_data["pre_existing_changes"] = dirty_before_status
        try:
            task_ledger.log_task(tid, str(proj), args.task, "COMPLETED", **ledger_data)
        except Exception:
            pass  # Don't let logging block success

        result = {"ok": True, "task_id": tid, "status": "COMPLETED",
                  "project": str(proj), "exit_code": proc.returncode,
                  "elapsed_seconds": elapsed, "commit": commit_info,
                  "changed_files": cfiles, "push": push_res,
                  "log": str(lf), "stdout_tail": so[-MAX_OUTPUT:]}
        if dirty_before:
            result["dirty_before"] = True
            result["pre_existing_changes"] = dirty_before_status
        emit(result)

    finally:
        try:
            fcntl.flock(lock_h.fileno(), fcntl.LOCK_UN)
            lock_h.close()
        except Exception: pass

if __name__ == "__main__":
    main()
