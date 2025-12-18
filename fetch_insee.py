"""fetch_insee.py
Fetch all French communes from geo.api.gouv.fr and save to cities_insee.csv
"""
import requests
import pandas as pd

URL = (
    "https://geo.api.gouv.fr/communes?fields=nom,code,codeDepartement,codeRegion,population,centre&format=json&geometry=centre&limit=50000"
)


def fetch(save_path="cities_insee.csv"):
    print("Fetching communes from geo.api.gouv.fr...")
    r = requests.get(URL, timeout=30)
    r.raise_for_status()
    data = r.json()
    rows = []
    for c in data:
        centre = c.get("centre") or {}
        coords = centre.get("coordinates") if isinstance(centre, dict) else None
        lon, lat = (coords[0], coords[1]) if coords and len(coords) >= 2 else (None, None)
        rows.append(
            {
                "nom": c.get("nom"),
                "code": c.get("code"),
                "codeDepartement": c.get("codeDepartement"),
                "codeRegion": c.get("codeRegion"),
                "population": c.get("population") or 0,
                "lat": lat,
                "lon": lon,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(save_path, index=False)
    print(f"Saved {len(df)} communes to {save_path}")


if __name__ == "__main__":
    fetch()
