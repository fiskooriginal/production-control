# Конфигурация периодических задач для Celery Beat
#
# Используйте crontab для расписаний:
#   from celery.schedules import crontab
#
# Примеры расписаний:
#   crontab(minute=0, hour=1)          # Каждый день в 01:00
#   crontab(minute="*/5")              # Каждые 5 минут
#   crontab(minute=0, hour="*/3")      # Каждые 3 часа
#   crontab(hour=7, minute=30, day_of_week=1)  # Каждый понедельник в 7:30
#   crontab(day_of_month="1", hour=0)  # Первое число месяца в полночь
#
# Подробнее: https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html

from celery.schedules import crontab

beat_schedule = {
    "process-outbox-events": {
        "task": "tasks.process_outbox_events",
        "schedule": crontab(minute="*/1"),  # Каждую минуту
    },
    "update-dashboard-statistics": {
        "task": "tasks.update_dashboard_stats",
        "schedule": crontab(minute="*/5"),  # Каждые 5 минут
    },
    "auto-close-expired-batches": {
        "task": "tasks.auto_close_expired_batches",
        "schedule": crontab(hour=1, minute=0),  # Каждый день в 01:00
    },
    # Пример: Очистка старых файлов - каждый день в 02:00
    # "cleanup-old-files": {
    #     "task": "tasks.cleanup_old_files",
    #     "schedule": crontab(hour=2, minute=0),
    # },
    #
    # Пример: Повторная отправка webhooks - каждые 15 минут
    # "retry-failed-webhooks": {
    #     "task": "tasks.retry_failed_webhooks",
    #     "schedule": crontab(minute="*/15"),
    # },
}
