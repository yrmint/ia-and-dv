import pandas as pd


def apply_filters(
        df: pd.DataFrame,
        date_from,
        date_to,
        verdicts: list[str],
        criticalities: list[str],
) -> pd.DataFrame:
    result = df.copy()

    if date_from:
        result = result[
            result["registered_at"] >= pd.Timestamp(date_from)
            ]

    if date_to:
        end = pd.Timestamp(date_to) + pd.Timedelta(days=1)
        result = result[result["registered_at"] < end]

    if verdicts:
        result = result[result["verdict"].isin(verdicts)]

    if criticalities:
        result = result[result["criticality"].isin(criticalities)]

    return result
