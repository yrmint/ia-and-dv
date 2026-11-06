import pandas as pd


def load_mock_data() -> pd.DataFrame:
    data = [
        {
            "EntityId": 1001,
            "registered_at": "2026-11-07 08:15",
            "verdict": "Подтвержденный инцидент",
            "criticality": "Критическая",
            "status": "В работе",
            "source": "EDR",
            "asset": "WS-001",
            "description": "Подозрительный запуск PowerShell",
            "analyst": "Аналитик 1",
        },
        {
            "EntityId": 1002,
            "registered_at": "2026-11-07 08:42",
            "verdict": "Ложное срабатывание",
            "criticality": "Низкая",
            "status": "Закрыт",
            "source": "SIEM",
            "asset": "SRV-002",
            "description": "Срабатывание правила обнаружения сканирования",
            "analyst": "Аналитик 2",
        },
        {
            "EntityId": 1003,
            "registered_at": "2026-11-07 09:10",
            "verdict": "Не определен",
            "criticality": "Высокая",
            "status": "Новый",
            "source": "IDS",
            "asset": "SRV-003",
            "description": "Обнаружена подозрительная сетевая активность",
            "analyst": "Не назначен",
        },
        {
            "EntityId": 1004,
            "registered_at": "2026-11-07 09:35",
            "verdict": "Подтвержденный инцидент",
            "criticality": "Средняя",
            "status": "Ожидание",
            "source": "EDR",
            "asset": "WS-004",
            "description": "Обнаружен подозрительный файл",
            "analyst": "Аналитик 1",
        },
        {
            "EntityId": 1005,
            "registered_at": "2026-11-07 10:05",
            "verdict": "Ложное срабатывание",
            "criticality": "Средняя",
            "status": "Закрыт",
            "source": "SIEM",
            "asset": "WS-005",
            "description": "Штатная активность администратора",
            "analyst": "Аналитик 3",
        },
        {
            "EntityId": 1006,
            "registered_at": "2026-11-07 10:25",
            "verdict": "Не определен",
            "criticality": "Критическая",
            "status": "Новый",
            "source": "IDS",
            "asset": "SRV-006",
            "description": "Возможная попытка эксплуатации уязвимости",
            "analyst": "Не назначен",
        },
    ]

    df = pd.DataFrame(data)
    df["registered_at"] = pd.to_datetime(df["registered_at"])

    return df
