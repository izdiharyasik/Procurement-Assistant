#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example. Please set OPENAI_API_KEY in .env before using translation/review."
fi

set -a
source .env
set +a

streamlit run streamlit_app.py
