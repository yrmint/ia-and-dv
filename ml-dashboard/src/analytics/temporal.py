import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.analytics.charts import _empty, _style
from src.analytics.metrics import prepare_evaluation_data


def calculate_weekly_metrics(df, threshold=0.18):
    """Calculate weekly model performance using valid labels."""
    if df.empty or "timestamp" not in df.columns:
        return pd.DataFrame()

    timestamps = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        utc=True,
    )

    weeks = (
        timestamps.dt.tz_localize(None)
        .dt.to_period("W-SUN")
        .dt.start_time
    )

    if weeks.dropna().empty:
        return pd.DataFrame()

    week_index = pd.date_range(
        start=weeks.min(),
        end=weeks.max(),
        freq="W-MON",
        name="week",
    )

    summary = pd.DataFrame(index=week_index)

    summary["total"] = (
        weeks.value_counts()
        .reindex(week_index, fill_value=0)
    )

    evaluated = prepare_evaluation_data(
        df,
        threshold=threshold,
    ).copy()

    count_columns = ["labeled", "tp", "tn", "fp", "fn"]

    if evaluated.empty:
        for column in count_columns:
            summary[column] = 0
    else:
        evaluated["week"] = (
            pd.to_datetime(
                evaluated["timestamp"],
                errors="coerce",
                utc=True,
            )
            .dt.tz_localize(None)
            .dt.to_period("W-SUN")
            .dt.start_time
        )

        y = evaluated["_y"]
        pred = evaluated["_pred"]

        evaluated["tp"] = ((y == 1) & (pred == 1)).astype(int)
        evaluated["tn"] = ((y == 0) & (pred == 0)).astype(int)
        evaluated["fp"] = ((y == 0) & (pred == 1)).astype(int)
        evaluated["fn"] = ((y == 1) & (pred == 0)).astype(int)

        grouped = evaluated.groupby("week").agg(
            labeled=("_y", "size"),
            tp=("tp", "sum"),
            tn=("tn", "sum"),
            fp=("fp", "sum"),
            fn=("fn", "sum"),
        )

        summary = summary.join(grouped)

        summary[count_columns] = (
            summary[count_columns]
            .fillna(0)
            .astype(int)
        )

    summary["actual_positive"] = (
        summary["tp"] + summary["fn"]
    )

    summary["predicted_positive"] = (
        summary["tp"] + summary["fp"]
    )

    summary["precision"] = (
        summary["tp"]
        / summary["predicted_positive"].replace(0, np.nan)
    )

    summary["recall"] = (
        summary["tp"]
        / summary["actual_positive"].replace(0, np.nan)
    )

    summary["f1"] = (
        2 * summary["tp"]
        / (
            2 * summary["tp"]
            + summary["fp"]
            + summary["fn"]
        ).replace(0, np.nan)
    )

    summary["fnr"] = (
        summary["fn"]
        / summary["actual_positive"].replace(0, np.nan)
    )

    summary["label_coverage"] = (
        summary["labeled"]
        / summary["total"].replace(0, np.nan)
    )

    return summary.reset_index()


def _weekly_style(fig, title, results, threshold):
    """Apply consistent styling to weekly charts."""

    fig = _style(fig, title, height=400)

    fig.update_xaxes(
        title="Неделя (понедельник – воскресенье, UTC)",
        tickmode="array",
        tickvals=results["week"],
        tickformat="%d.%m",
        tickangle=-45,
        range=[
            results["week"].min() - pd.Timedelta(days=4),
            results["week"].max() + pd.Timedelta(days=4),
        ],
    )

    fig.update_layout(
        title_text=f"{title} (порог: {threshold:.0%})",
        hovermode="closest",
        legend={
            "orientation": "h",
            "y": -0.4,
            "x": 0,
        },
        margin={
            "l": 55,
            "r": 25,
            "t": 75,
            "b": 140,
        },
    )

    return fig


