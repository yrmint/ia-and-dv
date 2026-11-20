# Intelligent Analysis and Data Visualization
Репозиторий курса "Интеллектуальный анализ и визуализация данных"


[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](#)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](#)

[![uv](https://img.shields.io/badge/uv-Lightning_Fast-261230?logo=python&logoColor=white)](#)
[![Ruff](https://img.shields.io/badge/Ruff-Lint%20%26%20Format-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![Taipy](https://img.shields.io/badge/Taipy-Dashboard-FF4B4B?logo=python&logoColor=white)](https://docs.taipy.io/)

## About

Проект реализует аналитический дашборд по инцидентам информационной безопасности (SOC Incident Dashboard).

Дашборд позволяет исследовать данные об инцидентах: динамику, критичность, вердикты, нарушения SLA и типы шумных алертов.


### Ключевые возможности

- Интерактивный дашборд на Taipy GUI
- Фильтрация по периоду, вердикту и критичности
- KPI-метрики (общее количество, открытые, критические инциденты)
- Визуализации:
  - динамика инцидентов во времени
  - нарушения SLA
  - распределение по вердиктам
  - наиболее шумные типы инцидентов
  - критические типы инцидентов
- Тёмная и светлая темы

### Результаты

- Готовый к запуску SOC-дашборд
- Воспроизводимое окружение через `uv`
- Автоматический линтинг и форматирование кода (Ruff + GitHub Actions)

## Технологический Стэк

- **Язык:** Python 3.12+
- **Пакетный менеджер:** uv
- **Дашборд:** Taipy 4.1
- **Данные:** Pandas, Parquet
- **Визуализация:** Plotly, Seaborn
- **Код-стайл и CI:** Ruff, GitHub Actions

## Установка и запуск

### Предварительные требования
- [Набор данных об инцидентах](https://disk.yandex.ru/d/waiZmiOzun8EZA/Datasets) (нужен файл `iavd_incidents_raw_target.parquet`)
- [Python 3.12+](https://www.python.org/downloads/)
- Пакетный менеджер [uv](https://github.com/astral-sh/uv)


### 1. Клонирование репозитория

```commandline
git clone https://github.com/yrmint/ia-and-dv.git
cd ia-and-dv
```

### 2. Установка зависимостей

```commandline
uv sync
```

### 3. Подготовка данных

Разместите файл с данными в папку data/

### 4. Запуск 

```commandline
cd soc-dashboard
uv run python -m app
```

После запуска дашборд доступен на [localhost](http://localhost:5000/)

## Тестирование
Ruff (linting and formatting):
```commandline
uv run ruff check . --fix
```
```commandline
uv run ruff format .
```
