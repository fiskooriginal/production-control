# API Документация

Полное описание REST API Production Control.

## Содержание

- [Обзор](#обзор)
- [Базовый URL](#базовый-url)
- [Аутентификация](#аутентификация)
- [Формат ответов](#формат-ответов)
- [Пагинация](#пагинация)
- [Фильтрация и сортировка](#фильтрация-и-сортировка)
- [Endpoints](#endpoints)
- [Примеры использования](#примеры-использования)
- [Интерактивная документация](#интерактивная-документация)

## Обзор

Production Control предоставляет REST API для управления производством, партиями, продуктами, рабочими центрами, вебхуками и аналитикой.

API следует принципам REST и использует стандартные HTTP методы и коды статусов.

## Базовый URL

```
http://localhost:8000/api
```

В production окружении базовый URL будет отличаться.

## Аутентификация

В текущей версии API не требует аутентификации. В production рекомендуется добавить аутентификацию (JWT, OAuth2, API ключи).

## Формат ответов

### Успешный ответ

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Пример",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Ошибка

```json
{
  "detail": "Описание ошибки"
}
```

### Список с пагинацией

```json
{
  "items": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

## Пагинация

Большинство endpoints для списков поддерживают пагинацию через query параметры:

- `limit` — количество элементов на странице (по умолчанию: 20, максимум: 100)
- `offset` — смещение для пагинации (по умолчанию: 0)

**Пример:**

```bash
GET /api/batches?limit=10&offset=20
```

## Фильтрация и сортировка

Многие endpoints поддерживают фильтрацию и сортировку. Подробности см. в описании конкретных endpoints в Swagger UI.

**Пример сортировки:**

```bash
GET /api/batches?sort_by=created_at&sort_order=desc
```

## Endpoints

### Healthcheck

#### Проверка статуса сервиса

```http
GET /api/healthcheck/service
```

**Ответ:**

```json
{
  "status": "ok"
}
```

#### Проверка подключения к БД

```http
GET /api/healthcheck/database
```

**Ответ:**

```json
{
  "status": "ok"
}
```

### Партии (Batches)

#### Создание партии

```http
POST /api/batches
```

**Тело запроса:**

```json
{
  "batch_number": "BATCH-2025-001",
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "planned_date": "2025-01-20",
  "description": "Описание партии"
}
```

**Ответ:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "batch_number": "BATCH-2025-001",
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "open",
  "planned_date": "2025-01-20",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Список партий

```http
GET /api/batches
```

**Query параметры:**

- `limit` — количество элементов (по умолчанию: 20)
- `offset` — смещение (по умолчанию: 0)
- `sort_by` — поле для сортировки
- `sort_order` — порядок сортировки (`asc` или `desc`)
- `batch_number` — фильтр по номеру партии
- `work_center_id` — фильтр по рабочему центру
- `status` — фильтр по статусу (`open`, `closed`)
- `planned_date_from` — фильтр по дате от
- `planned_date_to` — фильтр по дате до

**Ответ:** `200 OK`

```json
{
  "items": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

#### Получение партии по ID

```http
GET /api/batches/{batch_id}
```

**Ответ:** `200 OK`

#### Обновление партии

```http
PATCH /api/batches/{batch_id}
```

**Тело запроса:**

```json
{
  "planned_date": "2025-01-25",
  "description": "Обновленное описание"
}
```

**Ответ:** `200 OK`

#### Удаление партии

```http
DELETE /api/batches/{batch_id}
```

**Ответ:** `204 No Content`

#### Добавление продукта в партию

```http
POST /api/batches/{batch_id}/products
```

**Тело запроса:**

```json
{
  "unique_code": "PROD-001"
}
```

**Ответ:** `200 OK`

#### Удаление продукта из партии

```http
DELETE /api/batches/{batch_id}/products/{product_id}
```

**Ответ:** `200 OK`

**Важно:** Продукт будет полностью удален из БД, так как `batch_id` является обязательным полем.

#### Закрытие партии

```http
PATCH /api/batches/{batch_id}/close
```

**Тело запроса:**

```json
{
  "closed_date": "2025-01-20"
}
```

**Ответ:** `200 OK`

#### Агрегация партии

```http
POST /api/batches/{batch_id}/aggregate
```

**Тело запроса:**

```json
{
  "aggregation_date": "2025-01-20"
}
```

**Ответ:** `200 OK`

#### Агрегация партии (асинхронная задача)

```http
POST /api/batches/{batch_id}/aggregate/task
```

**Тело запроса:**

```json
{
  "aggregation_date": "2025-01-20"
}
```

**Ответ:** `202 Accepted`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Экспорт партий

```http
POST /api/batches/export
```

**Тело запроса:**

```json
{
  "format": "excel",
  "filters": {
    "status": "open"
  }
}
```

**Ответ:** `202 Accepted`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Импорт партий

```http
POST /api/batches/import
```

**Тело запроса:** `multipart/form-data`

- `file` — файл для импорта (Excel, CSV)
- `format` — формат файла (`excel`, `csv`)

**Ответ:** `202 Accepted`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Генерация отчета по партии

```http
POST /api/batches/{batch_id}/report
```

**Query параметры:**

- `format` — формат отчета (`pdf`, `excel`)

**Ответ:** `200 OK`

```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "format": "pdf",
  "download_url": "/api/reports/550e8400-e29b-41d4-a716-446655440000"
}
```

### Продукты (Products)

#### Список продуктов

```http
GET /api/products
```

**Query параметры:**

- `limit` — количество элементов
- `offset` — смещение
- `sort_by` — поле для сортировки
- `sort_order` — порядок сортировки

**Ответ:** `200 OK`

```json
{
  "items": [...],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

#### Получение продукта по ID

```http
GET /api/products/{product_id}
```

**Ответ:** `200 OK`

#### Агрегация продукта

```http
PATCH /api/products/{product_id}/aggregate
```

**Тело запроса:**

```json
{
  "aggregation_date": "2025-01-20"
}
```

**Ответ:** `200 OK`

### Рабочие центры (Work Centers)

#### Создание рабочего центра

```http
POST /api/work_centers
```

**Тело запроса:**

```json
{
  "name": "Цех №1",
  "code": "WC-001",
  "description": "Описание рабочего центра"
}
```

**Ответ:** `201 Created`

#### Список рабочих центров

```http
GET /api/work_centers
```

**Query параметры:**

- `limit` — количество элементов
- `offset` — смещение
- `sort_by` — поле для сортировки
- `sort_order` — порядок сортировки
- `name` — фильтр по имени
- `code` — фильтр по коду

**Ответ:** `200 OK`

#### Получение рабочего центра по ID

```http
GET /api/work_centers/{work_center_id}
```

**Ответ:** `200 OK`

#### Обновление рабочего центра

```http
PATCH /api/work_centers/{work_center_id}
```

**Тело запроса:**

```json
{
  "name": "Обновленное имя",
  "description": "Обновленное описание"
}
```

**Ответ:** `200 OK`

#### Удаление рабочего центра

```http
DELETE /api/work_centers/{work_center_id}
```

**Ответ:** `204 No Content`

### Вебхуки (Webhooks)

#### Создание подписки на вебхук

```http
POST /api/webhooks
```

**Тело запроса:**

```json
{
  "url": "https://example.com/webhook",
  "event_types": ["batch.created", "batch.closed"],
  "secret": "webhook_secret_key",
  "active": true
}
```

**Ответ:** `201 Created`

#### Список подписок

```http
GET /api/webhooks
```

**Query параметры:**

- `limit` — количество элементов
- `offset` — смещение
- `active` — фильтр по активности
- `event_type` — фильтр по типу события

**Ответ:** `200 OK`

#### Получение подписки по ID

```http
GET /api/webhooks/{subscription_id}
```

**Ответ:** `200 OK`

#### Удаление подписки

```http
DELETE /api/webhooks/{subscription_id}
```

**Ответ:** `204 No Content`

#### Список доставок для подписки

```http
GET /api/webhooks/{subscription_id}/deliveries
```

**Query параметры:**

- `limit` — количество элементов
- `offset` — смещение

**Ответ:** `200 OK`

### События (Events)

#### Список типов событий

```http
GET /api/events
```

**Ответ:** `200 OK`

```json
{
  "items": [
    {
      "name": "batch.created",
      "description": "Событие создания партии"
    },
    {
      "name": "batch.closed",
      "description": "Событие закрытия партии"
    }
  ]
}
```

### Аналитика (Analytics)

#### Статистика дашборда

```http
GET /api/analytics/dashboard
```

**Ответ:** `200 OK`

```json
{
  "total_batches": 100,
  "open_batches": 45,
  "closed_batches": 55,
  "total_products": 500,
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Примечание:** Статистика обновляется Celery Beat каждые 5 минут и берется из кэша.

### Фоновые задачи (Background Tasks)

#### Получение статуса задачи

```http
GET /api/background_tasks/{task_id}
```

**Ответ:** `200 OK`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "SUCCESS",
  "result": {
    "file_id": "550e8400-e29b-41d4-a716-446655440001",
    "download_url": "/api/reports/550e8400-e29b-41d4-a716-446655440001"
  }
}
```

**Статусы задач:**

- `PENDING` — задача в очереди
- `PROGRESS` — задача выполняется (содержит прогресс)
- `SUCCESS` — задача завершена успешно (содержит результат)
- `FAILURE` — задача завершена с ошибкой

## Примеры использования

### Создание партии и добавление продукта

```bash
# 1. Создание партии
curl -X POST http://localhost:8000/api/batches \
  -H "Content-Type: application/json" \
  -d '{
    "batch_number": "BATCH-2025-001",
    "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
    "planned_date": "2025-01-20"
  }'

# 2. Добавление продукта в партию
curl -X POST http://localhost:8000/api/batches/{batch_id}/products \
  -H "Content-Type: application/json" \
  -d '{
    "unique_code": "PROD-001"
  }'

# 3. Закрытие партии
curl -X PATCH http://localhost:8000/api/batches/{batch_id}/close \
  -H "Content-Type: application/json" \
  -d '{
    "closed_date": "2025-01-20"
  }'
```

### Экспорт партий с отслеживанием задачи

```bash
# 1. Запуск экспорта
RESPONSE=$(curl -X POST http://localhost:8000/api/batches/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "excel",
    "filters": {"status": "open"}
  }')

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')

# 2. Проверка статуса задачи
curl http://localhost:8000/api/background_tasks/$TASK_ID

# 3. Получение результата (когда статус SUCCESS)
RESULT=$(curl http://localhost:8000/api/background_tasks/$TASK_ID)
DOWNLOAD_URL=$(echo $RESULT | jq -r '.result.download_url')
```

### Работа с вебхуками

```bash
# 1. Создание подписки
curl -X POST http://localhost:8000/api/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "event_types": ["batch.created", "batch.closed"],
    "secret": "my_secret_key",
    "active": true
  }'

# 2. Просмотр доставок
curl http://localhost:8000/api/webhooks/{subscription_id}/deliveries
```

## Интерактивная документация

После запуска приложения доступна интерактивная документация:

- **Swagger UI**: <http://localhost:8000/docs>
  - Интерактивное тестирование API
  - Описание всех endpoints
  - Примеры запросов и ответов

- **ReDoc**: <http://localhost:8000/redoc>
  - Альтернативный формат документации
  - Удобное чтение

### Использование Swagger UI

1. Откройте <http://localhost:8000/docs>
2. Выберите нужный endpoint
3. Нажмите "Try it out"
4. Заполните параметры запроса
5. Нажмите "Execute"
6. Просмотрите ответ

## Коды статусов HTTP

- `200 OK` — успешный запрос
- `201 Created` — ресурс успешно создан
- `202 Accepted` — запрос принят для асинхронной обработки
- `204 No Content` — успешное удаление (без тела ответа)
- `400 Bad Request` — неверный запрос
- `404 Not Found` — ресурс не найден
- `422 Unprocessable Entity` — ошибка валидации
- `500 Internal Server Error` — внутренняя ошибка сервера

## Ограничения

- Максимальный размер файла для импорта: 10 MB
- Максимальное количество элементов на странице: 100
- Таймаут для синхронных операций: 30 секунд
- Асинхронные задачи хранят результаты в течение 24 часов

## Дополнительная информация

- [Установка и настройка](INSTALLATION.md)
- [Руководство по разработке](DEVELOPMENT.md)
- [Устранение неполадок](TROUBLESHOOTING.md)

