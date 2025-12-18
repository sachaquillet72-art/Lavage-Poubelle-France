"""Fallback entrypoint for Streamlit Cloud

This file ensures a module named `main`/`main.py` exists so Streamlit
Cloud can start the app even if the app settings point to `main.py`.
It simply imports and executes `app.py` in the repository root.
"""
from importlib import util
from pathlib import Path
import sys

APP_PATH = Path(__file__).parent / "app.py"

if not APP_PATH.exists():
    raise SystemExit("Error: app.py not found in repository root. Please ensure app.py is present.")

spec = util.spec_from_file_location("app_module", str(APP_PATH))
module = util.module_from_spec(spec)
spec.loader.exec_module(module)
