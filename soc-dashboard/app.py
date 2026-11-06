from config import APP_TITLE
from src.analytics.charts import (
    incidents_over_time,
    verdict_distribution,
)
from src.analytics.metrics import calculate_metrics
from src.mock_data import load_mock_data

# import callbacks for taipy to find from the Markdown field
# # noqa: F401 makes ruff ignore the unused imports
from src.ui.callbacks import (
    close_details,  # noqa: F401
    on_queue_action,  # noqa: F401
    refresh_dashboard,  # noqa: F401
    reset_filters,  # noqa: F401
)
from src.ui.pages import main_page
from taipy.gui import Gui

# data
data = load_mock_data()
queue = data.copy()


# interface initial state

date_from = None
date_to = None

verdict_options = [
    "Подтвержденный инцидент",
    "Ложное срабатывание",
    "Не определен",
]

criticality_options = [
    "Критическая",
    "Высокая",
    "Средняя",
    "Низкая",
]

selected_verdicts = []
selected_criticalities = []

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
verdict_chart = verdict_distribution(data)


if __name__ == "__main__":
    gui = Gui(page=main_page)
    gui.run(title=APP_TITLE, port=5000)
