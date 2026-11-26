import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.analytics.metrics import calculate_metrics

PLOT_TEMPLATE = "plotly_white"
COLORS = {"default": "#959595", "red": "#D64C4C", "orange": "#d6964c", "muted": "#64748B"}


def _empty(title, message="Недостаточно данных для построения графика"):
    fig = go.Figure()
    fig.add_annotation(text=message, x=.5, y=.5, xref="paper", yref="paper",
                       showarrow=False, font={"color": COLORS["muted"], "size": 13})
    fig.update_layout(title=title, template=PLOT_TEMPLATE, height=330,
                      margin={"l": 25, "r": 20, "t": 55, "b": 25})
    return fig


def _style(fig, title, height=330):
    fig.update_layout(title=title, template=PLOT_TEMPLATE, height=height,
                      margin={"l": 25, "r": 20, "t": 55, "b": 35},
                      legend_title_text="")
    return fig


def missed_incidents_by_type(evaluated, top_n=10):
    """Show missed and detected real incidents grouped by incident type."""
    title = f"Топ-{top_n} типов инцидентов по числу пропусков"
    incident_col = "Значение Инцидента (группировка по типу)"

    required = {incident_col, "_y", "_pred"}

    if evaluated.empty or not required.issubset(evaluated.columns):
        return _empty(title)

    actual = evaluated.loc[
        evaluated["_y"] == 1, [incident_col, "_pred"]
    ].copy()

    if actual.empty:
        return _empty(title, "Нет реальных инцидентов")

    actual["_type"] = (
        actual[incident_col]
        .astype("string")
        .fillna("Не указан")
        .str.strip()
        .replace("", "Не указан")
    )

    summary = (
        actual.groupby("_type")["_pred"]
        .agg(total="size", tp="sum")
        .reset_index()
    )

    summary["fn"] = summary["total"] - summary["tp"]
    summary["fnr"] = summary["fn"] / summary["total"]

    summary = (
        summary[summary["fn"] > 0]
        .sort_values(
            ["fn", "total", "_type"],
            ascending=[False, False, True],
        )
        .head(top_n)
        .iloc[::-1]
    )

    if summary.empty:
        return _empty(title, "Нет пропущенных инцидентов")

    customdata = summary[
        ["total", "fn", "tp", "fnr"]
    ].to_numpy(dtype=float)

    hover = (
        "<b>%{y}</b>"
        "<br>Реальных инцидентов: %{customdata[0]:.0f}"
        "<br>Пропущено (FN): %{customdata[1]:.0f}"
        "<br>Обнаружено (TP): %{customdata[2]:.0f}"
        "<br>Доля пропусков: %{customdata[3]:.2%}"
        "<extra></extra>"
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=summary["_type"],
        x=summary["fn"],
        name="Пропущено (FN)",
        orientation="h",
        marker_color=COLORS["red"],
        customdata=customdata,
        hovertemplate=hover,
    ))

    fig.add_trace(go.Bar(
        y=summary["_type"],
        x=summary["tp"],
        name="Обнаружено (TP)",
        orientation="h",
        marker_color=COLORS["default"],
        customdata=customdata,
        hovertemplate=hover,
    ))

    fig.update_layout(barmode="stack")

    fig.update_xaxes(
        title="Количество реальных инцидентов",
        rangemode="tozero",
    )

    fig.update_yaxes(
        automargin=True,
        categoryorder="array",
        categoryarray=summary["_type"].tolist(),
    )

    return _style(fig, title, height=500)


def build_charts(df, threshold):
    m = calculate_metrics(df, threshold)
    ev = m["evaluated"]

    if len(ev):
        matrix = [[m["tn"], m["fp"]], [m["fn"], m["tp"]]]
        confusion = go.Figure(data=go.Heatmap(
            z=matrix, x=["Прогноз: не инцидент", "Прогноз: инцидент"],
            y=["Факт: не инцидент", "Факт: инцидент"],
            text=matrix, texttemplate="%{text}", colorscale="Blues",
            showscale=False,
        ))
        confusion = _style(confusion, "Совпадение прогноза с фактической меткой")
    else:
        confusion = _empty("Совпадение прогноза с фактической меткой")

    prob = pd.to_numeric(df["y_pred_proba"], errors="coerce").dropna()
    prob = prob[prob.between(0, 1)]

    if not prob.empty:
        threshold = 0.18

        edges = np.sort(np.unique(
            np.r_[np.linspace(0, 1, 21), threshold]
        ))

        counts, edges = np.histogram(prob, bins=edges)

        centers = (edges[:-1] + edges[1:]) / 2
        widths = np.diff(edges)

        colors = [COLORS["default"] for _ in centers]

        risk = go.Figure(
            go.Bar(
                x=centers,
                y=counts,
                width=widths,
                marker={
                    "color": colors,
                },
                customdata=np.column_stack((edges[:-1], edges[1:])),
                hovertemplate=(
                    "Интервал: %{customdata[0]:.0%}–%{customdata[1]:.0%}"
                    "<br>Количество: %{y}"
                    "<extra></extra>"
                ),
            )
        )

        risk.update_xaxes(
            range=[0, 1],
            tickvals=np.linspace(0, 1, 11),
            tickformat=".0%",
            title="Вероятность инцидента",
        )
        risk.update_yaxes(
            title="Количество событий",
            rangemode="tozero",
        )

        risk = _style(risk, "Распределение оценок вероятности инцидента")
    else:
        risk = _empty("Распределение оценок вероятности инцидента")

    return {
        "confusion": confusion,
        "risk": risk,
        "missed_incidents": missed_incidents_by_type(ev),
}
