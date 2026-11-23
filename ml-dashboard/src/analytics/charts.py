import plotly.graph_objects as go

from src.analytics.metrics import calculate_metrics

PLOT_TEMPLATE = "plotly_white"
COLORS = {"navy": "#2457A7", "red": "#C2413B", "green": "#25855A",
          "amber": "#D18B24", "muted": "#64748B"}


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

    return {
        "confusion": confusion,
    }
