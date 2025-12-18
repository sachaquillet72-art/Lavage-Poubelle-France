Live demo
=========

Live Streamlit app: https://lavage-poubelle-france-dymspjckkyacsshqwfb7hz.streamlit.app/

If you see **"Main module does not exist"** in Streamlit Cloud:

1. Open your app in https://share.streamlit.io and click **Manage** → **Settings**.
2. Set **Main file** to `app.py` (or `main.py` — included as a fallback).
3. Set **Visibility** to **Public** (or "Anyone with link") so the app is accessible.

The repository contains a GitHub Actions workflow that regenerates the INSEE communes CSV and validates the app on every push to `main`.

If you want, I can also remove the `cities_insee.csv` from the repo and fetch it at runtime to reduce repo size — tell me which you prefer.
