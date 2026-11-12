import pandas as pd


def calculate_metrics(df: pd.DataFrame) -> dict:
    status = df["status"].fillna("").astype(str)
    criticality = df["criticality"].fillna("").astype(str)
    verdict = df["verdict"].fillna("").astype(str)

    return {
        "total": len(df),

        "open": status.str.contains(
            r"Новый|В работе|Ожидание",
            regex=True,
            na=False,
        ).sum(),

        "critical": (criticality == "Критическая").sum(),

        "confirmed": (verdict == "Подтвержденный инцидент").sum(),
    }
