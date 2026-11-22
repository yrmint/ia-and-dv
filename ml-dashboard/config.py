from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

PREDICTIONS_PATH = DATA_DIR / "MODEL_PREDICTIONS_target.parquet"
INCIDENTS_PATH = DATA_DIR / "iavd_incidents_raw3_target.parquet"

APP_TITLE = "Оценка качества ML-инференса в SOC"

ID_COL = "incident_id"
