from datetime import datetime

from config import APP_TITLE
from src.ui.pages import main_page
from taipy.gui import Gui
from src.data.loader import load_data


predictions, incidents = load_data()
print(predictions.head())
print(incidents.head())

current_date = datetime.now().strftime("%d.%m.%Y")

filters_open = False
date_from = None
date_to = None

gui = Gui(page=main_page, css_file="src/ui/styles.css")
gui.run(title=APP_TITLE, use_reloader=False)
