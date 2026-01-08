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
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
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
  "limit": 25,
  "offset": 0
}
```

## Пагинация

Большинство endpoints для списков поддерживают пагинацию через query параметры:

- `limit` — количество элементов на странице (по умолчанию: 25, минимум: 1, максимум: 100)
- `offset` — смещение для пагинации (по умолчанию: 0, минимум: 0)

**Пример:**

```bash
GET /api/batches?limit=10&offset=20
```

## Фильтрация и сортировка

Многие endpoints поддерживают фильтрацию и сортировку через query параметры:

- `sort_field` — поле для сортировки (по умолчанию: `created_at`)
- `sort_direction` — направление сортировки: `ASC` или `DESC` (по умолчанию: `DESC`)

**Пример сортировки:**

```bash
GET /api/batches?sort_field=created_at&sort_direction=DESC
```

## Endpoints

### Healthcheck

#### Проверка статуса сервиса

```http
GET /api/healthcheck/service
```

**Ответ:** `200 OK`

```json
{
  "status": "ok"
}
```

#### Проверка подключения к БД

```http
GET /api/healthcheck/database
```

**Ответ:** `200 OK`

**Успешный ответ:**

```json
{
  "status": "ok"
}
```

**Ответ при ошибке:**

```json
{
  "status": "error",
  "message": "Описание ошибки подключения к БД"
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
  "task_description": "Описание задания",
  "shift": "1",
  "team": "Бригада А",
  "batch_number": 1001,
  "batch_date": "2025-01-20",
  "nomenclature": "Номенклатура товара",
  "ekn_code": "EKN-001",
  "shift_start": "2025-01-20T08:00:00Z",
  "shift_end": "2025-01-20T20:00:00Z",
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Ответ:** `201 Created`

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": null,
  "is_closed": false,
  "closed_at": null,
  "task_description": "Описание задания",
  "shift": "1",
  "team": "Бригада А",
  "batch_number": 1001,
  "batch_date": "2025-01-20",
  "nomenclature": "Номенклатура товара",
  "ekn_code": "EKN-001",
  "shift_time_range": {
    "start": "2025-01-20T08:00:00Z",
    "end": "2025-01-20T20:00:00Z"
  },
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "products": []
}
```

#### Список партий

```http
GET /api/batches
```

**Query параметры:**

- `limit` — количество элементов (по умолчанию: 25, максимум: 100)
- `offset` — смещение (по умолчанию: 0)
- `sort_field` — поле для сортировки (по умолчанию: `created_at`)
- `sort_direction` — направление сортировки: `ASC` или `DESC` (по умолчанию: `DESC`)
- `is_closed` — фильтр по статусу закрытия (boolean)
- `batch_number` — фильтр по номеру партии (int, больше 0)
- `batch_date` — фильтр по дате партии (YYYY-MM-DD)
- `batch_date_from` — фильтр по начальной дате партии (YYYY-MM-DD)
- `batch_date_to` — фильтр по конечной дате партии (YYYY-MM-DD)
- `work_center_id` — фильтр по ID рабочего центра (UUID строка)
- `shift` — фильтр по смене

**Ответ:** `200 OK`

```json
{
  "items": [...],
  "total": 100,
  "limit": 25,
  "offset": 0
}
```

#### Получение партии по ID

```http
GET /api/batches/{batch_id}
```

**Параметры пути:**

- `batch_id` — UUID партии

**Ответ:** `200 OK`

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T11:00:00Z",
  "is_closed": false,
  "closed_at": null,
  "task_description": "Описание задания",
  "shift": "1",
  "team": "Бригада А",
  "batch_number": 1001,
  "batch_date": "2025-01-20",
  "nomenclature": "Номенклатура товара",
  "ekn_code": "EKN-001",
  "shift_time_range": {
    "start": "2025-01-20T08:00:00Z",
    "end": "2025-01-20T20:00:00Z"
  },
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "products": [
    {
      "uuid": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2025-01-15T10:35:00Z",
      "updated_at": null,
      "unique_code": "PROD-001",
      "batch_id": "550e8400-e29b-41d4-a716-446655440000",
      "is_aggregated": false,
      "aggregated_at": null
    }
  ]
}
```

