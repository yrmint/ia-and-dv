import taipy.gui.builder as tgb

from src.ui.callbacks import refresh_dashboard, reset_filters, toggle_filters

with tgb.Page() as main_page:
    with tgb.layout(
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

            with tgb.layout(columns="1 1", gap="6px"):
                tgb.selector(
                    value="{selected_criticalities}",
                    lov="{criticality_options}",
                    multiple=True,
                    dropdown=True,
                    label="Критичность",
                )

                tgb.selector(
                    value="{selected_sources}",
                    lov="{source_options}",
                    multiple=True,
                    dropdown=True,
                    label="Источник инцидента",
                )

            with tgb.layout(gap="6px"):
                tgb.text("Порог вероятности инцидента")

                tgb.slider(
                    "{prediction_threshold}",
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    continuous=False,
                    width="100%",
                )

                tgb.text("Текущий порог: {prediction_threshold}")

            with tgb.layout("1 1", gap="10px"):
                tgb.button("Применить", on_action=refresh_dashboard,)
                tgb.button("Сбросить", on_action=reset_filters,)

    # metrics
    with tgb.part("card"), tgb.layout(columns="1 1 1 1"):
        with tgb.part():
            tgb.text("**Всего обработано**", mode="md")
            tgb.text("{metric_total}", class_name="metric-value")
        with tgb.part():
            tgb.text("**С валидными метками**", mode="md")
            tgb.text("{metric_labeled}", class_name="metric-value")
        with tgb.part():
            tgb.text("**Пропущено реальных инцидентов**", mode="md")
            tgb.text("{metric_fn}", class_name="metric-value metric-danger")
        with tgb.part():
            tgb.text("**Ложные тревоги**", mode="md")
            tgb.text("{metric_fp}", class_name="metric-value")

    # threshold analysis
    with tgb.layout(columns="1 1", columns__mobile="1"):
        with tgb.part():
            tgb.chart(figure="{threshold_quality_chart}")
        with tgb.part():
            tgb.chart(figure="{threshold_errors_chart}")

    # charts
    with tgb.layout(columns="1 1", columns__mobile="1"):
        with tgb.part():
            tgb.chart(figure="{confusion_chart}")
        with tgb.part():
            tgb.chart(figure="{risk_chart}")

    with tgb.part():
        tgb.chart(figure="{missed_incidents_chart}")
