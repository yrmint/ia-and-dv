
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.analytics.charts import _empty, _style
from src.analytics.metrics import prepare_evaluation_data


def _safe_divide(numerator, denominator):
    """Return NaN when a metric is undefined."""
    return np.divide(
        numerator,
        denominator,
        out=np.full(len(numerator), np.nan, dtype=float),
        where=denominator != 0,
    )


def calculate_threshold_metrics(df, current_threshold=0.18):
    """Evaluate classification quality across decision thresholds."""
    if df.empty or "y_pred_proba" not in df.columns:
        return pd.DataFrame()

    evaluated = prepare_evaluation_data(df, threshold=0.0)

    if evaluated.empty:
        return pd.DataFrame()

    probabilities = pd.to_numeric(
        evaluated["y_pred_proba"], errors="coerce"
    )

    valid = probabilities.between(0, 1)
    probabilities = probabilities[valid].to_numpy(dtype=float)
    labels = evaluated.loc[valid, "_y"].to_numpy(dtype=int)

    if not len(probabilities):
        return pd.DataFrame()

    thresholds = np.unique(
        np.r_[np.arange(101) / 100, current_threshold]
    )

    positive_scores = np.sort(probabilities[labels == 1])
    negative_scores = np.sort(probabilities[labels == 0])

    fn = np.searchsorted(
        positive_scores, thresholds, side="left"
    )
    tn = np.searchsorted(
        negative_scores, thresholds, side="left"
    )

    tp = len(positive_scores) - fn
    fp = len(negative_scores) - tn

    precision = _safe_divide(tp, tp + fp)
    recall = _safe_divide(tp, tp + fn)
    f1 = _safe_divide(2 * tp, 2 * tp + fp + fn)

    return pd.DataFrame({
        "threshold": thresholds,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    })


def _threshold_style(fig, title, threshold):
    fig = _style(fig, title, height=400)

    fig.add_vline(
        x=threshold,
        line_dash="dash",
        line_color="#64748B",
        annotation_text=f"Текущий порог: {threshold:.0%}",
        annotation_position=(
            "top right" if threshold <= 0.5 else "top left"
        ),
    )

    fig.update_xaxes(
        title="Порог вероятности инцидента",
        range=[0, 1],
        tickformat=".0%",
        hoverformat=".0%",
    )

    fig.update_layout(
        hovermode="x unified",
        legend={
            "orientation": "h",
            "y": -0.25,
            "x": 0,
        },
        margin={"l": 55, "r": 25, "t": 70, "b": 105},
    )

    return fig


def build_threshold_charts(df, threshold=0.18):
    """Build threshold performance and error analysis charts."""
    quality_title = "Метрики качества при разных порогах"
    errors_title = "Ошибки модели при разных порогах"

    results = calculate_threshold_metrics(df, threshold)

    if results.empty:
        return {
            "quality": _empty(quality_title),
            "errors": _empty(errors_title),
        }

    quality = go.Figure()

    quality_series = [
        ("precision", "Точность (Precision)", "#4C9BD6"),
        ("recall", "Полнота (Recall)", "#D6964C"),
        ("f1", "F1-мера", "#959595"),
    ]

    for column, name, color in quality_series:
        quality.add_trace(go.Scatter(
            x=results["threshold"],
            y=results[column],
            name=name,
            mode="lines",
            line={"color": color, "width": 2},
            hovertemplate="%{y:.2%}<extra></extra>",
            connectgaps=False,
        ))

    quality.add_hline(
        y=0.75,
        line_dash="dot",
        line_color="#64748B",
        annotation_text="Пример цели: Recall 75%",
        annotation_position="bottom right",
    )

    quality.update_yaxes(
        title="Значение метрики",
        range=[0, 1.02],
        tickformat=".0%",
    )

    errors = go.Figure()

    error_series = [
        ("fn", "Пропущенные инциденты (FN)", "#D64C4C"),
        ("fp", "Ложные тревоги (FP)", "#D6964C"),
    ]

    for column, name, color in error_series:
        errors.add_trace(go.Scatter(
            x=results["threshold"],
            y=results[column],
            name=name,
            mode="lines",
            line={"color": color, "width": 2},
            hovertemplate="%{y:,.0f}<extra></extra>",
        ))

    errors.update_yaxes(
        title="Количество событий",
        rangemode="tozero",
    )

    return {
        "quality": _threshold_style(
            quality, quality_title, threshold
        ),
        "errors": _threshold_style(
            errors, errors_title, threshold
        ),
    }
