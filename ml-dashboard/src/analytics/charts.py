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


def calculate_irp_fnr(evaluated):
    """Calculate category FNR and pointwise 95% Wilson score intervals."""
    category_col = "Пиктограмма IRP"
    required = {category_col, "_y", "_pred"}

    if evaluated.empty or not required.issubset(evaluated.columns):
        return pd.DataFrame()

    actual = evaluated.loc[
        (evaluated["_y"] == 1) & evaluated["_pred"].isin([0, 1]),
        [category_col, "_pred"],
    ].copy()

    if actual.empty:
        return pd.DataFrame()

    actual["category"] = (
        actual[category_col]
        .astype("string")
        .fillna("Не указано")
        .str.strip()
        .replace("", "Не указано")
    )
    actual["missed"] = (actual["_pred"] == 0).astype(int)

    summary = (
        actual.groupby("category", as_index=False)
        .agg(n=("missed", "size"), fn=("missed", "sum"))
    )
    summary["fnr"] = summary["fn"] / summary["n"]

    # Wilson score interval for a binomial proportion (95%, two-sided).
    z = 1.959963984540054
    n = summary["n"].to_numpy(dtype=float)
    p = summary["fnr"].to_numpy(dtype=float)
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    half_width = (
        z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
        / denominator
    )
    summary["ci_low"] = np.clip(center - half_width, 0, 1)
    summary["ci_high"] = np.clip(center + half_width, 0, 1)
    # Exact endpoints for categories with no misses or all misses.
    summary.loc[summary["fn"] == 0, "ci_low"] = 0.0
    summary.loc[summary["fn"] == summary["n"], "ci_high"] = 1.0

    return summary.sort_values(
        ["fnr", "n", "category"], ascending=[False, False, True]
    ).reset_index(drop=True)


def missed_incidents_by_irp(evaluated, min_actual=20):
    """Compare IRP category FNR against the overall model FNR."""
    title = "Доля пропущенных инцидентов по категориям IRP"
    summary = calculate_irp_fnr(evaluated)

    if summary.empty:
        return _empty(title, "Нет данных о реальных инцидентах")

    # Include every category in the baseline, even small categories.
    overall_fnr = float(summary["fn"].sum() / summary["n"].sum())
    shown = summary.loc[summary["n"] >= min_actual].copy()

    if shown.empty:
        return _empty(
            title,
            f"Нет категорий с N ≥ {min_actual}<br>"
            f"Общая доля пропусков: {overall_fnr:.2%}",
        )

    customdata = shown[["fn", "n", "ci_low", "ci_high"]].to_numpy(dtype=float)
    fig = go.Figure(go.Scatter(
        x=shown["fnr"],
        y=shown["category"],
        mode="markers",
        marker={"color": COLORS["red"], "size": 10},
        error_x={
            "type": "data",
            "symmetric": False,
            "array": (shown["ci_high"] - shown["fnr"]).clip(lower=0),
            "arrayminus": (shown["fnr"] - shown["ci_low"]).clip(lower=0),
            "color": COLORS["muted"],
            "thickness": 1.5,
            "width": 5,
            "visible": True,
        },
        customdata=customdata,
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>Пропущено (FN): %{customdata[0]:.0f}"
            "<br>Реальных инцидентов (N): %{customdata[1]:.0f}"
            "<br>Доля пропусков (FNR): %{x:.2%}"
            "<br>95% ДИ (Уилсон): %{customdata[2]:.2%} – %{customdata[3]:.2%}"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    fig.add_vline(
        x=overall_fnr,
        line_dash="dash",
        line_color=COLORS["muted"],
        line_width=1.5,
    )
    fig.add_annotation(
        x=overall_fnr,
        y=1.06,
        xref="x",
        yref="paper",
        text=f"Общая доля пропусков: {overall_fnr:.2%}",
        xanchor="left" if overall_fnr <= 0.5 else "right",
        showarrow=False,
        font={"color": COLORS["muted"], "size": 12},
    )

    # Keep FN / N readable in a separate column, outside the percent axis.
    fig.add_annotation(
        x=1.025, y=1.06, xref="paper", yref="paper",
        text="<b>FN / N</b>", xanchor="left", showarrow=False,
    )
    for row in shown.itertuples(index=False):
        fig.add_annotation(
            x=1.025,
            y=row.category,
            xref="paper",
            yref="y",
            text=f"{row.fn} / {row.n}",
            xanchor="left",
            showarrow=False,
        )

    fig = _style(fig, title, height=max(380, 190 + 39 * len(shown)))
    fig.update_xaxes(
        title="Доля пропусков (FNR)",
        range=[0, 1],
        tickformat=".0%",
        tickvals=np.linspace(0, 1, 6),
    )
    fig.update_yaxes(
        title="Категория IRP",
        type="category",
        categoryorder="array",
        categoryarray=shown["category"].tolist(),
        autorange="reversed",
        automargin=True,
    )
    fig.update_layout(
        margin={"l": 25, "r": 110, "t": 90, "b": 75},
        showlegend=False,
    )
    fig.add_annotation(
        x=0, y=-0.24, xref="paper", yref="paper",
        text=f"95% ДИ (Уилсон); N ≥ {min_actual}. "
             f"Показано категорий: {len(shown)} из {len(summary)}.",
        xanchor="left", showarrow=False,
        font={"size": 11, "color": COLORS["muted"]},
    )
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
        "missed_incidents": missed_incidents_by_irp(ev),
    }