#### Обновление партии

```http
PATCH /api/batches/{batch_id}
```

**Параметры пути:**

- `batch_id` — UUID партии

**Тело запроса (все поля опциональны):**

```json
{
  "task_description": "Обновленное описание задания",
  "shift": "2",
  "team": "Бригада Б",
  "batch_number": 1002,
  "batch_date": "2025-01-25",
  "nomenclature": "Обновленная номенклатура",
  "ekn_code": "EKN-002",
  "shift_start": "2025-01-25T08:00:00Z",
  "shift_end": "2025-01-25T20:00:00Z",
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_closed": false
}
```

**Ответ:** `200 OK`

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T11:00:00Z",
  "is_closed": false,
  "closed_at": null,
  "task_description": "Обновленное описание задания",
  "shift": "2",
  "team": "Бригада Б",
  "batch_number": 1002,
  "batch_date": "2025-01-25",
  "nomenclature": "Обновленная номенклатура",
  "ekn_code": "EKN-002",
  "shift_time_range": {
    "start": "2025-01-25T08:00:00Z",
    "end": "2025-01-25T20:00:00Z"
  },
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "products": []
}
```

#### Удаление партии

```http
DELETE /api/batches/{batch_id}
```

**Параметры пути:**

- `batch_id` — UUID партии

**Ответ:** `204 No Content`

**Важно:** Можно удалить только закрытую партию. Все связанные продукты будут автоматически удалены.

#### Добавление продукта в партию

```http
POST /api/batches/{batch_id}/products
```

**Параметры пути:**

- `batch_id` — UUID партии

**Тело запроса:**

```json
{
  "unique_code": "PROD-001"
}
```

**Ответ:** `200 OK`

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T11:00:00Z",
  "is_closed": false,
  "closed_at": null,
  "task_description": "Описание задания",
  "shift": "1",
  "team": "Бригада А",
  "batch_number": 1001,
  "batch_date": "2025-01-20",
  "nomenclature": "Номенклатура товара",
  "ekn_code": "EKN-001",
  "shift_time_range": {
    "start": "2025-01-20T08:00:00Z",
    "end": "2025-01-20T20:00:00Z"
  },
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "products": [
    {
      "uuid": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2025-01-15T11:00:00Z",
      "updated_at": null,
      "unique_code": "PROD-001",
      "batch_id": "550e8400-e29b-41d4-a716-446655440000",
      "is_aggregated": false,
      "aggregated_at": null
    }
  ]
}
```

#### Удаление продукта из партии

```http
DELETE /api/batches/{batch_id}/products/{product_id}
```

**Параметры пути:**

- `batch_id` — UUID партии
- `product_id` — UUID продукта

**Ответ:** `200 OK`

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T11:05:00Z",
  "is_closed": false,
  "closed_at": null,
  "task_description": "Описание задания",
  "shift": "1",
  "team": "Бригада А",
  "batch_number": 1001,
  "batch_date": "2025-01-20",
  "nomenclature": "Номенклатура товара",
  "ekn_code": "EKN-001",
  "shift_time_range": {
    "start": "2025-01-20T08:00:00Z",
    "end": "2025-01-20T20:00:00Z"
  },
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "products": []
}
```

**Важно:** Продукт будет полностью удален из БД, так как `batch_id` является обязательным полем.

#### Закрытие партии

```http
PATCH /api/batches/{batch_id}/close
```

**Параметры пути:**

- `batch_id` — UUID партии

**Тело запроса:**

```json
{
  "closed_at": "2025-01-20T20:00:00Z"
}
```

Поле `closed_at` опционально. Если не указано, используется текущее время.

**Ответ:** `200 OK`

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-20T20:00:00Z",
  "is_closed": true,
  "closed_at": "2025-01-20T20:00:00Z",
  "task_description": "Описание задания",
  "shift": "1",
  "team": "Бригада А",
  "batch_number": 1001,
  "batch_date": "2025-01-20",
  "nomenclature": "Номенклатура товара",
  "ekn_code": "EKN-001",
  "shift_time_range": {
    "start": "2025-01-20T08:00:00Z",
    "end": "2025-01-20T20:00:00Z"
  },
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "products": []
}
```

