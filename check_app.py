"""check_app.py
Simple validation script used by CI to import the app and exercise data loading.
Exits with non-zero code on failure so the workflow fails early.
"""
import sys
from importlib import util
from pathlib import Path


def main():
    try:
        p = Path(__file__).parent / "app.py"
        if not p.exists():
            print("ERROR: app.py not found next to check_app.py")
            return 4
        spec = util.spec_from_file_location("app_module", str(p))
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "load_data"):
            print("ERROR: app.py does not define load_data()")
            return 2
        df = mod.load_data()
        print(f"OK: load_data returned {len(df)} rows")
        # quick sanity checks
        # Accept common column name variants so the app can be localized.
        column_aliases = {
            "City": ["City", "Ville", "nom", "city"],
            "Population": ["Population", "population", "pop", "population_total"],
        }

        missing = []
        used = {}
        for logical, aliases in column_aliases.items():
            found = next((a for a in aliases if a in df.columns), None)
            if not found:
                missing.append(logical)
            else:
                used[logical] = found

        if missing:
            print("ERROR: Missing required logical columns:", missing)
            print("Available columns:", list(df.columns))
            return 3

        print("INFO: using columns:", used)
        return 0
    except Exception as e:
        print("ERROR while validating app:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
