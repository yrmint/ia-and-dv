import pandas as pd

from src.analytics.charts import (
    incidents_over_time,
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
            ("EntityId", "ID"),
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
            ("Период взятия в работу", "Период до взятия в работу"),
            ("Время Решения", "Время решения (сек)"),
            ("SLA по устранению", "SLA по устранению"),
            ("SLA по взятию в работу Атаки", "SLA по взятию в работу"),
        ],
        "ТЕХНИЧЕСКИЙ КОНТЕКСТ": [
            ("Полное имя", "Пользователь"),
            ("suser", "Учетная запись источника"),
            ("duser", "Учетная запись цели"),
            ("Hostname Цели", "Хост цели"),
            ("Hostname атакующего", "Хост атакующего"),
            ("Привилегии аккаунта", "Привилегии аккаунта"),
            ("processName", "Процесс"),
            ("processParentName", "Родительский процесс"),
            ("commandName", "Команда / утилита"),
            ("processPath", "Путь процесса"),
            ("processParentPath", "Путь родительского процесса"),
            ("Команда", "Командная строка"),
            ("object", "Тип объекта"),
            ("objectValue", "Объекты воздействия"),
            ("objectLinks", "Связанные объекты"),
            ("Файловый ресурс", "Файловые ресурсы"),
        ],
        "ОПИСАНИЕ И РЕЗУЛЬТАТ": [
            ("Описание инцидента", "Описание инцидента"),
            ("Алерт", "Исходные алерты"),
            ("Теги", "Теги"),
            ("Значение Атаки (группировка)", "Значения родительской атаки"),
            ("Значение Инцидента (группировка)", "Значения инцидента"),
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

    if index is None:
        return

    try:
        index = int(index)
    except (TypeError, ValueError):
        return

    if not 0 <= index < len(state.queue):
        return

    incident = state.queue.iloc[index]

    state.selected_incident_id = incident["EntityId"]
    state.details_text = _build_incident_details(incident)
    state.details_open = True


def close_details(state):
    """Close the incident details dialog."""

    state.details_open = False
    state.selected_incident_id = None
    state.details_text = ""
