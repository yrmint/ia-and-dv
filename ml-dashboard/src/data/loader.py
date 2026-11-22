from pathlib import Path
import pandas as pd

from config import PREDICTIONS_PATH, INCIDENTS_PATH, ID_COL


def _read_parquet(path: Path, required: bool = True) -> pd.DataFrame:
    if not path.exists():
        if required:
            raise FileNotFoundError(
                f"Файл не найден: {path}\n"
                "Поместите parquet-файл в ia-and-dv/data/ "
            )
        return pd.DataFrame()
    return pd.read_parquet(path)


def load_data():
    """Load inference results and optional source incident features."""
    predictions = _read_parquet(Path(PREDICTIONS_PATH))
    incidents = _read_parquet(Path(INCIDENTS_PATH), required=False)

    if ID_COL not in predictions.columns:
        raise ValueError(f"В predictions отсутствует обязательная колонка {ID_COL!r}")

    # Add features from the raw incident table only when they are absent
    # from the inference table. Avoid duplicate column names after the join.
    if not incidents.empty and ID_COL in incidents.columns:
        missing = [c for c in incidents.columns
                   if c == ID_COL or c not in predictions.columns]
        extra = incidents[missing].drop_duplicates(ID_COL)
        predictions = predictions.merge(extra, on=ID_COL, how="left")

    return predictions, incidents