def _weekly_hover_data(results):
    """Prepare additional information for chart tooltips."""

    start = results["week"].dt.strftime("%d.%m.%Y")

    end = (
        results["week"] + pd.Timedelta(days=6)
    ).dt.strftime("%d.%m.%Y")

    coverage = results["label_coverage"].map(
        lambda value: (
            f"{value:.1%}"
            if pd.notna(value)
            else "Нет данных"
        )
    )

    return pd.DataFrame({
        "period": start + " – " + end,
        "total": results["total"],
        "labeled": results["labeled"],
        "coverage": coverage,
        "actual_positive": results["actual_positive"],
        "predicted_positive": results["predicted_positive"],
    }).to_numpy()


def _add_unavailable_marker(
    fig,
    results,
    mask,
    custom_data,
    name,
):
    """Mark weeks with unavailable values."""

    if not mask.any():
        return

    fig.add_trace(go.Scatter(
        x=results.loc[mask, "week"],
        y=np.zeros(int(mask.sum())),
        mode="markers",
        name=name,
        marker={
            "symbol": "x",
            "size": 10,
            "color": "#64748B",
        },
        customdata=custom_data[mask.to_numpy()],
        hovertemplate=(
            "%{customdata[0]}<br>"
            + name
            + "<br>"
            "Всего прогнозов: %{customdata[1]}<br>"
            "Оценено: %{customdata[2]}<br>"
            "Покрытие оценки: %{customdata[3]}"
            "<extra></extra>"
        ),
    ))


def build_temporal_charts(df, threshold=0.18):
    """Build weekly quality and error analysis charts."""

    quality_title = "Динамика метрик качества модели"
    errors_title = "Динамика ошибок модели"

    results = calculate_weekly_metrics(df, threshold)

    if results.empty:
        return {
            "quality": _empty(quality_title),
            "errors": _empty(errors_title),
        }

    custom_data = _weekly_hover_data(results)

    hover_context = (
        "<br>Всего прогнозов: %{customdata[1]}"
        "<br>Оценено: %{customdata[2]}"
        "<br>Покрытие оценки: %{customdata[3]}"
        "<br>Реальных инцидентов: %{customdata[4]}"
        "<br>Предсказано инцидентов: %{customdata[5]}"
        "<extra></extra>"
    )

    # Chart 1: Model quality over time

    quality = go.Figure()

    quality_series = [
        ("precision", "Точность (Precision)", "#4C9BD6"),
        ("recall", "Полнота (Recall)", "#D6964C"),
        ("f1", "F1-мера", "#959595"),
    ]

    for column, name, color in quality_series:
        quality.add_trace(go.Scatter(
            x=results["week"],
            y=results[column],
            mode="lines+markers",
            name=name,
            line={
                "color": color,
                "width": 2,
            },
            marker={"size": 6},
            connectgaps=False,
            customdata=custom_data,
            hovertemplate=(
                "%{customdata[0]}<br>"
                + name
                + ": %{y:.2%}"
                + hover_context
            ),
        ))

    _add_unavailable_marker(
        quality,
        results,
        results[
            ["precision", "recall", "f1"]
        ].isna().all(axis=1),
        custom_data,
        "Метрики не определены",
    )

    quality.update_yaxes(
        title="Значение метрики",
        range=[-0.03, 1.03],
        tickformat=".0%",
        tick0=0,
        dtick=0.2,
    )

    # Chart 2: Model errors over time

    errors = go.Figure()

    error_series = [
        ("fn", "Пропущенные инциденты (FN)", "#D64C4C"),
        ("fp", "Ложные тревоги (FP)", "#D6964C"),
    ]

    for column, name, color in error_series:
        errors.add_trace(go.Bar(
            x=results["week"],
            y=results[column].where(
                results["labeled"].gt(0)
            ),
            name=name,
            marker_color=color,
            customdata=custom_data,
            hovertemplate=(
                "%{customdata[0]}<br>"
                + name
                + ": %{y:,.0f}"
                + hover_context
            ),
        ))

    _add_unavailable_marker(
        errors,
        results,
        results["labeled"].eq(0),
        custom_data,
        "Нет данных для оценки",
    )

    errors.update_layout(
        barmode="group",
    )

    errors.update_yaxes(
        title="Количество прогнозов",
        rangemode="tozero",
    )

    return {
        "quality": _weekly_style(
            quality,
            quality_title,
            results,
            threshold,
        ),
        "errors": _weekly_style(
            errors,
            errors_title,
            results,
            threshold,
        ),
    }
