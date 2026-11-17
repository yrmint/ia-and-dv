import pandas as pd


def apply_filters(
        df: pd.DataFrame,
        date_from,
        date_to,
        verdicts: list[str] | None = None,
        criticalities: list[str] | None = None,
) -> pd.DataFrame:
    result = df.copy()

    # convert timestamps to UTC then remove timezone information
    registered_at = (
        pd.to_datetime(
            result["registered_at"],
            errors="coerce",
            utc=True,
        )
        .dt.tz_localize(None)
    )

    if date_from:
        start = pd.Timestamp(date_from)
        result = result[registered_at >= start]
        registered_at = registered_at.loc[result.index]

    if date_to:
        end = pd.Timestamp(date_to) + pd.Timedelta(days=1)
        result = result[registered_at < end]

    if verdicts:
        result = result[result["verdict"].isin(verdicts)]

    if criticalities:
        result = result[result["criticality"].isin(criticalities)]

    return result
