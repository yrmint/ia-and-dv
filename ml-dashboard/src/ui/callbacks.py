from src.analytics.filters import apply_filters
from src.analytics.metrics import calculate_metrics


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
    m = calculate_metrics(filtered)

    state.metric_total = m['total']
    state.metric_labeled = m['labeled']
    state.metric_fn = m['fn']
    state.metric_fp = m['fp']


def reset_filters(state):
    state.date_from = None
    state.date_to = None
    state.selected_criticalities = []
    state.selected_sources = []
    refresh_dashboard(state)

