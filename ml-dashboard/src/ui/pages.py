import taipy.gui.builder as tgb

from src.ui.callbacks import toggle_filters

with tgb.Page() as main_page, tgb.layout(
        columns="1 auto",
        class_name="dashboard-header"
):
    with tgb.layout(
            columns="auto auto",
            class_name="dashboard-title-group"
    ):
        tgb.text("# Качество ML-инференса SOC", mode="md")
        tgb.text("{current_date}", class_name="current-date")

    with tgb.layout(
            columns="auto auto",
            class_name="title-buttons-group"
    ):
        tgb.button(
            "Фильтры",
            on_action=toggle_filters,
            class_name="relative nolabel"
        )
        tgb.toggle(
            theme=True,
            class_name="relative nolabel theme-toggle"
        )

    # sliding out filters panel
    with tgb.pane(open="{filters_open}"):   # noqa: SIM117
        with tgb.layout(columns="1", class_name="filters-content", gap="16px"):

            tgb.text("## Фильтры", mode="md")

            with tgb.layout(columns="4 1 4", gap="6px"):
                tgb.date("{date_from}", label="От")

                with tgb.layout(
                        columns="1",
                        class_name="dash-container",
                ):
                    tgb.text("—", class_name="dash-text")

                tgb.date("{date_to}", label="До")

            with tgb.layout(gap="6px"):
                tgb.text("Критичность")
                tgb.selector(
                    multiple=True,
                )

            with tgb.layout(gap="6px"):
                tgb.text("Источник инцидента")
                tgb.selector(
                    multiple=True,
                )

            with tgb.layout("1 1", gap="10px"):
                tgb.button("Применить")
                tgb.button("Сбросить")
