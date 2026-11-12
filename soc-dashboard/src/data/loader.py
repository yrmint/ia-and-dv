from pathlib import Path

import pandas as pd
from config import DATA_PATH


def load_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Loads data."""

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Файл с данными не найден: {path}")

    df = pd.read_parquet(path)

    required_columns = ["EntityId", "Создан"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"В датасете отсутствуют обязательные колонки: {missing_columns}"
        )

    df["Создан"] = pd.to_datetime(df["Создан"], errors="coerce")

    column_mapping = {
        "registered_at": "Создан",
        "verdict": "Вердикт",
        "criticality": "Критичность",
        "status": "Фаза реагирования",
        "source": "Источник инцидента",
        "asset": "Hostname Цели",
        "description": "Описание инцидента",
        "analyst": "Ответственный",
    }

    for new_column, source_column in column_mapping.items():
        if source_column in df.columns:
            df[new_column] = df[source_column]
        else:
            df[new_column] = pd.NA

    if "Алерт" in df.columns:
        df["description"] = df["description"].fillna(df["Алерт"])

    text_columns = [
        "verdict",
        "criticality",
        "status",
        "source",
        "asset",
        "description",
        "analyst",
    ]

    for column in text_columns:
        df[column] = df[column].fillna("Не указано").astype(str)

    return df

