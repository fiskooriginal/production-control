def get_dashboard_stats_key(prefix: str = "cache") -> str:
    """Генерирует ключ кэша для статистики дашборда."""
    return f"{prefix}:analytics:dashboard:stats"