#### Агрегация партии

```http
PATCH /api/batches/{batch_id}/aggregate
```

**Параметры пути:**

- `batch_id` — UUID партии

**Тело запроса:**

```json
{
  "aggregated_at": "2025-01-20T18:00:00Z"
}
```

Поле `aggregated_at` опционально. Если не указано, используется текущее время.

**Ответ:** `202 Accepted`

```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-20T18:00:00Z",
  "is_closed": false,
  "closed_at": null,
  "task_description": "Описание задания",
  "shift": "1",
  "team": "Бригада А",
  "batch_number": 1001,
  "batch_date": "2025-01-20",
  "nomenclature": "Номенклатура товара",
  "ekn_code": "EKN-001",
  "shift_time_range": {
    "start": "2025-01-20T08:00:00Z",
    "end": "2025-01-20T20:00:00Z"
  },
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "products": []
}
```

#### Агрегация партии (асинхронная задача)

```http
PATCH /api/batches/{batch_id}/aggregate_async
```

**Параметры пути:**

- `batch_id` — UUID партии

**Тело запроса:**

```json
{
  "aggregated_at": "2025-01-20T18:00:00Z",
  "unique_codes": ["PROD-001", "PROD-002"]
}
```

Поля `aggregated_at` и `unique_codes` опциональны:

- Если `aggregated_at` не указано, используется текущее время
- Если `unique_codes` не указан, агрегируются все продукты партии
- Если `unique_codes` указан, агрегируются только указанные продукты

**Ответ:** `202 Accepted`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "message": "Aggregation task started"
}
```

#### Экспорт партий

```http
POST /api/batches/export
```

**Query параметры:**

- `format` — формат файла: `xlsx` или `csv` (обязательный)

**Тело запроса (опционально):**

```json
{
  "is_closed": false,
  "batch_number": 1001,
  "batch_date": "2025-01-20",
  "batch_date_from": "2025-01-01",
  "batch_date_to": "2025-01-31",
  "work_center_id": "550e8400-e29b-41d4-a716-446655440000",
  "shift": "1"
}
```

**Ответ:** `202 Accepted`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "message": "Export task started"
}
```

#### Импорт партий

```http
POST /api/batches/import
```

**Тело запроса:** `multipart/form-data`

- `file` — файл для импорта (xlsx или csv) (обязательный)
- `update_existing` — обновлять ли существующие партии (boolean, по умолчанию: false)

