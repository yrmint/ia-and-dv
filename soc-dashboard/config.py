from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_PATH = DATA_DIR / "iavd_incidents_raw_target.parquet"

ID_COLUMN = "EntityId"
DATE_COLUMN = "registered_at"
VERDICT_COLUMN = "verdict"
CRITICALITY_COLUMN = "criticality"
STATUS_COLUMN = "status"

APP_TITLE = "SOC Incident Dashboard"
