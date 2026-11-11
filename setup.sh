#!/usr/bin/env bash
# One-shot workspace setup (Linux/macOS/Git-Bash). Windows PowerShell users: run the steps by hand.
set -e
python3 -m venv floodenv
source floodenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python src/03_check_env.py

if [ ! -d .git ]; then
  git init -b main
  git add .
  git commit -m "AGT-309: initial workspace scaffold"
fi
echo "Setup complete. Next: edit config.yaml, then python src/01_define_aoi.py"
