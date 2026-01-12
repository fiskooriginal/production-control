# Установка и настройка

Это руководство поможет вам установить и настроить Production Control для локальной разработки или production окружения.

## Содержание

- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Установка с Docker](#установка-с-docker)
- [Локальная установка](#локальная-установка)
- [Настройка окружения](#настройка-окружения)
- [Применение миграций](#применение-миграций)
- [Проверка установки](#проверка-установки)

## Требования

### Обязательные требования

- **Python 3.13+** — основной язык разработки
- **Docker 20.10+** и **Docker Compose 2.0+** — для контейнеризации
- **uv** — менеджер зависимостей Python (рекомендуется)

### Опциональные требования

- **Git** — для клонирования репозитория
- **PostgreSQL 17+** — если запускаете БД локально (без Docker)
- **Redis 7+** — если запускаете Redis локально
- **RabbitMQ 3.13+** — если запускаете RabbitMQ локально
- **MinIO** — если запускаете MinIO локально

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd production-control
```

### 2. Настройка окружения

Создайте файл `.env` в корне проекта. Пример конфигурации см. в [CONFIGURATION.md](CONFIGURATION.md).

### 3. Установка зависимостей

```bash
uv sync
```

### 4. Запуск миграций

```bash
docker compose --profile migration up
```

### 5. Запуск сервисов

```bash
# Запуск всего стека (API + Celery)
docker compose --profile api --profile celery up -d
```

### 6. Проверка работоспособности

```bash
# Проверка API
curl http://localhost:8000/api/healthcheck/service

# Проверка базы данных
curl http://localhost:8000/api/healthcheck/database
```

## Установка с Docker

### Предварительные требования

Убедитесь, что Docker и Docker Compose установлены и запущены:

```bash
docker --version
docker compose version
```

### Запуск всех сервисов

```bash
# Запуск всего стека
docker compose --profile api --profile celery up -d

# Просмотр статуса
docker compose ps

# Просмотр логов
docker compose logs -f
```

### Запуск отдельных сервисов

#### Только API сервер

```bash
docker compose --profile api up -d
```

API будет доступно на <http://localhost:8000>

#### Только Celery (workers, beat, flower)

```bash
docker compose --profile celery up -d
```

Сервисы будут доступны:
- **Flower**: <http://localhost:5555>
- **RabbitMQ Management**: <http://localhost:15672>
- **MinIO Console**: <http://localhost:19001>

### Остановка сервисов

```bash
# Остановить все сервисы
docker compose down

# Остановить и удалить volumes (удалит все данные!)
docker compose down -v
```

## Локальная установка

Если вы предпочитаете запускать приложение локально без Docker (кроме инфраструктурных сервисов):

### 1. Установка зависимостей

```bash
# Установка uv (если еще не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка зависимостей проекта
uv sync
```

### 2. Активация виртуального окружения

```bash
# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Запуск инфраструктурных сервисов

Запустите PostgreSQL, Redis, RabbitMQ и MinIO через Docker:

```bash
docker compose --profile app up -d postgres redis rabbitmq minio
```

Или используйте локальные установки этих сервисов.

### 4. Настройка переменных окружения

Убедитесь, что в `.env` указаны правильные хосты для локальных сервисов:

```env
DB_HOST=localhost
REDIS_HOST=localhost
RABBITMQ_HOST=localhost
MINIO_ENDPOINT=localhost:9000
```

### 5. Применение миграций

```bash
alembic upgrade head
```

### 6. Запуск приложения

```bash
# Запуск API сервера
uvicorn src.presentation.main:app --reload --host 0.0.0.0 --port 8000

# В отдельном терминале - запуск Celery worker
celery -A src.infrastructure.background_tasks.app:celery_app worker -l INFO

# В отдельном терминале - запуск Celery beat
celery -A src.infrastructure.background_tasks.app:celery_app beat -l INFO

# В отдельном терминале - запуск Flower
celery -A src.infrastructure.background_tasks.app:celery_app flower --port=5555
```

## Настройка окружения

### Создание .env файла

Создайте файл `.env` в корне проекта. Подробное описание всех переменных окружения см. в [CONFIGURATION.md](CONFIGURATION.md).

Минимальная конфигурация для начала работы:

```env
# База данных
DB_HOST=postgres
DB_PORT=5432
DB_NAME=production_control
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=public

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKETS=reports,exports,imports
MINIO_SECURE=false

# Логирование
LOG_LEVEL=INFO
```

### Использование Dev Containers

Проект поддерживает Dev Containers для быстрой настройки среды разработки. Подробные инструкции см. в [DEVCONTAINERS.md](DEVCONTAINERS.md).

## Применение миграций

### С использованием Docker

```bash
docker compose --profile migration up
```

### Локально

```bash
# Применить все миграции
alembic upgrade head

# Применить конкретную миграцию
alembic upgrade <revision_hash>

# Откатить последнюю миграцию
alembic downgrade -1

# Откатить до конкретной ревизии
alembic downgrade <revision_hash>

# Просмотр текущей версии
alembic current

# Просмотр истории миграций
alembic history

# Создание новой миграции
alembic revision --autogenerate -m "описание изменений"
```

### Проверка миграций

```bash
# Проверить текущую версию БД
alembic current

# Просмотреть историю
alembic history --verbose
```

## Проверка установки

### 1. Проверка API

```bash
# Проверка статуса сервиса
curl http://localhost:8000/api/healthcheck/service

# Ожидаемый ответ:
# {"status": "ok"}

# Проверка подключения к БД
curl http://localhost:8000/api/healthcheck/database

# Ожидаемый ответ:
# {"status": "ok"}
```

### 2. Проверка документации API

Откройте в браузере:
- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

### 3. Проверка Celery

```bash
# Проверка зарегистрированных задач
docker compose exec celery_worker celery -A src.infrastructure.background_tasks.app:celery_app inspect registered

# Проверка статуса воркеров
docker compose exec celery_worker celery -A src.infrastructure.background_tasks.app:celery_app inspect active
```

### 4. Проверка инфраструктурных сервисов

```bash
# Проверка статуса всех контейнеров
docker compose ps

# Проверка логов
docker compose logs --tail=50
```

### 5. Проверка подключений

- **PostgreSQL**: `docker compose exec postgres pg_isready -U postgres`
- **Redis**: `docker compose exec redis redis-cli ping`
- **RabbitMQ**: `docker compose exec rabbitmq rabbitmq-diagnostics ping`
- **MinIO**: Откройте <http://localhost:19001> в браузере

## Следующие шаги

После успешной установки:

1. Ознакомьтесь с [API документацией](API.md)
2. Изучите [руководство по разработке](DEVELOPMENT.md)
3. Настройте [мониторинг](MONITORING.md)
4. Прочитайте [руководство по устранению неполадок](TROUBLESHOOTING.md) на случай проблем

## Проблемы при установке?

Если вы столкнулись с проблемами при установке, см. раздел [Устранение неполадок](TROUBLESHOOTING.md).

