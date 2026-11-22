from datetime import datetime

from config import APP_TITLE
from src.ui.pages import main_page
from taipy.gui import Gui

current_date = datetime.now().strftime("%d.%m.%Y")

filters_open = False
date_from = None
date_to = None

gui = Gui(page=main_page, css_file="src/ui/styles.css")
gui.run(title=APP_TITLE, use_reloader=False)