**Ответ:** `202 Accepted`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "message": "Import task started"
}
```

#### Генерация отчета по партии

```http
POST /api/batches/{batch_id}/reports/generate
```

**Параметры пути:**

- `batch_id` — UUID партии

**Query параметры:**

- `format` — формат отчета: `pdf` или `xlsx` (обязательный)
- `user_email` — Email адрес для отправки уведомления с отчетом (опциональный)

**Ответ:** `201 Created`

```json
{
  "report_path": "/reports/550e8400-e29b-41d4-a716-446655440000.pdf",
  "download_url": "/api/reports/550e8400-e29b-41d4-a716-446655440000"
}
```

### Продукты (Products)

#### Список продуктов

```http
GET /api/products
```

**Query параметры:**

- `limit` — количество элементов (по умолчанию: 25, максимум: 100)
- `offset` — смещение (по умолчанию: 0)
- `sort_field` — поле для сортировки (по умолчанию: `created_at`)
- `sort_direction` — направление сортировки: `ASC` или `DESC` (по умолчанию: `DESC`)

**Ответ:** `200 OK`

```json
{
  "items": [
    {
      "uuid": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2025-01-15T10:35:00Z",
      "updated_at": null,
      "unique_code": "PROD-001",
      "batch_id": "550e8400-e29b-41d4-a716-446655440000",
      "is_aggregated": false,
      "aggregated_at": null
    }
  ],
  "total": 50,
  "limit": 25,
  "offset": 0
}
```

#### Получение продукта по ID

```http
GET /api/products/{product_id}
```

**Параметры пути:**

- `product_id` — UUID продукта

**Ответ:** `200 OK`

```json
{
  "uuid": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2025-01-15T10:35:00Z",
  "updated_at": "2025-01-20T18:00:00Z",
  "unique_code": "PROD-001",
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_aggregated": true,
  "aggregated_at": "2025-01-20T18:00:00Z"
}
```

#### Агрегация продукта

```http
PATCH /api/products/{product_id}/aggregate
```

**Параметры пути:**

- `product_id` — UUID продукта

**Тело запроса:**

```json
{
  "aggregated_at": "2025-01-20T18:00:00Z"
}
```

Поле `aggregated_at` опционально. Если не указано, используется текущее время.

**Ответ:** `200 OK`

```json
{
  "uuid": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2025-01-15T10:35:00Z",
  "updated_at": "2025-01-20T18:00:00Z",
  "unique_code": "PROD-001",
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_aggregated": true,
  "aggregated_at": "2025-01-20T18:00:00Z"
}
```

### Рабочие центры (Work Centers)

#### Создание рабочего центра

```http
POST /api/work_centers
```

**Тело запроса:**

```json
{
  "identifier": "WC-001",
  "name": "Цех №1"
}
```

**Ответ:** `201 Created`

```json
{
  "uuid": "770e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": null,
  "identifier": "WC-001",
  "name": "Цех №1"
}
```

#### Список рабочих центров

```http
GET /api/work_centers
```

**Query параметры:**

- `limit` — количество элементов (по умолчанию: 25, максимум: 100)
- `offset` — смещение (по умолчанию: 0)
- `sort_field` — поле для сортировки (по умолчанию: `created_at`)
- `sort_direction` — направление сортировки: `ASC` или `DESC` (по умолчанию: `DESC`)
- `identifier` — фильтр по идентификатору

**Ответ:** `200 OK`

```json
{
  "items": [
    {
      "uuid": "770e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": null,
      "identifier": "WC-001",
      "name": "Цех №1"
    }
  ],
  "total": 10,
  "limit": 25,
  "offset": 0
}
```

#### Получение рабочего центра по ID

```http
GET /api/work_centers/{work_center_id}
```

**Параметры пути:**

- `work_center_id` — UUID рабочего центра

**Ответ:** `200 OK`

```json
{
  "uuid": "770e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T11:00:00Z",
  "identifier": "WC-001",
  "name": "Цех №1"
}
```

#### Обновление рабочего центра

```http
PATCH /api/work_centers/{work_center_id}
```

**Параметры пути:**

- `work_center_id` — UUID рабочего центра

**Тело запроса (все поля опциональны):**

```json
{
  "identifier": "WC-002",
  "name": "Обновленное имя"
}
```

**Ответ:** `200 OK`

```json
{
  "uuid": "770e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T11:00:00Z",
  "identifier": "WC-002",
  "name": "Обновленное имя"
}
```

#### Удаление рабочего центра

```http
DELETE /api/work_centers/{work_center_id}
```

**Параметры пути:**

- `work_center_id` — UUID рабочего центра

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
  "events": ["batch.created", "batch.closed"],
  "secret_key": "webhook_secret_key",
  "is_active": true,
  "retry_count": 3,
  "timeout": 10
}
```

**Возможные типы событий:**

