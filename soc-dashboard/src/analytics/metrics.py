import pandas as pd


def _format_duration(seconds: float | None) -> str:
    """Форматирует секунды в человекочитаемый вид."""
    if seconds is None or pd.isna(seconds):
        return "—"

    seconds = float(seconds)
    if seconds < 0:
        return "—"

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    parts = []
    if days > 0:
        parts.append(f"{days} дн.")
    if hours > 0 or days > 0:
        parts.append(f"{hours} ч.")
    parts.append(f"{minutes} мин.")

    return " ".join(parts)

def calculate_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total": 0,
            "open": 0,
            "critical": 0,
            "confirmed": 0,
            "sla_violation_rate": 0.0,
            "avg_take_time": "—",
            "median_take_time": "—",
            "avg_resolve_time": "—",
            "median_resolve_time": "—",
        }

    status = df["status"].fillna("").astype(str)
    criticality = df["criticality"].fillna("").astype(str)
    verdict = df["verdict"].fillna("").astype(str)

    # SLA
    sla_col = "SLA просрочен (взятие в работу)"
    if sla_col in df.columns:
        sla = df[sla_col].map({
            True: True, False: False,
            "True": True, "False": False,
        })
        known_sla = sla.dropna()
        sla_rate = (
            known_sla.sum() / len(known_sla) * 100
            if len(known_sla) > 0 else 0.0
        )
    else:
        sla_rate = 0.0

    take_col = "Период взятия в работу"
    if take_col in df.columns:
        take_seconds = pd.to_numeric(df[take_col], errors="coerce") / 1000
        avg_take = take_seconds.mean()
        median_take = take_seconds.median()
    else:
        avg_take = median_take = None

    resolve_col = "Время решения"
    if resolve_col in df.columns:
        resolve_seconds = (df[resolve_col].where(df[resolve_col].notna()).div(1_000_000))
        resolve_seconds = resolve_seconds[resolve_seconds.gt(0)]
        avg_resolve = resolve_seconds.mean()
        median_resolve = resolve_seconds.median()
    else:
        avg_resolve = median_resolve = None

    return {
        "total": len(df),
        "open": status.str.contains(
            r"Новый|В работе|Ожидание",
            regex=True,
            na=False,
        ).sum(),
        "critical": (criticality == "Критическая").sum(),
        "confirmed": (verdict == "Подтвержденный инцидент").sum(),
        "sla_violation_rate": round(float(sla_rate), 1),
        "avg_take_time": _format_duration(avg_take),
        "median_take_time": _format_duration(median_take),
        "avg_resolve_time": _format_duration(avg_resolve),
        "median_resolve_time": _format_duration(median_resolve),
    }
