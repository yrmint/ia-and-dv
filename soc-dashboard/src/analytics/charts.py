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


def noisy_incident_types(df: pd.DataFrame, top_n: int = 10):
    if df.empty:
        return px.bar(title="Нет данных")

    type_col = (
        "incident_type"
        if "incident_type" in df.columns
        else "Тип инцидента"
    )

    verdict_col = (
        "verdict"
        if "verdict" in df.columns
        else "Вердикт"
    )

    if type_col not in df.columns or verdict_col not in df.columns:
        return px.bar(title="Нет данных")

    data = df[[type_col, verdict_col]].copy()

    data[type_col] = (
        data[type_col]
        .fillna("Не указано")
        .astype(str)
    )

    data[verdict_col] = (
        data[verdict_col]
        .fillna("Не указано")
        .astype(str)
    )

    summary = (
        data.groupby(type_col)
        .agg(
            total=(verdict_col, "size"),
            false_positive=(
                verdict_col,
                lambda values: (values == "False Positive").sum(),
            ),
        )
        .reset_index()
    )

    summary["other"] = (
        summary["total"] - summary["false_positive"]
    )

    summary["fp_rate"] = (
        summary["false_positive"]
        / summary["total"]
        * 100
    ).round(1)

    summary = (
        summary.nlargest(top_n, "total")
        .sort_values("total")
    )

    chart_data = summary.melt(
        id_vars=[type_col, "total", "fp_rate"],
        value_vars=["false_positive", "other"],
        var_name="category",
        value_name="count",
    )

    chart_data["category"] = chart_data["category"].map({
        "false_positive": "False Positive",
        "other": "Остальные",
    })

    fig = px.bar(
        chart_data,
        x="count",
        y=type_col,
        color="category",
        orientation="h",
        barmode="stack",
        custom_data=["total", "fp_rate"],
        title="Топ-10 типов инцидентов: поток и False Positive",
        labels={
            type_col: "Тип инцидента",
            "count": "Количество карточек",
            "category": "Вердикт",
        },
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{fullData.name}: %{x}<br>"
            "Всего карточек: %{customdata[0]}<br>"
            "Доля False Positive: %{customdata[1]}%"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title="Количество карточек",
        yaxis_title="Тип инцидента",
        legend_title="Вердикт",
    )

    return fig