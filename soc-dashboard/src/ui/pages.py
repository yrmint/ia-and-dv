import taipy.gui.builder as tgb

from src.ui.callbacks import (
    close_details,
    on_queue_action,
    refresh_dashboard,
    reset_filters,
)

with tgb.Page() as main_page:

    with tgb.layout(
            columns="1 auto",
            class_name="dashboard-header",
    ):
        tgb.text("# Инциденты SOC", mode="md")
        tgb.toggle(
            theme=True,
            class_name="relative nolabel theme-toggle",)

    with tgb.layout(
            columns="1 2",
            columns__mobile="1",
            gap="1.5rem",
            class_name="top-layout",
    ):
        with tgb.part(class_name="intro-panel"):
            with tgb.layout(columns="1 1 1", gap="1rem"):
                tgb.text("**Всего инцидентов**", mode="md")
                tgb.text("**В очереди**", mode="md")
                tgb.text("**Критических**", mode="md", class_name="metric-critical")


            with tgb.layout(columns="1 1 1", gap="1rem"):
                # with tgb.part("card"):
                    tgb.text(
                        "{metric_total}",
                        class_name="metric-value",
                    )

                # with tgb.part("card"):
                    tgb.text(
                        "{metric_open}",
                        class_name="metric-value",
                    )

                # with tgb.part("card"):
                    tgb.text(
                        "{metric_critical}",
                        class_name="metric-value metric-critical",
                    )

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

    with tgb.layout(columns="1 1"):
        with tgb.part():
            tgb.chart(figure="{time_chart}")

        with tgb.part():
            tgb.chart(figure="{verdict_chart}")

    with tgb.layout(columns="1"), tgb.part():
        tgb.chart(figure="{noise_chart}")

    with tgb.layout(columns="1"), tgb.part():
        tgb.chart(figure="{criticality_chart}")

    tgb.text("## Очередь инцидентов", mode="md")
    tgb.text(
        "Нажмите на строку, чтобы открыть подробности карточки."
    )

    tgb.table(
        "{queue}",
        columns=[
            "EntityId",
            "Создан",
            "Тип инцидента",
            "Критичность",
            "Фаза реагирования",
            "Вердикт",
            "Ответственный",
            "Количество инцидентов",
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
