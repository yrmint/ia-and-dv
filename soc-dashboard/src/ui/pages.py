import taipy.gui.builder as tgb

from src.ui.callbacks import (
    close_details,
    on_period_change,
    on_queue_action,
    refresh_dashboard,
    reset_filters,
    toggle_filters,
)

with tgb.Page() as main_page:

    # Header
    with tgb.layout(
            columns="1 auto",
            class_name="dashboard-header",
    ):
        with tgb.layout(
                columns="auto auto",
                class_name="dashboard-title-group",
        ):
            tgb.text("# Инциденты SOC", mode="md")
            tgb.text("{current_date}", class_name="current-date")

        with tgb.layout(
            columns="auto auto",
            class_name="title-buttons-group",
        ):
            tgb.button(
                "Фильтры",
                on_action=toggle_filters,
                class_name="relative nolabel",
            )
            tgb.toggle(
                theme=True,
                class_name="relative nolabel theme-toggle",
            )

    # Filters slider
    with tgb.pane(open="{filters_open}"):   # noqa: SIM117
        with tgb.layout(columns="1", class_name="filters-content", gap="16px"):

            tgb.text("## Фильтры", mode="md")

            # Dates
            with tgb.layout(columns="4 1 4", gap="6px"):
                tgb.date("{date_from}", label="От")
                with tgb.layout(columns="1", class_name="dash-container"):
                    tgb.text("—", class_name="dash-text")
                tgb.date("{date_to}", label="До")

            # Verdict + Сriticality
            with tgb.layout(columns="1 1", gap="6px"):
                tgb.selector(
                    value="{selected_verdicts}",
                    lov="{verdict_options}",
                    multiple=True,
                    dropdown=True,
                    label="Вердикт",
                )
                tgb.selector(
                    value="{selected_criticalities}",
                    lov="{criticality_options}",
                    multiple=True,
                    dropdown=True,
                    label="Критичность",
                )

            # Buttons
            with tgb.layout("1 1", gap="10px"):
                tgb.button("Применить", on_action=refresh_dashboard,)
                tgb.button("Сбросить", on_action=reset_filters,)

    # KPI metrics
    with tgb.layout(
        columns="1 1 1 1 1 1",
        gap="1rem",
        class_name="kpi-row",
        ):

            with tgb.part(class_name="kpi-card"):
                tgb.text("Всего", class_name="kpi-label")
                tgb.text("{metric_total}", class_name="kpi-value")

            with tgb.part(class_name="kpi-card"):
                tgb.text("В очереди", class_name="kpi-label")
                tgb.text("{metric_open}", class_name="kpi-value")

            with tgb.part(class_name="kpi-card"):
                tgb.text("Критических", class_name="kpi-label")
                tgb.text("{metric_critical}", class_name="kpi-value metric-critical")

            with tgb.part(class_name="kpi-card"):
                tgb.text("Нарушения SLA", class_name="kpi-label")
                tgb.text("{metric_sla_rate} %", class_name="kpi-value")

            with tgb.part(class_name="kpi-card"):
                tgb.text("Ср. время взятия", class_name="kpi-label")
                tgb.text("{metric_avg_take}", class_name="kpi-value")

            with tgb.part(class_name="kpi-card"):
                tgb.text("Ср. время решения", class_name="kpi-label")
                tgb.text("{metric_avg_resolve}", class_name="kpi-value")


    tgb.text("## Аналитика", mode="md")
    tgb.toggle(
        "{selected_period}",
        lov=["7 дней", "30 дней"],
        on_change=on_period_change,
    )

    with tgb.layout(columns="1 1", gap="1rem"):
        with tgb.part(class_name="chart-bottom-spacing"):
            tgb.chart(figure="{time_chart}")

        with tgb.part(class_name="chart-bottom-spacing"):
            tgb.chart(figure="{sla_chart}")

    with tgb.layout(columns="1 1", gap="1rem"):
            with tgb.part(class_name="chart-bottom-spacing"):
                tgb.chart(figure="{noise_chart}")

            with tgb.part(class_name="chart-bottom-spacing"):
                tgb.chart(figure="{criticality_chart}")

    with tgb.layout(columns="1"), tgb.part(class_name="chart-bottom-spacing"):
            tgb.chart(figure="{resolve_time_chart}")

    tgb.text("## Очередь инцидентов", mode="md")
    tgb.text(
        "Нажмите на строку, чтобы открыть подробности карточки."
    )

    tgb.table(
        "{queue}",
        columns=[
            "ID",
            "Создан",
            "Тип инцидента",
            "Критичность",
            "Вердикт",
            "Ответственный",
        ],
        page_size=10,
        on_action=on_queue_action,
    )

    with tgb.dialog(
            "{details_open}",
            title="Карточка инцидента",
            on_action=close_details,
    ):
        tgb.text(
            "{details_text}",
            mode="pre",
        )

        tgb.button(
            "Закрыть",
            on_action=close_details,
        )
