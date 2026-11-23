import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.analytics.metrics import calculate_metrics

PLOT_TEMPLATE = "plotly_white"
COLORS = {"default": "#959595", "red": "D64C4C", "orange": "#d6964c", "muted": "#64748B"}


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
    }