- `batch.created` — партия создана
- `batch.closed` — партия закрыта
- `batch.opened` — партия открыта
- `batch.product_added` — продукт добавлен в партию
- `batch.product_removed` — продукт удален из партии
- `batch.aggregated` — партия агрегирована
- `batch.deleted` — партия удалена
- `batch.report_generated` — отчет по партии сгенерирован
- `product.aggregated` — продукт агрегирован
- `work_center.deleted` — рабочий центр удален
- `batch.import_completed` — импорт партий завершен

**Ответ:** `201 Created`

```json
{
  "uuid": "880e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": null,
  "url": "https://example.com/webhook",
  "events": ["batch.created", "batch.closed"],
  "is_active": true,
  "retry_count": 3,
  "timeout": 10
}
```

#### Список подписок

```http
GET /api/webhooks
```

**Query параметры:**

- `limit` — количество элементов (по умолчанию: 25, максимум: 100)
- `offset` — смещение (по умолчанию: 0)
- `event_type` — фильтр по типу события (один из типов событий)

**Ответ:** `200 OK`

```json
{
  "items": [
    {
      "uuid": "880e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": null,
      "url": "https://example.com/webhook",
      "events": ["batch.created", "batch.closed"],
      "is_active": true,
      "retry_count": 3,
      "timeout": 10
    }
  ],
  "total": 5,
  "limit": 25,
  "offset": 0
}
```

#### Получение подписки по ID

```http
GET /api/webhooks/{subscription_id}
```

**Параметры пути:**

- `subscription_id` — UUID подписки

**Ответ:** `200 OK`

```json
{
  "uuid": "880e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": null,
  "url": "https://example.com/webhook",
  "events": ["batch.created", "batch.closed"],
  "is_active": true,
  "retry_count": 3,
  "timeout": 10
}
```

#### Удаление подписки

```http
DELETE /api/webhooks/{subscription_id}
```

**Параметры пути:**

- `subscription_id` — UUID подписки

**Ответ:** `204 No Content`

#### Список доставок для подписки

```http
GET /api/webhooks/{subscription_id}/deliveries
```

**Параметры пути:**

- `subscription_id` — UUID подписки

**Query параметры:**

- `limit` — количество элементов (по умолчанию: 25, максимум: 100)
- `offset` — смещение (по умолчанию: 0)

**Ответ:** `200 OK`

```json
{
  "items": [
    {
      "uuid": "990e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-01-15T11:00:00Z",
      "updated_at": "2025-01-15T11:00:05Z",
      "subscription_id": "880e8400-e29b-41d4-a716-446655440000",
      "event_type": "batch.created",
      "payload": {
        "batch_id": "550e8400-e29b-41d4-a716-446655440000",
        "batch_number": 1001
      },
      "status": "success",
      "attempts": 1,
      "response_status": 200,
      "response_body": "OK",
      "error_message": null,
      "delivered_at": "2025-01-15T11:00:05Z"
    }
  ],
  "total": 10,
  "limit": 25,
  "offset": 0
}
```

**Возможные статусы доставки:**

- `pending` — доставка в ожидании
- `success` — доставка успешна
- `failed` — доставка неудачна

#### Тестовый эндпоинт для приема webhook

```http
POST /api/webhooks/test
```

**Query параметры:**

- `secret_key` — секретный ключ для проверки подписи (опциональный)

**Тело запроса:** произвольный JSON

**Ответ:** `200 OK`

```json
{
  "status": "received",
  "received_at": "2025-01-15T11:00:00Z",
  "event": "batch.created",
  "signature_valid": true,
  "headers": {
    "x-webhook-signature": "sha256=...",
    "x-webhook-event": "batch.created"
  },
  "payload": {
    "batch_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

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
      "uuid": "aa0e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": null,
      "name": "batch.created",
      "version": 1,
      "webhook_enabled": true,
      "description": "Событие создания партии"
    },
    {
      "uuid": "bb0e8400-e29b-41d4-a716-446655440001",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": null,
      "name": "batch.closed",
      "version": 1,
      "webhook_enabled": true,
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
  "active_batches": 45,
  "total_products": 500,
  "aggregated_products": 400,
  "aggregation_rate": 80.0,
  "cached_at": "2025-01-15T10:30:00Z"
}
```

