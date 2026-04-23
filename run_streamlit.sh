#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example. Please configure AI_PROVIDER and related variables in .env before using translation/review."
fi

set -a
source .env
set +a

streamlit run streamlit_app.py
