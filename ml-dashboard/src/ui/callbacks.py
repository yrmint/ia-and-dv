
from src.analytics.charts import build_charts
from src.analytics.filters import apply_filters
from src.analytics.metrics import calculate_metrics
from src.analytics.thresholds import build_threshold_charts


def toggle_filters(state):
    state.filters_open = not state.filters_open


def refresh_dashboard(state):
    filtered = apply_filters(
        state.predictions,
        state.date_from,
        state.date_to,
        state.selected_criticalities,
        state.selected_sources,
    )

    m = calculate_metrics(
        filtered,
        threshold=state.prediction_threshold,
    )

    state.metric_total = m["total"]
    state.metric_labeled = m["labeled"]
    state.metric_fn = m["fn"]
    state.metric_fp = m["fp"]

    charts = build_charts(
        filtered,
        threshold=state.prediction_threshold,
    )

    threshold_charts = build_threshold_charts(
        filtered,
        threshold=state.prediction_threshold,
    )

    state.threshold_quality_chart = threshold_charts["quality"]
    state.threshold_errors_chart = threshold_charts["errors"]

    state.confusion_chart = charts["confusion"]
    state.missed_incidents_chart = charts["missed_incidents"]

    state.filters_open = False


def reset_filters(state):
    state.date_from = None
    state.date_to = None
    state.selected_criticalities = []
    state.selected_sources = []
    state.prediction_threshold = 0.18
    refresh_dashboard(state)

    state.filters_open = False
