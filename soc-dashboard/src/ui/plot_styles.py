import re
from functools import lru_cache
from pathlib import Path

CSS_PATH = Path("src/ui/styles.css")


@lru_cache(maxsize=1)
def get_plot_colors():
    css = CSS_PATH.read_text(encoding="utf-8")

    def get_variable(name):
        match = re.search(
            rf"{re.escape(name)}:\s*(#[0-9A-Fa-f]{{6}})",
            css,
        )

        if not match:
            raise ValueError(f"CSS variable {name} not found")

        return match.group(1)

    return {
        "default": get_variable("--plot-color-default"),
        "highlight": get_variable("--plot-color-highlight"),
    }
