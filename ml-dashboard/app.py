from datetime import datetime

from config import APP_TITLE
from src.analytics.metrics import calculate_metrics
from src.data.loader import load_data
from src.ui.pages import main_page
from taipy.gui import Gui

predictions, incidents = load_data()

current_date = datetime.now().strftime("%d.%m.%Y")
date_from = None
date_to = None
selected_criticalities = []
selected_sources = []
criticality_options = (
    sorted(predictions["Критичность"].dropna().astype(str).unique().tolist())
    if "Критичность" in predictions.columns else []
)
source_options = (
    sorted(predictions["Источник инцидента"].dropna().astype(str).unique().tolist())
    if "Источник инцидента" in predictions.columns else []
)

filters_open = False
prediction_threshold = 0.18

all_metrics = calculate_metrics(
    predictions,
    threshold=prediction_threshold,
)
metric_total = all_metrics["total"]
metric_labeled = all_metrics["labeled"]
metric_fn = all_metrics["fn"]
metric_fp = all_metrics["fp"]

gui = Gui(page=main_page, css_file="src/ui/styles.css")
gui.run(title=APP_TITLE, use_reloader=False)
