import pandas as pd


def apply_filters(
        df,
        date_from=None,
        date_to=None,
        criticalities=None,
        sources=None,
):
    result = df.copy()

    if "timestamp" in result.columns:
        result["_dashboard_date"] = pd.to_datetime(
            result["timestamp"],
            errors="coerce",
            utc=True,
        )

        if date_from is not None and date_from != "":
            start = pd.Timestamp(date_from)

            start = start.tz_localize("UTC") if start.tzinfo is None else start.tz_convert("UTC")

            result = result[
                result["_dashboard_date"] >= start
                ]

        if date_to is not None and date_to != "":
            end = pd.Timestamp(date_to)

            end = end.tz_localize("UTC") if end.tzinfo is None else end.tz_convert("UTC")

            end = end + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)

            result = result[
                result["_dashboard_date"] <= end
                ]

    if criticalities is not None and len(criticalities) > 0:
        if isinstance(criticalities, str):
            criticalities = [criticalities]

        if "Критичность" in result.columns:
            result = result[
                result["Критичность"].astype(str).isin(criticalities)
            ]

    if sources is not None and len(sources) > 0:
        if isinstance(sources, str):
            sources = [sources]

        if "Источник инцидента" in result.columns:
            result = result[
                result["Источник инцидента"].astype(str).isin(sources)
            ]

    return result.drop(
        columns=["_dashboard_date"],
        errors="ignore",
    )
