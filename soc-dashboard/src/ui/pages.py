import taipy.gui.builder as tgb

from src.ui.callbacks import (
    close_details,
    on_period_change,
    on_queue_action,
    refresh_dashboard,
    reset_filters,
)

with tgb.Page() as main_page:

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

        tgb.toggle(
            theme=True,
            class_name="relative nolabel theme-toggle",
        )

    with tgb.layout(
            columns="1 2",
            columns__mobile="1",
            gap="1.5rem",
            class_name="top-layout",
    ):
        with tgb.layout(columns="1 1 1 1 1 1", gap="1rem", class_name="kpi-row"):

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


        with tgb.part(class_name="filters-panel"):
            with tgb.layout(
                    columns="1 1",
                    columns__mobile="1",
            ):
                tgb.date(
                    "{date_from}",
                    label="Дата от",
                )

                tgb.date(
                    "{date_to}",
                    label="Дата до",
                )

                tgb.selector(
                    "{selected_verdicts}",
                    lov="{verdict_options}",
                    multiple=True,
                    dropdown=True,
                    label="Вердикт",
                )

                tgb.selector(
                    "{selected_criticalities}",
                    lov="{criticality_options}",
                    multiple=True,
                    dropdown=True,
                    label="Критичность",
                )

            with tgb.layout(columns="1 1"):
                tgb.button(
                    "Применить фильтры",
                    on_action=refresh_dashboard,
                )

                tgb.button(
                    "Сбросить фильтры",
                    on_action=reset_filters,
                )



    tgb.text("## Аналитика", mode="md")
    tgb.toggle(
        "{selected_period}",
        lov=["7 дней", "30 дней"],
        on_change=on_period_change,
    )

    with tgb.layout(columns="1 1", gap="1rem"):
        with tgb.part():
            tgb.chart(figure="{time_chart}")

        with tgb.part():
            tgb.chart(figure="{sla_chart}")

    with tgb.layout(columns="1 1", gap="1rem"):
            with tgb.part():
                tgb.chart(figure="{noise_chart}")

            with tgb.part():
                tgb.chart(figure="{criticality_chart}")

    with tgb.layout(columns="1"), tgb.part():
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
