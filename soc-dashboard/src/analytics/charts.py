import pandas as pd
import plotly.express as px


def incidents_over_time(df: pd.DataFrame):
    if df.empty:
        return px.line(title="Нет данных")

    grouped = (
        df.assign(date=df["registered_at"].dt.floor("h"))
        .groupby("date")
        .size()
        .reset_index(name="incidents")
    )

    fig = px.line(
        grouped,
        x="date",
        y="incidents",
        markers=True,
        title="Количество инцидентов во времени",
        labels={
            "date": "Время",
            "incidents": "Количество",
        },
    )

    return fig


def verdict_distribution(df: pd.DataFrame):
    if df.empty:
        return px.bar(title="Нет данных")

    grouped = (
        df.groupby("verdict")
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        grouped,
        x="verdict",
        y="count",
        title="Распределение по вердиктам",
        labels={
            "verdict": "Вердикт",
            "count": "Количество",
        },
    )

    return fig
