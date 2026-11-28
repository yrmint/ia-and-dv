
import pandas as pd

from src.analytics.charts import (
    analyst_workload,
    critical_incident_types,
    incidents_over_time,
    noisy_incident_types,
    sla_violations_over_time,
    verdict_distribution,
)
from src.analytics.filters import apply_filters
from src.analytics.metrics import calculate_metrics


def _format_value(value):
    """Format a dataset value for display in the incident card."""

    if value is None:
        return "Не указано"

    if isinstance(value, (list, tuple)):
        return "\n".join(str(item) for item in value)

    try:
        if pd.isna(value):
            return "Не указано"
    except (TypeError, ValueError):
        pass

    if isinstance(value, pd.Timestamp):
        return value.strftime("%d.%m.%Y %H:%M:%S")

    if isinstance(value, str):
        value = value.replace("~~||~~", "\n")
        return value.strip() or "Не указано"

    return str(value)


def _build_incident_details(incident):
    """Build a readable description using original dataset columns."""

    sections = {
        "ОБЩАЯ ИНФОРМАЦИЯ": [
            ("ID", "ID"),
            ("Создан", "Дата создания"),
            ("Дата закрытия (факт)", "Дата закрытия"),
            ("Тип инцидента", "Тип инцидента"),
            ("Типы угроз", "Типы угроз"),
            ("Критичность", "Критичность"),
            ("Вердикт", "Вердикт"),
            ("Фаза реагирования", "Фаза реагирования"),
            ("Источник инцидента", "Источник"),
            ("Количество инцидентов", "Количество событий"),
        ],
        "ОТВЕТСТВЕННЫЕ И SLA": [
            ("Ответственный", "Ответственный аналитик"),
            ("Прошлый ответственный", "Предыдущий аналитик"),
            ("Группа устранения", "Группа устранения"),
            ("Дата взятия в работу", "Дата взятия в работу"),
            ("work_period", "Период до взятия в работу"),
        ],
        "ТЕХНИЧЕСКИЙ КОНТЕКСТ": [
            ("Полное имя", "Пользователь"),
            ("suser", "Учетная запись источника"),
            ("duser", "Учетная запись цели"),
            ("Hostname Цели", "Хост цели"),
            ("Hostname атакующего", "Хост атакующего"),
        ],
        "ОПИСАНИЕ И РЕЗУЛЬТАТ": [
            ("Описание инцидента", "Описание инцидента"),
            ("Решение", "Решение аналитика"),
            ("Комментарий", "Комментарии"),
            ("Принятые меры", "Принятые меры"),
            ("Рекомендации по плейбуку", "Рекомендации по плейбуку"),
        ],
    }

    result = []

    for section, fields in sections.items():
        lines = []

        for column, label in fields:
            if column in incident.index:
                value = _format_value(incident[column])
                if value != "Не указано":
                    lines.append(f"{label}:\n{value}")

        if lines:
            result.append(section)
            result.extend(lines)

    return "\n\n".join(result)


def on_period_change(state, var_name, value):
    days = 7 if value == "7 дней" else 30

    filtered = apply_filters(
        state.data,
        state.date_from,
        state.date_to,
        state.selected_verdicts,
        state.selected_criticalities,
    )

    state.time_chart = incidents_over_time(filtered, days=days)
    state.sla_chart = sla_violations_over_time(filtered, days=days)


def toggle_filters(state):
    state.filters_open = not state.filters_open


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

    days = 7 if state.selected_period == "7 дней" else 30
    state.time_chart = incidents_over_time(filtered, days=days)
    state.sla_chart = sla_violations_over_time(filtered, days=days)
    state.verdict_chart = verdict_distribution(filtered)
    state.noise_chart = noisy_incident_types(filtered)
    state.criticality_chart = critical_incident_types(filtered)
    state.analyst_chart = analyst_workload(filtered)

    state.queue = filtered.reset_index(drop=True)

    if state.selected_incident_id is not None:
        ids = state.queue["ID"].tolist()

        if state.selected_incident_id not in ids:
            close_details(state)

    state.filters_open = False


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

    if index is None:
        return

    try:
        index = int(index)
    except (TypeError, ValueError):
        return

    if not 0 <= index < len(state.queue):
        return

    incident = state.queue.iloc[index]

    state.selected_incident_id = incident["ID"]
    state.details_text = _build_incident_details(incident)
    state.details_open = True


def close_details(state):
    """Close the incident details dialog."""

    state.details_open = False
    state.selected_incident_id = None
    state.details_text = ""
