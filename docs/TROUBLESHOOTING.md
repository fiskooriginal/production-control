# Устранение неполадок

Руководство по решению распространенных проблем в Production Control.

## Содержание

- [Общие проблемы](#общие-проблемы)
- [Проблемы с базой данных](#проблемы-с-базой-данных)
- [Проблемы с миграциями](#проблемы-с-миграциями)
- [Проблемы с Celery](#проблемы-с-celery)
- [Проблемы с RabbitMQ](#проблемы-с-rabbitmq)
- [Проблемы с Redis](#проблемы-с-redis)
- [Проблемы с MinIO](#проблемы-с-minio)
- [Проблемы с API](#проблемы-с-api)
- [Проблемы с производительностью](#проблемы-с-производительностью)
- [Очистка и сброс](#очистка-и-сброс)

## Общие проблемы

### Сервис не запускается

**Симптомы:**
- Контейнер сразу останавливается
- Ошибки в логах при старте

**Решение:**

1. Проверьте логи:
```bash
docker compose logs app
```

2. Проверьте переменные окружения:
```bash
docker compose exec app env | grep -E "DB_|REDIS_|RABBITMQ_"
```

3. Убедитесь, что все зависимости запущены:
```bash
docker compose ps
```

4. Проверьте healthcheck'и зависимостей:
```bash
docker compose ps --format json | jq '.[] | select(.Health != "healthy" and .Health != "") | {name: .Name, health: .Health}'
```

### Проблемы с сетью Docker

**Симптомы:**
- Сервисы не могут подключиться друг к другу
- Ошибки "Connection refused"

**Решение:**

1. Проверьте сеть Docker:
```bash
docker network ls
docker network inspect production-control.network
```

2. Пересоздайте сеть:
```bash
docker compose down
docker network rm production-control.network
docker compose up -d
```

3. Проверьте, что сервисы используют правильные имена хостов (имена сервисов в docker-compose.yml)

## Проблемы с базой данных

### Ошибка подключения к PostgreSQL

**Ошибка:**
```
OSError: Multiple exceptions: [Errno 111] Connect call failed ('::1', 5432, 0, 0), [Errno 111] Connect call failed ('127.0.0.1', 5432)
```

**Решение:**

1. Убедитесь, что PostgreSQL запущен:
```bash
docker compose ps postgres
```

2. Проверьте переменные окружения:
```bash
docker compose exec app env | grep DB_
```

3. Проверьте логи PostgreSQL:
```bash
docker compose logs postgres
```

4. Проверьте подключение вручную:
```bash
docker compose exec postgres pg_isready -U postgres
```

5. Проверьте, что используется правильный хост:
   - В Docker Compose: `DB_HOST=postgres`
   - Локально: `DB_HOST=localhost`

### База данных не создана

**Решение:**

1. Создайте базу данных вручную:
```bash
docker compose exec postgres psql -U postgres -c "CREATE DATABASE production_control;"
```

2. Или пересоздайте контейнер PostgreSQL:
```bash
docker compose down -v postgres
docker compose up -d postgres
```

### Проблемы с правами доступа

**Ошибка:**
```
permission denied for schema public
```

**Решение:**

1. Предоставьте права пользователю:
```bash
docker compose exec postgres psql -U postgres -d production_control -c "GRANT ALL ON SCHEMA public TO postgres;"
```

### Медленные запросы

**Решение:**

1. Проверьте активные запросы:
```sql
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND query NOT LIKE '%pg_stat_activity%';
```

2. Проверьте индексы:
```sql
SELECT tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

3. Проверьте размер таблиц:
```sql
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Проблемы с миграциями

### Ошибка: "Relative revision -N didn't produce N migrations"

**Ошибка:**
```
ERROR [alembic.util.messaging] Relative revision -10 didn't produce 10 migrations
```

**Решение:**

Используйте конкретные ревизии вместо относительных:

```bash
# Вместо
alembic downgrade -10

# Используйте
alembic history  # найти нужную ревизию
alembic downgrade <revision_hash>
```

### Миграция не применяется

**Решение:**

1. Проверьте текущую версию:
```bash
alembic current
```

2. Проверьте историю:
```bash
alembic history
```

3. Примените миграцию принудительно:
```bash
alembic upgrade <revision_hash>
```

4. Если миграция застряла, проверьте блокировки:
```sql
SELECT * FROM pg_locks WHERE relation = 'alembic_version'::regclass;
```

### Конфликт миграций

**Решение:**

1. Проверьте, что миграции в правильном порядке:
```bash
alembic history --verbose
```

2. Если есть конфликт, создайте merge миграцию:
```bash
alembic merge -m "merge migrations" heads
```

### Откат миграции с данными

**Внимание:** Откат миграции может привести к потере данных!

**Решение:**

1. Сделайте резервную копию:
```bash
docker compose exec postgres pg_dump -U postgres production_control > backup.sql
```

2. Проверьте миграцию перед откатом:
```bash
alembic downgrade -1 --sql  # посмотреть SQL без выполнения
```

3. Откатите миграцию:
```bash
alembic downgrade -1
```

## Проблемы с Celery

### Задачи не выполняются

**Симптомы:**
- Задачи остаются в статусе PENDING
- Нет активности в логах воркера

**Решение:**

1. Проверьте, что воркер запущен:
```bash
docker compose ps celery_worker
```

2. Проверьте подключение к RabbitMQ:
```bash
docker compose logs rabbitmq
docker compose exec celery_worker celery -A src.infrastructure.background_tasks.app:celery_app inspect active
```

3. Проверьте подключение к Redis:
```bash
docker compose logs redis
docker compose exec redis redis-cli ping
```

4. Проверьте логи воркера:
```bash
docker compose logs celery_worker
```

5. Проверьте зарегистрированные задачи:
```bash
docker compose exec celery_worker celery -A src.infrastructure.background_tasks.app:celery_app inspect registered
```

### Периодические задачи не запускаются

**Симптомы:**
- Задачи из beat_schedule не выполняются
- Нет записей в логах beat

**Решение:**

1. Убедитесь, что `celery_beat` запущен:
```bash
docker compose ps celery_beat
```

2. Проверьте конфигурацию в `beat_schedule.py`

3. Проверьте логи beat:
```bash
docker compose logs celery_beat
```

4. Проверьте расписание:
```bash
docker compose exec celery_beat celery -A src.infrastructure.background_tasks.app:celery_app inspect scheduled
```

5. Проверьте файл расписания:
```bash
docker compose exec celery_beat ls -la /app/celerybeat-schedule/
```

### Задачи падают с ошибками

**Решение:**

1. Проверьте логи воркера:
```bash
docker compose logs celery_worker | grep ERROR
```

2. Проверьте статус задачи через API:
```bash
curl http://localhost:8000/api/background_tasks/{task_id}
```

3. Проверьте через Flower:
   - Откройте <http://localhost:5555>
   - Перейдите в раздел "Tasks"
   - Найдите задачу и посмотрите traceback

### Высокая загрузка очереди

**Решение:**

1. Проверьте длину очереди в RabbitMQ Management:
   - Откройте <http://localhost:15672>
   - Перейдите в раздел "Queues"

2. Увеличьте количество воркеров:
```env
CELERY_WORKER_CONCURRENCY=4
```

3. Проверьте, нет ли зависших задач:
```bash
docker compose exec celery_worker celery -A src.infrastructure.background_tasks.app:celery_app inspect active
```

## Проблемы с RabbitMQ

### RabbitMQ не запускается

**Решение:**

1. Проверьте логи:
```bash
docker compose logs rabbitmq
```

2. Проверьте права доступа к volumes:
```bash
docker compose exec rabbitmq ls -la /var/lib/rabbitmq
```

3. Очистите данные и пересоздайте:
```bash
docker compose down -v rabbitmq
docker compose up -d rabbitmq
```

### Проблемы с подключением

**Ошибка:**
```
Connection refused to RabbitMQ
```

**Решение:**

1. Проверьте, что RabbitMQ запущен:
```bash
docker compose ps rabbitmq
```

2. Проверьте переменные окружения:
```bash
docker compose exec app env | grep RABBITMQ_
```

3. Проверьте подключение:
```bash
docker compose exec rabbitmq rabbitmq-diagnostics ping
```

4. Проверьте через Management API:
```bash
curl -u guest:guest http://localhost:15672/api/overview
```

## Проблемы с Redis

### Redis не отвечает

**Решение:**

1. Проверьте, что Redis запущен:
```bash
docker compose ps redis
```

2. Проверьте подключение:
```bash
docker compose exec redis redis-cli ping
```

3. Проверьте логи:
```bash
docker compose logs redis
```

4. Если используется пароль, проверьте переменную окружения:
```bash
docker compose exec app env | grep REDIS_PASSWORD
```

### Проблемы с кэшем

**Решение:**

1. Очистите кэш:
```bash
docker compose exec redis redis-cli FLUSHDB
```

2. Проверьте использование памяти:
```bash
docker compose exec redis redis-cli INFO memory
```

## Проблемы с MinIO

### Ошибка подключения к MinIO

**Решение:**

1. Проверьте, что MinIO запущен:
```bash
docker compose ps minio
```

2. Проверьте переменные окружения:
```bash
docker compose exec app env | grep MINIO_
```

3. Проверьте подключение:
```bash
curl http://localhost:19000/minio/health/live
```

4. Проверьте через консоль:
   - Откройте <http://localhost:19001>
   - Войдите с учетными данными

### Bucket'ы не создаются

**Решение:**

1. Проверьте переменную `MINIO_BUCKETS`:
```bash
docker compose exec app env | grep MINIO_BUCKETS
```

2. Создайте bucket'ы вручную через консоль MinIO

3. Проверьте логи приложения при старте:
```bash
docker compose logs app | grep -i minio
```

## Проблемы с API

### 500 Internal Server Error

**Решение:**

1. Проверьте логи приложения:
```bash
docker compose logs app | tail -50
```

2. Проверьте логи с фильтром по ошибкам:
```bash
docker compose logs app | grep -i error
```

3. Проверьте подключение к БД:
```bash
curl http://localhost:8000/api/healthcheck/database
```

4. Включите DEBUG логирование:
```env
LOG_LEVEL=DEBUG
```

### Медленные запросы

**Решение:**

1. Проверьте логи с временем выполнения:
```bash
docker compose logs app | grep -E "duration|time"
```

2. Проверьте базу данных (см. раздел "Медленные запросы")

3. Проверьте использование ресурсов:
```bash
docker stats app
```

4. Проверьте количество соединений к БД:
```sql
SELECT count(*) FROM pg_stat_activity;
```

### Ошибки валидации (422)

**Решение:**

1. Проверьте формат запроса в Swagger UI: <http://localhost:8000/docs>
2. Проверьте схему в `src/presentation/api/schemas/`
3. Включите DEBUG логирование для детальной информации об ошибках

## Проблемы с производительностью

### Высокое использование CPU

**Решение:**

1. Проверьте процессы:
```bash
docker stats
```

2. Проверьте активные задачи Celery:
```bash
docker compose exec celery_worker celery -A src.infrastructure.background_tasks.app:celery_app inspect active
```

3. Уменьшите количество воркеров:
```env
CELERY_WORKER_CONCURRENCY=1
```

### Высокое использование памяти

**Решение:**

1. Проверьте использование памяти:
```bash
docker stats
```

2. Проверьте размер БД:
```sql
SELECT pg_size_pretty(pg_database_size('production_control'));
```

3. Очистите старые данные из outbox:
```sql
DELETE FROM outbox_events WHERE processed_at < NOW() - INTERVAL '7 days';
```

4. Очистите кэш Redis:
```bash
docker compose exec redis redis-cli FLUSHDB
```

### Медленная работа БД

**Решение:**

1. Проверьте индексы:
```sql
SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public';
```

2. Выполните ANALYZE:
```sql
ANALYZE;
```

3. Проверьте медленные запросы (требует настройки):
```sql
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## Очистка и сброс

### Полный сброс окружения

**Внимание:** Это удалит все данные!

```bash
# Остановить и удалить все контейнеры и volumes
docker compose down -v

# Удалить все volumes вручную
docker volume rm production-control.postgres.data
docker volume rm production-control.redis.data
docker volume rm production-control.rabbitmq.data
docker volume rm production-control.minio.data
docker volume rm production-control.celery_beat.schedule

# Пересоздать все
docker compose up -d
```

### Очистка только данных БД

```bash
# Подключиться к БД
docker compose exec postgres psql -U postgres -d production_control

# Удалить все данные (сохраняя структуру)
TRUNCATE TABLE batches, products, work_centers, webhook_subscriptions CASCADE;
```

### Очистка очередей Celery

```bash
# Очистить все очереди
docker compose exec rabbitmq rabbitmqctl purge_queue default
```

### Очистка кэша Redis

```bash
# Очистить текущую БД
docker compose exec redis redis-cli FLUSHDB

# Очистить все БД
docker compose exec redis redis-cli FLUSHALL
```

### Очистка старых данных

```sql
-- Удалить старые события из outbox (старше 7 дней)
DELETE FROM outbox_events 
WHERE processed_at < NOW() - INTERVAL '7 days';

-- Удалить старые доставки вебхуков (старше 30 дней)
DELETE FROM webhook_deliveries 
WHERE created_at < NOW() - INTERVAL '30 days';
```

## Получение помощи

Если проблема не решена:

1. Соберите информацию:
   - Версия Python: `python --version`
   - Версия Docker: `docker --version`
   - Логи проблемного сервиса: `docker compose logs <service>`
   - Конфигурация: `.env` (без паролей!)

2. Проверьте документацию:
   - [Установка и настройка](INSTALLATION.md)
   - [Конфигурация](CONFIGURATION.md)
   - [Мониторинг](MONITORING.md)

3. Создайте issue с описанием проблемы и собранной информацией

## Дополнительная информация

- [Установка и настройка](INSTALLATION.md)
- [Конфигурация](CONFIGURATION.md)
- [Мониторинг](MONITORING.md)
- [Руководство по разработке](DEVELOPMENT.md)

