import numpy as np
import pandas as pd
from config import PREDICTION_COL, TARGET_COL, VALID_LABEL_COL


def _binary(series):
    """Normalize common binary encodings to nullable integers 0/1."""
    if series is None:
        return pd.Series(dtype="Int64")
    if pd.api.types.is_bool_dtype(series):
        return series.astype("Int64")
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().any():
        return numeric.where(numeric.isin([0, 1])).astype("Int64")

    mapping = {
        "1": 1, "true": 1, "yes": 1, "да": 1, "инцидент": 1,
        "0": 0, "false": 0, "no": 0, "нет": 0, "не инцидент": 0,
        "неинцидент": 0,
    }
    return series.astype(str).str.strip().str.lower().map(mapping).astype("Int64")


def prepare_evaluation_data(df):
    data = df.copy()
    if TARGET_COL not in data or PREDICTION_COL not in data:
        return data.iloc[0:0].copy()

    data["_y"] = _binary(data[TARGET_COL])
    data["_pred"] = _binary(data[PREDICTION_COL])

    # If the source explicitly marks labels as invalid, exclude those rows.
    if VALID_LABEL_COL in data.columns:
        flag = data[VALID_LABEL_COL]
        if pd.api.types.is_bool_dtype(flag):
            data = data[flag.fillna(False)]
        else:
            normalized = flag.astype(str).str.strip().str.lower()
            invalid_values = {"0", "false", "no", "нет", "invalid", "невалидна", "невалидный"}
            # Only apply this filter if the column contains recognizable validity values.
            if normalized.isin(invalid_values | {"1", "true", "yes", "да", "valid"}).any():
                data = data[~normalized.isin(invalid_values)]

    return data.dropna(subset=["_y", "_pred"])


def calculate_metrics(df):
    evaluated = prepare_evaluation_data(df)
    total = len(df)
    labeled = len(evaluated)

    if labeled == 0:
        return {
            "total": total, "labeled": 0, "tp": 0, "tn": 0, "fp": 0, "fn": 0,
            "fnr": None, "recall": None, "precision": None, "accuracy": None,
            "agreement": None, "mean_latency": None, "p95_latency": None,
            "evaluated": evaluated,
        }

    y, pred = evaluated["_y"], evaluated["_pred"]
    tp = int(((y == 1) & (pred == 1)).sum())
    tn = int(((y == 0) & (pred == 0)).sum())
    fp = int(((y == 0) & (pred == 1)).sum())
    fn = int(((y == 1) & (pred == 0)).sum())

    actual_positive = tp + fn
    predicted_positive = tp + fp
    accuracy = (tp + tn) / labeled
    recall = tp / actual_positive if actual_positive else None
    fnr = fn / actual_positive if actual_positive else None
    precision = tp / predicted_positive if predicted_positive else None

    # Agreement with the analyst's SOC verdict is reported separately:
    # it is not necessarily the same as agreement with the binary target.
    agreement = None
    if "Вердикт" in evaluated.columns:
        soc = evaluated["Вердикт"].astype(str).str.strip().str.lower()
        # This is only a conservative binary mapping; unknown labels are excluded.
        incident_words = {"инцидент", "true positive", "tp", "1", "да"}
        nonincident_words = {"не инцидент", "неинцидент", "false positive", "fp", "0", "нет"}
        soc_binary = soc.map(lambda x: 1 if x in incident_words else (0 if x in nonincident_words else np.nan))
        comparable = soc_binary.notna()
        if comparable.any():
            agreement = float((soc_binary[comparable].astype(int) ==
                               evaluated.loc[comparable, "_pred"].astype(int)).mean())

    latency = pd.to_numeric(df.get("latency_s", pd.Series(dtype=float)), errors="coerce").dropna()
    return {
        "total": total, "labeled": labeled, "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "fnr": fnr, "recall": recall, "precision": precision,
        "accuracy": accuracy, "agreement": agreement,
        "mean_latency": float(latency.mean()) if len(latency) else None,
        "p95_latency": float(latency.quantile(.95)) if len(latency) else None,
        "evaluated": evaluated,
    }
