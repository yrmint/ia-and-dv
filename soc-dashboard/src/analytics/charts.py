import pandas as pd
import plotly.express as px
from src.ui.plot_styles import get_plot_colors


def incidents_over_time(df: pd.DataFrame, days: int = 7):
    if df.empty:
        return px.bar(title="Нет данных")

    if days not in (7, 30):
        raise ValueError("days must be either 7 or 30")

    data = df.copy()
    data["registered_at"] = pd.to_datetime(
        data["registered_at"],
        errors="coerce",
    )
    data = data.dropna(subset=["registered_at"])

    if data.empty:
        return px.bar(title="Нет данных")

    data["registered_at"] = data["registered_at"].dt.normalize()

    start_date = data["registered_at"].min()
    end_date = data["registered_at"].max()

    data["period_start"] = (
            start_date
            + (
                    (data["registered_at"] - start_date).dt.days // days
            ) * pd.Timedelta(days=days)
    )

    grouped = (
        data.groupby("period_start")
        .size()
        .reset_index(name="incidents")
    )

    period_range = pd.date_range(
        start=start_date,
        end=end_date,
        freq=f"{days}D",
    )

    grouped = (
        grouped.set_index("period_start")
        .reindex(period_range, fill_value=0)
        .rename_axis("period_start")
        .reset_index()
    )

    max_incidents = grouped["incidents"].max()
    colors = get_plot_colors()

    grouped["color"] = colors["default"]
    if max_incidents > 0:
        grouped.loc[
            grouped["incidents"] == max_incidents,
            "color",
        ] = colors["red"]


    fig = px.bar(
        grouped,
        x="period_start",
        y="incidents",
        color="color",
        color_discrete_map={
            colors["default"]: colors["default"],
            colors["red"]: colors["red"],
        },
        title=f"Количество инцидентов за каждые {days} дней",
        labels={
            "period_start": "Начало периода",
            "incidents": "Количество инцидентов",
        },
        hover_data={"color": False},
    )

    fig.update_layout(
        xaxis_title="Период",
        yaxis_title="Количество инцидентов",
        showlegend=False,
        hovermode="x",
    )

    return fig


