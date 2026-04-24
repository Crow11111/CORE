#!/bin/bash
cd /OMEGA_CORE
source .venv/bin/activate
uvicorn src.api.db_backend:app --host 0.0.0.0 --port 8000 --reload &
