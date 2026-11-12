import pandas as pd
import plotly.express as px


def incidents_over_time(df: pd.DataFrame):
    if df.empty:
        return px.line(title="Нет данных")

    data = df.copy()
    data["registered_at"] = pd.to_datetime(
        data["registered_at"],
        errors="coerce",
    )
    data = data.dropna(subset=["registered_at"])

    if data.empty:
        return px.line(title="Нет данных")

    period = data["registered_at"].max() - data["registered_at"].min()

    if period <= pd.Timedelta(days=3):
        freq = "h"
        x_label = "Время"
    elif period <= pd.Timedelta(days=90):
        freq = "D"
        x_label = "Дата"
    else:
        freq = "W"
        x_label = "Неделя"

    grouped = (
        data.assign(date=data["registered_at"].dt.to_period(freq).dt.start_time)
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
            "date": x_label,
            "incidents": "Количество инцидентов",
        },
    )

    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title="Количество инцидентов",
        hovermode="x unified",
    )

    return fig


def verdict_distribution(df: pd.DataFrame):
    if df.empty:
        return px.bar(title="Нет данных")

    grouped = (
        df["verdict"]
        .fillna("Не указано")
        .astype(str)
        .value_counts()
        .rename_axis("verdict")
        .reset_index(name="count")
        .sort_values("count", ascending=True)
    )

    fig = px.bar(
        grouped,
        x="count",
        y="verdict",
        orientation="h",
        title="Распределение по вердиктам",
        labels={
            "verdict": "Вердикт",
            "count": "Количество инцидентов",
        },
    )

    fig.update_layout(
        xaxis_title="Количество инцидентов",
        yaxis_title="Вердикт",
    )

    return fig