def sla_violations_over_time(df: pd.DataFrame, days: int = 7):
    sla_col = "SLA просрочен (взятие в работу)"

    if df.empty:
        return px.bar(title="Нет данных")

    if days not in (7, 30):
        raise ValueError("days must be either 7 or 30")

    data = df[["registered_at", sla_col]].copy()

    data["registered_at"] = pd.to_datetime(
        data["registered_at"],
        errors="coerce",
    )

    data["sla_violated"] = data[sla_col].map({
        True: True,
        False: False,
        "True": True,
        "False": False,
    })

    data = data.dropna(subset=["registered_at", "sla_violated"])

    if data.empty:
        return px.bar(title="Нет данных")

    data["registered_at"] = data["registered_at"].dt.normalize()

    start_date = data["registered_at"].min()
    end_date = data["registered_at"].max()

    data["period_start"] = (
            start_date
            + (
                    (data["registered_at"] - start_date).dt.days // days
            ) * pd.Timedelta(days=days)
    )

    grouped = (
        data.groupby("period_start")["sla_violated"]
        .agg(
            violations="sum",
            total="count",
        )
        .reset_index()
    )

    period_range = pd.date_range(
        start=start_date,
        end=end_date,
        freq=f"{days}D",
    )

    grouped = (
        grouped.set_index("period_start")
        .reindex(period_range, fill_value=0)
        .rename_axis("period_start")
        .reset_index()
    )

    grouped["violation_rate"] = (
            grouped["violations"]
            / grouped["total"].replace(0, pd.NA)
            * 100
    ).fillna(0)

    max_rate = grouped["violation_rate"].max()
    colors = get_plot_colors()

    grouped["color"] = colors["default"]

    if max_rate > 0:
        grouped.loc[
            grouped["violation_rate"] == max_rate,
            "color",
        ] = colors["red"]

    fig = px.bar(
        grouped,
        x="period_start",
        y="violation_rate",
        color="color",
        color_discrete_map={
            colors["default"]: colors["default"],
            colors["red"]: colors["red"],
        },
        title=f"Доля нарушений SLA за каждые {days} дней",
        labels={
            "period_start": "Начало периода",
            "violation_rate": "Доля нарушений SLA",
        },
        custom_data=["violations", "total"],
        hover_data={"color": False},
    )

    fig.update_traces(
        hovertemplate=(
            "Начало периода: %{x|%d.%m.%Y}<br>"
            "Доля нарушений: %{y:.1f}%<br>"
            "Нарушений: %{customdata[0]}<br>"
            "Всего инцидентов: %{customdata[1]}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title="Период",
        yaxis_title="Доля нарушений SLA",
        yaxis_ticksuffix="%",
        yaxis_range=[0, 100],
        xaxis={
            "type": "date",
            "tickformat": "%d.%m.%Y",
        },
        showlegend=False,
        hovermode="x",
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

    colors = get_plot_colors()

    fig = px.bar(
        grouped,
        x="count",
        y="verdict",
        orientation="h",
        color_discrete_sequence=[colors["default"]],
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

    colors = get_plot_colors()

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
        color_discrete_map={
            "False Positive": colors["red"],
            "Остальные": colors["default"],
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


def critical_incident_types(df: pd.DataFrame, top_n: int = 10):
    if df.empty:
        return px.bar(title="Нет данных")

    type_col = (
        "incident_type"
        if "incident_type" in df.columns
        else "Тип инцидента"
    )

    criticality_col = (
        "criticality"
        if "criticality" in df.columns
        else "Критичность"
    )

    if type_col not in df.columns or criticality_col not in df.columns:
        return px.bar(title="Нет данных")

    data = df[[type_col, criticality_col]].copy()

    data[type_col] = (
        data[type_col]
        .fillna("Не указано")
        .astype(str)
    )

    data[criticality_col] = (
        data[criticality_col]
        .fillna("Отсутствует")
        .astype(str)
    )

    summary = (
        data.groupby(type_col)
        .agg(
            total=(criticality_col, "size"),
            critical=(
                criticality_col,
                lambda values: (values == "Критическая").sum(),
            ),
            high=(
                criticality_col,
                lambda values: (values == "Высокая").sum(),
            ),
        )
        .reset_index()
    )

    summary["high_risk"] = (
        summary["critical"] + summary["high"]
    )

    summary["other"] = (
        summary["total"] - summary["high_risk"]
    )

    summary["high_risk_rate"] = (
        summary["high_risk"]
        / summary["total"]
        * 100
    ).round(1)

    summary = (
        summary.nlargest(top_n, "high_risk")
        .sort_values("high_risk")
    )

    chart_data = summary.melt(
        id_vars=[
            type_col,
            "total",
            "high_risk",
            "high_risk_rate",
        ],
        value_vars=[
            "critical",
            "high",
            "other",
        ],
        var_name="category",
        value_name="count",
    )

    chart_data["category"] = chart_data["category"].map({
        "critical": "Критическая",
        "high": "Высокая",
        "other": "Остальные",
    })

    colors = get_plot_colors()

    fig = px.bar(
        chart_data,
        x="count",
        y=type_col,
        color="category",
        orientation="h",
        barmode="stack",
        custom_data=[
            "total",
            "high_risk",
            "high_risk_rate",
        ],
        title="Топ-10 типов инцидентов по уровню риска",
        labels={
            type_col: "Тип инцидента",
            "count": "Количество карточек",
            "category": "Критичность",
        },
        color_discrete_map={
            "Критическая": colors["red"],
            "Высокая": colors["orange"],
            "Остальные": colors["default"],
        },
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{fullData.name}: %{x}<br>"
            "Всего карточек: %{customdata[0]}<br>"
            "Критические + высокие: %{customdata[1]}<br>"
            "Доля высокого риска: %{customdata[2]}%"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title="Количество карточек",
        yaxis_title="Тип инцидента",
        legend_title="Критичность",
    )

    return fig
