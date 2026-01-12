# Мониторинг и логирование

Руководство по мониторингу и логированию Production Control.

## Содержание

- [Обзор](#обзор)
- [Логирование](#логирование)
- [Мониторинг сервисов](#мониторинг-сервисов)
- [Healthcheck endpoints](#healthcheck-endpoints)
- [Flower (Celery мониторинг)](#flower-celery-мониторинг)
- [RabbitMQ Management](#rabbitmq-management)
- [Мониторинг базы данных](#мониторинг-базы-данных)
- [Метрики и алерты](#метрики-и-алерты)

## Обзор

Production Control предоставляет несколько инструментов для мониторинга состояния системы:

- Логирование через стандартный Python logging
- Healthcheck endpoints для проверки состояния
- Flower для мониторинга Celery задач
- RabbitMQ Management для мониторинга очередей
- Интеграция с внешними системами мониторинга

## Логирование

### Уровни логирования

Уровень логирования настраивается через переменную окружения `LOG_LEVEL`:

- `DEBUG` — детальная отладочная информация (только для разработки)
- `INFO` — информационные сообщения (по умолчанию)
- `WARNING` — предупреждения
- `ERROR` — ошибки
- `CRITICAL` — критические ошибки

### Просмотр логов

#### Docker Compose

```bash
# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f app
docker compose logs -f celery_worker
docker compose logs -f celery_beat
docker compose logs -f flower

# Последние 100 строк
docker compose logs --tail=100 app

# Логи с временными метками
docker compose logs -f --timestamps app
```

#### Локальная разработка

Логи выводятся в консоль (stdout/stderr). Для перенаправления в файл:

```bash
uvicorn src.presentation.main:app --reload 2>&1 | tee app.log
```

### Формат логов

Логи форматируются в JSON для удобного парсинга:

```json
{
  "timestamp": "2025-01-15T10:30:00.123456Z",
  "level": "INFO",
  "logger": "app",
  "message": "Application started successfully",
  "module": "main",
  "function": "lifespan"
}
```

### Структурированное логирование

Пример использования в коде:

```python
from src.core.logging import get_logger

logger = get_logger("my_module")

logger.info("Processing batch", extra={
    "batch_id": batch_id,
    "batch_number": batch_number
})

logger.error("Failed to process batch", exc_info=True, extra={
    "batch_id": batch_id,
    "error": str(e)
})
```

## Мониторинг сервисов

### Проверка статуса контейнеров

```bash
# Статус всех контейнеров
docker compose ps

# Детальная информация
docker compose ps -a

# Использование ресурсов
docker stats
```

### Healthcheck контейнеров

Все сервисы имеют встроенные healthcheck'и:

```bash
# Проверка healthcheck'ов
docker compose ps --format json | jq '.[] | {name: .Name, health: .Health}'
```

## Healthcheck endpoints

### Проверка статуса сервиса

```bash
curl http://localhost:8000/api/healthcheck/service
```

**Ответ:**

```json
{
  "status": "ok"
}
```

### Проверка подключения к БД

```bash
curl http://localhost:8000/api/healthcheck/database
```

**Ответ:**

```json
{
  "status": "ok"
}
```

### Использование в мониторинге

Эти endpoints можно использовать в системах мониторинга:

```bash
# Проверка с таймаутом
curl --max-time 5 http://localhost:8000/api/healthcheck/service

# Проверка с ожиданием определенного статуса
curl -f http://localhost:8000/api/healthcheck/service || echo "Service is down"
```

### Настройка мониторинга

Пример конфигурации для Prometheus (если добавлен exporter):

```yaml
scrape_configs:
  - job_name: 'production-control'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:8000']
```

## Flower (Celery мониторинг)

### Доступ

Flower доступен по адресу: <http://localhost:5555>

### Возможности

- **Просмотр активных задач** — задачи, выполняющиеся в данный момент
- **История выполнения** — завершенные задачи с результатами
- **Мониторинг воркеров** — статус и производительность воркеров
- **Статистика** — общая статистика по задачам
- **Управление задачами** — отмена задач, перезапуск воркеров

### Основные разделы

1. **Dashboard** — общая статистика
2. **Tasks** — список всех задач
3. **Workers** — список воркеров
4. **Monitor** — мониторинг в реальном времени
5. **Broker** — информация о брокере сообщений

### API Flower

Flower предоставляет REST API для программного доступа:

```bash
# Список активных задач
curl http://localhost:5555/api/tasks?state=ACTIVE

# Информация о воркерах
curl http://localhost:5555/api/workers

# Статистика
curl http://localhost:5555/api/stats
```

## RabbitMQ Management

### Доступ

RabbitMQ Management доступен по адресу: <http://localhost:15672>

Учетные данные по умолчанию: `guest` / `guest`

### Основные разделы

1. **Overview** — общая информация о кластере
2. **Connections** — активные соединения
3. **Channels** — открытые каналы
4. **Exchanges** — exchanges и их bindings
5. **Queues** — очереди и их статистика
6. **Admin** — управление пользователями и правами

### Мониторинг очередей

Проверьте следующие метрики:

- **Message rate** — скорость обработки сообщений
- **Queue length** — количество сообщений в очереди
- **Consumer count** — количество активных consumers
- **Memory usage** — использование памяти

### API RabbitMQ

RabbitMQ предоставляет Management API:

```bash
# Список очередей
curl -u guest:guest http://localhost:15672/api/queues

# Информация о конкретной очереди
curl -u guest:guest http://localhost:15672/api/queues/%2F/default

# Статистика
curl -u guest:guest http://localhost:15672/api/overview
```

## Мониторинг базы данных

### Подключение к PostgreSQL

```bash
# Через Docker
docker compose exec postgres psql -U postgres -d production_control

# Локально
psql -h localhost -U postgres -d production_control
```

### Полезные запросы

```sql
-- Размер базы данных
SELECT pg_size_pretty(pg_database_size('production_control'));

-- Размер таблиц
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Активные соединения
SELECT count(*) FROM pg_stat_activity;

-- Медленные запросы (требует настройки pg_stat_statements)
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Мониторинг через pgAdmin

Для визуального мониторинга используйте pgAdmin или другие инструменты:

```bash
# Запуск pgAdmin в Docker
docker run -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@example.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  dpage/pgadmin4
```

## Метрики и алерты

### Ключевые метрики для мониторинга

1. **API метрики**
   - Время ответа endpoints
   - Количество запросов в секунду
   - Количество ошибок (4xx, 5xx)

2. **База данных**
   - Количество соединений
   - Размер БД
   - Время выполнения запросов
   - Количество транзакций

3. **Celery**
   - Количество задач в очереди
   - Время выполнения задач
   - Количество успешных/неуспешных задач
   - Количество активных воркеров

4. **Инфраструктура**
   - Использование CPU
   - Использование памяти
   - Использование диска
   - Сетевая активность

### Настройка алертов

Пример конфигурации для Prometheus Alertmanager:

```yaml
groups:
  - name: production_control
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: CeleryQueueBacklog
        expr: celery_queue_length > 1000
        for: 10m
        annotations:
          summary: "Celery queue backlog is high"
      
      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends > 80
        for: 5m
        annotations:
          summary: "High number of database connections"
```

### Интеграция с внешними системами

#### Prometheus

Если добавлен Prometheus exporter:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'production-control'
    static_configs:
      - targets: ['localhost:8000']
```

#### Grafana

Создайте дашборды для визуализации метрик:

- API метрики (requests, latency, errors)
- Celery метрики (tasks, workers, queues)
- База данных (connections, queries, size)
- Инфраструктура (CPU, memory, disk)

#### Sentry

Для отслеживания ошибок в production:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

## Лучшие практики

1. **Логируйте важные события** — создание/обновление/удаление сущностей
2. **Используйте структурированное логирование** — добавляйте контекст (ID, параметры)
3. **Мониторьте ключевые метрики** — время ответа, ошибки, очереди
4. **Настройте алерты** — для критических метрик
5. **Регулярно проверяйте логи** — для выявления проблем
6. **Храните логи** — используйте централизованное хранение (ELK, Loki)
7. **Ротация логов** — настройте автоматическую ротацию

## Дополнительная информация

- [Установка и настройка](INSTALLATION.md)
- [Конфигурация](CONFIGURATION.md)
- [Устранение неполадок](TROUBLESHOOTING.md)

