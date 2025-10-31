#!/usr/bin/env bash
. venv/bin/activate
uvicorn mock_pdf_generator:app --reload --port ${MPG_PORT:-8000}