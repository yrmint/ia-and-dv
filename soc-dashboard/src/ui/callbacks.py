from src.analytics.charts import (
    incidents_over_time,
    verdict_distribution,
)
from src.analytics.filters import apply_filters
from src.analytics.metrics import calculate_metrics


def refresh_dashboard(state, var_name=None, var_value=None):
    """Update KPI, plots and queue applying filters."""

    filtered = apply_filters(
        state.data,
        state.date_from,
        state.date_to,
        state.selected_verdicts,
        state.selected_criticalities,
    )

    metrics = calculate_metrics(filtered)

    state.metric_total = int(metrics["total"])
    state.metric_open = int(metrics["open"])
    state.metric_critical = int(metrics["critical"])

    state.time_chart = incidents_over_time(filtered)
    state.verdict_chart = verdict_distribution(filtered)

    state.queue = filtered.reset_index(drop=True)

    if state.selected_incident_id is not None:
        ids = state.queue["EntityId"].tolist()

        if state.selected_incident_id not in ids:
            close_details(state)


def reset_filters(state):
    """Reset all filters."""

    state.date_from = None
    state.date_to = None
    state.selected_verdicts = []
    state.selected_criticalities = []

    refresh_dashboard(state)


def on_queue_action(state, var_name, payload):
    """Open the details of the selected incident."""

    index = payload.get("index")

    if index is None or index >= len(state.queue):
        return

    incident = state.queue.iloc[index]

    state.selected_incident_id = incident["EntityId"]

    state.details_text = (
        f"ID: {incident['EntityId']}\n"
        f"Дата регистрации: {incident['registered_at']}\n"
        f"Вердикт: {incident['verdict']}\n"
        f"Критичность: {incident['criticality']}\n"
        f"Статус: {incident['status']}\n"
        f"Источник: {incident['source']}\n"
        f"Актив: {incident['asset']}\n"
        f"Аналитик: {incident['analyst']}\n\n"
        f"Описание:\n{incident['description']}"
    )

    state.details_open = True


def close_details(state):
    """Close the details panel."""

    state.details_open = False
    state.selected_incident_id = None
    state.details_text = ""
