from datetime import datetime

from config import APP_TITLE
from src.analytics.metrics import calculate_metrics
from src.data.loader import load_data
from src.ui.pages import main_page
from taipy.gui import Gui

predictions, incidents = load_data()

current_date = datetime.now().strftime("%d.%m.%Y")

filters_open = False
date_from = None
date_to = None

all_metrics = calculate_metrics(predictions)
metric_total = all_metrics["total"]
metric_labeled = all_metrics["labeled"]
metric_fn = all_metrics["fn"]
metric_fp = all_metrics["fp"]

gui = Gui(page=main_page, css_file="src/ui/styles.css")
gui.run(title=APP_TITLE, use_reloader=False)
