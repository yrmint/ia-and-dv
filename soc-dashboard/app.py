from config import APP_TITLE
from src.analytics.charts import (
    critical_incident_types,
    incidents_over_time,
    noisy_incident_types,
    sla_violations_over_time,
    verdict_distribution,
)
from src.analytics.metrics import calculate_metrics
from src.data.loader import load_data
from src.ui.pages import main_page
from src.ui.themes import DARK_THEME, LIGHT_THEME
from taipy.gui import Gui

import pandas as pd

# data
data = load_data()
queue = data.copy()


# interface initial state

date_from = None
date_to = None

verdict_options = [
    "Не указан",
    "False Positive",
    "Дубликат",
    "Решён",
    "Не решён",
    "Закрыт по совокупности инцидентов",
    "Закрыт из родительской атаки"
]

criticality_options = [
    "Критическая",
    "Высокая",
    "Средняя",
    "Низкая",
    "Отсутствует"
]

current_date = data["Дата закрытия (факт)"].max().strftime("%d.%m.%Y %H:%M:%S")

selected_verdicts = []
selected_criticalities = []
selected_period = "7 дней"

selected_incident_id = None
details_open = False
details_text = ""

# KPI
metrics = calculate_metrics(data)

metric_total = int(metrics["total"])
metric_open = int(metrics["open"])
metric_critical = int(metrics["critical"])

# plots
time_chart = incidents_over_time(data)
sla_chart = sla_violations_over_time(data)
verdict_chart = verdict_distribution(data)
noise_chart = noisy_incident_types(data)
criticality_chart = critical_incident_types(data)


if __name__ == "__main__":
    gui = Gui(
        page=main_page,
        css_file="src/ui/styles.css",
    )
    gui.run(
        title=APP_TITLE,
        port=5000,
        dark_mode=True,
        light_theme=LIGHT_THEME,
        dark_theme=DARK_THEME,
    )
