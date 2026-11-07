main_page = """
# SOC Incident Dashboard

Мониторинг и анализ зарегистрированных инцидентов

<|layout|columns=1 1 1|
<|
**Всего инцидентов**

<|{metric_total}|text|>
|>

<|
**В очереди**

<|{metric_open}|text|>
|>

<|
**Критических**

<|{metric_critical}|text|>
|>
|>

---

## Фильтры

<|layout|columns=1 1 1 1|
<|
Дата от

<|{date_from}|date|>
|>

<|
Дата до

<|{date_to}|date|>
|>

<|
Вердикт

<|{selected_verdicts}|selector|lov={verdict_options}|multiple|>
|>

<|
Критичность

<|{selected_criticalities}|selector|lov={criticality_options}|multiple|>
|>
|>

<|Применить фильтры|button|on_action=refresh_dashboard|>
<|Сбросить фильтры|button|on_action=reset_filters|>

---

## Аналитика

<|layout|columns=1 1|
<|
<|chart|figure={time_chart}|>
|>

<|
<|chart|figure={verdict_chart}|>
|>
|>

---

## Очередь инцидентов

Нажмите на строку, чтобы открыть подробности карточки.

<|{queue}|table|columns=EntityId;registered_at;verdict;criticality;status;source;asset|page_size=10|on_action=on_queue_action|>

<|{details_open}|dialog|title=Карточка инцидента|on_action=close_details|
<|{details_text}|text|mode=pre|>

<|Закрыть|button|on_action=close_details|>
|>
"""
