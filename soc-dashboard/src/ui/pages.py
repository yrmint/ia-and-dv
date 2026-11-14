import taipy.gui.builder as tgb

from src.ui.callbacks import (
    close_details,
    on_queue_action,
    refresh_dashboard,
    reset_filters,
)

with tgb.Page() as main_page:

    tgb.text("# SOC Incident Dashboard", mode="md")
    tgb.text(
        "Мониторинг и анализ зарегистрированных инцидентов",
        mode="md",
    )

    with tgb.layout(columns="1 1 1"):
        with tgb.part("card"):
            tgb.text("**Всего инцидентов**", mode="md")
            tgb.text("{metric_total}")

        with tgb.part("card"):
            tgb.text("**В очереди**", mode="md")
            tgb.text("{metric_open}")

        with tgb.part("card"):
            tgb.text("**Критических**", mode="md")
            tgb.text("{metric_critical}")

    tgb.text("## Фильтры", mode="md")

    with tgb.layout(columns="1 1 1 1"):
        with tgb.part():
            tgb.date(
                "{date_from}",
                label="Дата от",
            )

        with tgb.part():
            tgb.date(
                "{date_to}",
                label="Дата до",
            )

        with tgb.part():
            tgb.selector(
                "{selected_verdicts}",
                lov="{verdict_options}",
                multiple=True,
                dropdown=True,
                label="Вердикт",
            )

        with tgb.part():
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
