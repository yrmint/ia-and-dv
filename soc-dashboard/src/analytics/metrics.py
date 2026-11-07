import pandas as pd


def calculate_metrics(df: pd.DataFrame) -> dict:
    return {
        "total": len(df),
        "open": df["status"].isin(["Новый", "В работе", "Ожидание"]).sum(),
        "critical": (df["criticality"] == "Критическая").sum(),
        "confirmed": (
                df["verdict"] == "Подтвержденный инцидент"
        ).sum(),
    }
