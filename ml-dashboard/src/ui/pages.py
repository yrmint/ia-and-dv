import taipy.gui.builder as tgb

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

    tgb.toggle(
        theme=True,
        class_name="relative nolabel theme-toggle"
    )
