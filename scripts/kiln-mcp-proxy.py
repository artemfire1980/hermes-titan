#!/usr/bin/env python3
"""MCP stdio-proxy для Kiln.

Запускает `kiln3d serve` как дочерний процесс и прозрачно
проксирует stdin/stdout между Hermes и Kiln.

Первый initialize займёт ~70 сек (Kiln грузит 46 плагинов),
дальше — всё быстро.

Переменные окружения:
    KILN_BIN            — путь к kiln3d
    KILN_LOG_LEVEL      — уровень логирования Kiln (default: ERROR)
    KILN_NO_UPDATE_CHECK — отключить проверку обновлений (default: 1)
    KILN_PROXY_LOG      — куда писать stderr прокси (default: /tmp/kiln-proxy.log)
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path

KILN_BIN = os.environ.get(
    "KILN_BIN",
    str(Path.home() / ".cache/uv/archive-v0/vZuWT9b7EakyQtIV/bin/kiln3d"),
)
LOG_LEVEL = os.environ.get("KILN_LOG_LEVEL", "ERROR")
NO_UPDATE = os.environ.get("KILN_NO_UPDATE_CHECK", "1")
PROXY_LOG = os.environ.get("KILN_PROXY_LOG", "/tmp/kiln-proxy.log")


def log(msg: str) -> None:
    with open(PROXY_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{os.getpid()}] {msg}\n")


def main() -> int:
    if not Path(KILN_BIN).exists():
        log(f"FATAL: KILN_BIN not found: {KILN_BIN}")
        return 1
    if not os.access(KILN_BIN, os.X_OK):
        log(f"FATAL: KILN_BIN not executable: {KILN_BIN}")
        return 1

    env = os.environ.copy()
    env["KILN_LOG_LEVEL"] = LOG_LEVEL
    if NO_UPDATE == "1":
        env["KILN_NO_UPDATE_CHECK"] = "1"

    log(f"starting: {KILN_BIN} serve (log_level={LOG_LEVEL})")

    proc = subprocess.Popen(
        [KILN_BIN, "serve"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        bufsize=0,
    )

    def pipe_stdin_to_kiln() -> None:
        """sys.stdin.buffer → proc.stdin."""
        try:
            assert sys.stdin.buffer is not None
            assert proc.stdin is not None
            while True:
                chunk = sys.stdin.buffer.read(65536)
                if not chunk:
                    break
                proc.stdin.write(chunk)
                proc.stdin.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            log(f"stdin pipe error: {e!r}")
        finally:
            try:
                if proc.stdin is not None:
                    proc.stdin.close()
            except Exception:
                pass

    def pipe_kiln_to_stdout() -> None:
        """proc.stdout → sys.stdout.buffer."""
        try:
            assert proc.stdout is not None
            assert sys.stdout.buffer is not None
            while True:
                chunk = proc.stdout.read(65536)
                if not chunk:
                    break
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            log(f"stdout pipe error: {e!r}")

    def drain_stderr() -> None:
        """proc.stderr → лог-файл."""
        try:
            assert proc.stderr is not None
            for line in iter(proc.stderr.readline, b""):
                log(f"kiln: {line.decode(errors='replace').rstrip()}")
        except Exception as e:
            log(f"stderr drain error: {e!r}")

    t_in = threading.Thread(target=pipe_stdin_to_kiln, daemon=True)
    t_out = threading.Thread(target=pipe_kiln_to_stdout, daemon=True)
    t_err = threading.Thread(target=drain_stderr, daemon=True)

    t_in.start()
    t_out.start()
    t_err.start()

    try:
        rc = proc.wait()
    except KeyboardInterrupt:
        log("KeyboardInterrupt — terminating Kiln")
        proc.terminate()
        try:
            rc = proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            rc = proc.wait()

    log(f"kiln exited with code {rc}")
    return rc or 0


if __name__ == "__main__":
    sys.exit(main())
