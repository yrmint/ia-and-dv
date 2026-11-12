from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
DATA_PATH = DATA_DIR / "iavd_incidents_raw_target.parquet"

APP_TITLE = "SOC Incident Dashboard"
