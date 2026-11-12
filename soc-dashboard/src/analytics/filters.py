import pandas as pd


def apply_filters(
        df: pd.DataFrame,
        date_from,
        date_to,
        verdicts: list[str] | None = None,
        criticalities: list[str] | None = None,
) -> pd.DataFrame:
    result = df.copy()

    if date_from:
        start = pd.Timestamp(date_from)
        result = result[
            pd.to_datetime(result["registered_at"], errors="coerce") >= start
            ]

    if date_to:
        end = pd.Timestamp(date_to) + pd.Timedelta(days=1)
        result = result[
            pd.to_datetime(result["registered_at"], errors="coerce") < end
            ]

    if verdicts:
        result = result[result["verdict"].isin(verdicts)]

    if criticalities:
        result = result[result["criticality"].isin(criticalities)]

    return result