**Примечание:** Статистика обновляется Celery Beat каждые 5 минут и берется из кэша.

### Фоновые задачи (Background Tasks)

#### Получение статуса задачи

```http
GET /api/background_tasks/{task_id}
```

**Параметры пути:**

- `task_id` — ID задачи (строка)

**Ответ:** `200 OK`

**Пример успешной задачи:**

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

**Пример задачи в процессе:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PROGRESS",
  "result": {
    "current": 50,
    "total": 100,
    "percent": 50
  }
}
```

**Пример задачи с ошибкой:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "FAILURE",
  "result": {
    "error": "Ошибка обработки файла"
  }
}
```

**Пример задачи в очереди:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "result": null
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
    "task_description": "Описание задания",
    "shift": "1",
    "team": "Бригада А",
    "batch_number": 1001,
    "batch_date": "2025-01-20",
    "nomenclature": "Номенклатура товара",
    "ekn_code": "EKN-001",
    "shift_start": "2025-01-20T08:00:00Z",
    "shift_end": "2025-01-20T20:00:00Z",
    "work_center_id": "550e8400-e29b-41d4-a716-446655440000"
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
    "closed_at": "2025-01-20T20:00:00Z"
  }'
```

### Экспорт партий с отслеживанием задачи

```bash
# 1. Запуск экспорта
RESPONSE=$(curl -X POST "http://localhost:8000/api/batches/export?format=xlsx" \
  -H "Content-Type: application/json" \
  -d '{
    "is_closed": false,
    "batch_date_from": "2025-01-01",
    "batch_date_to": "2025-01-31"
  }')

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')

# 2. Проверка статуса задачи
curl http://localhost:8000/api/background_tasks/$TASK_ID

# 3. Получение результата (когда статус SUCCESS)
RESULT=$(curl http://localhost:8000/api/background_tasks/$TASK_ID)
DOWNLOAD_URL=$(echo $RESULT | jq -r '.result.download_url')
```

### Импорт партий

```bash
# Запуск импорта с файлом
curl -X POST http://localhost:8000/api/batches/import \
  -F "file=@batches.xlsx" \
  -F "update_existing=false"
```

### Генерация отчета по партии

```bash
# Генерация PDF отчета
curl -X POST "http://localhost:8000/api/batches/{batch_id}/reports/generate?format=pdf&user_email=user@example.com"

# Генерация Excel отчета
curl -X POST "http://localhost:8000/api/batches/{batch_id}/reports/generate?format=xlsx"
```

### Агрегация партии (асинхронная)

```bash
# Агрегация всех продуктов партии
curl -X PATCH http://localhost:8000/api/batches/{batch_id}/aggregate_async \
  -H "Content-Type: application/json" \
  -d '{
    "aggregated_at": "2025-01-20T18:00:00Z"
  }'

# Агрегация только указанных продуктов
curl -X PATCH http://localhost:8000/api/batches/{batch_id}/aggregate_async \
  -H "Content-Type: application/json" \
  -d '{
    "aggregated_at": "2025-01-20T18:00:00Z",
    "unique_codes": ["PROD-001", "PROD-002"]
  }'
```

### Работа с вебхуками

```bash
# 1. Создание подписки
curl -X POST http://localhost:8000/api/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "events": ["batch.created", "batch.closed"],
    "secret_key": "my_secret_key",
    "is_active": true,
    "retry_count": 3,
    "timeout": 10
  }'

# 2. Просмотр доставок
curl http://localhost:8000/api/webhooks/{subscription_id}/deliveries?limit=10&offset=0

# 3. Тестирование webhook
curl -X POST "http://localhost:8000/api/webhooks/test?secret_key=my_secret_key" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: sha256=..." \
  -H "X-Webhook-Event: batch.created" \
  -d '{
    "batch_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
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
