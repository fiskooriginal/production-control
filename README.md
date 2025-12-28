# Production Control

Система управления производством с поддержкой фоновых задач и событийно-ориентированной архитектуры.

## Архитектура

Проект следует принципам Clean Architecture с разделением на слои:

- **Domain**: бизнес-логика, сущности, события, исключения
- **Application**: commands, query handlers, DTO
- **Infrastructure**: репозитории, БД, Celery, outbox
- **Presentation**: FastAPI endpoints, schemas, mappers

## Требования

- Python 3.13+
- Docker и Docker Compose
- uv (для управления зависимостями)

> **💡 Использование Dev Containers**: Проект поддерживает Dev Containers для быстрой настройки среды разработки. Подробные инструкции по настройке VS Code и PyCharm см. в [docs/DEVCONTAINERS.md](docs/DEVCONTAINERS.md).

## Установка зависимостей

```bash
uv sync
```

## Запуск сервисов

### API сервер (FastAPI)

```bash
# Production режим
docker compose --profile api up -d

# Dev режим с hot-reload
docker compose --profile dev up -d
```

API доступно на: <http://localhost:8000>

### Миграции БД

```bash
docker compose --profile migration up
```

### Celery workers и планировщик

```bash
# Запустить worker, beat и flower
docker compose --profile celery up -d
```

Доступ к сервисам:

- **Flower** (мониторинг): <http://localhost:5555>
- **RabbitMQ Management**: <http://localhost:15672> (guest/guest)

### Полный стек (API + Celery)

```bash
docker compose --profile api --profile celery up -d
```

## Конфигурация

Настройки задаются через переменные окружения в `.env` файле:

### База данных

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=production_control
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=public
```

### Redis

```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

### RabbitMQ

```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
```

### Celery

```env
CELERY_BROKER_URL=  # если не указано, собирается из RABBITMQ_*
CELERY_RESULT_BACKEND=  # если не указано, собирается из REDIS_*
CELERY_TIMEZONE=UTC
CELERY_TASK_DEFAULT_QUEUE=default
CELERY_TASK_ACKS_LATE=true
CELERY_TASK_REJECT_ON_WORKER_LOST=true
CELERY_WORKER_CONCURRENCY=2
CELERY_REDIS_KEY_PREFIX=celery
```

### Логирование

```env
LOG_LEVEL=INFO
```

## Структура проекта

```
src/
├── core/               # Общие настройки, логирование, база данных
├── domain/             # Доменная модель (сущности, события, value objects)
├── application/        # Commands и query handlers
├── infrastructure/     # Реализация инфраструктуры
│   ├── celery/         # Celery app и задачи
│   │   ├── app.py              # Bootstrap Celery приложения
│   │   ├── beat_schedule.py    # Конфигурация периодических задач
│   │   └── tasks/              # Celery задачи
│   ├── events/         # Сериализация событий и реестр
│   ├── persistence/    # Модели БД, репозитории, миграции
│   └── uow/            # Unit of Work с event collection
└── presentation/       # FastAPI приложение и endpoints
```

## Разработка

### Добавление новой задачи Celery

1. Создайте модуль задачи в `src/infrastructure/celery/tasks/`:

```python
from src.infrastructure.celery.app import celery_app

@celery_app.task(name="my_module.my_task")
def my_task(arg1: str) -> dict:
    # ваша логика
    return {"status": "done"}
```

1. Импортируйте задачу в `src/infrastructure/celery/tasks/__init__.py`:

```python
from src.infrastructure.celery.tasks.my_module import my_task

__all__ = ["my_task", ...]
```

1. Обновите `include` в `src/infrastructure/celery/app.py`:

```python
celery_app = Celery(
    "production_control",
    broker=broker_url,
    backend=result_backend,
    include=[
        "src.infrastructure.celery.tasks.outbox",
        "src.infrastructure.celery.tasks.my_module",
    ],
)
```

### Добавление периодической задачи

Периодические задачи настраиваются в файле `src/infrastructure/celery/beat_schedule.py`:

```python
from celery.schedules import crontab

beat_schedule = {
    # Каждый день в 01:00
    "auto-close-expired-batches": {
        "task": "tasks.auto_close_expired_batches",
        "schedule": crontab(hour=1, minute=0),
    },

    # Каждые 5 минут
    "update-statistics": {
        "task": "tasks.update_cached_statistics",
        "schedule": crontab(minute="*/5"),
    },

    # Каждые 15 минут
    "retry-failed-webhooks": {
        "task": "tasks.retry_failed_webhooks",
        "schedule": crontab(minute="*/15"),
    },

    # Используйте числа (float/int) для интервалов в секундах
    "quick-poll": {
        "task": "tasks.quick_check",
        "schedule": 30.0,  # каждые 30 секунд
    },
}
```

**Примеры crontab расписаний:**

- `crontab(minute=0, hour=1)` — каждый день в 01:00
- `crontab(minute="*/5")` — каждые 5 минут
- `crontab(minute=0, hour="*/3")` — каждые 3 часа
- `crontab(hour=7, minute=30, day_of_week=1)` — каждый понедельник в 7:30
- `crontab(day_of_month="1", hour=0)` — первое число месяца в полночь
- `crontab(0, 0, day_of_month='2-30/2')` — каждый чётный день месяца

Подробнее: [Celery Periodic Tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html)

### Просмотр зарегистрированных задач

```bash
# Список всех задач
docker compose exec celery_worker celery -A src.infrastructure.celery.app:celery_app inspect registered

# Активные периодические задачи
docker compose exec celery_beat celery -A src.infrastructure.celery.app:celery_app inspect scheduled
```

## Мониторинг

- **Flower**: <http://localhost:5555> — мониторинг Celery задач
- **RabbitMQ Management**: <http://localhost:15672> — управление очередями
- **Логи**: `docker compose logs -f <service>`

```bash
# Логи конкретного сервиса
docker compose logs -f celery_worker
docker compose logs -f celery_beat
docker compose logs -f flower
```
