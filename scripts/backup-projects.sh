#!/bin/bash
set -euo pipefail
BACKUP=~/ai-system/backup-projects
SOURCE=~/projects

# rsync без вложенных .git (иначе они попадут как пустые gitlink)
rsync -a --exclude='node_modules' --exclude='__pycache__' \
  --exclude='*.pyc' --exclude='.env*' --exclude='.git/' \
  "$SOURCE/" "$BACKUP/projects/"

cd "$BACKUP"
git add -A
if git diff --cached --quiet; then
    echo "No changes in projects"
    exit 0
fi
git commit -qm "projects snapshot $(date +%F-%H%M)"
if ! git push -q origin main 2>&1 && ! git push -q origin master 2>&1; then
    echo "ERROR: git push failed for projects backup" >&2
    exit 1
fi
echo "✅ Projects backup pushed successfully"
