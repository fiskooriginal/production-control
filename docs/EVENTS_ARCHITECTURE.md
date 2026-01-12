# Архитектура событий

## Обзор

В системе реализована унифицированная архитектура управления событиями, которая обеспечивает:
- Типобезопасную регистрацию событий через `EventTypesEnum`
- Централизованное хранение метаданных событий в базе данных
- Автоматическую синхронизацию событий из кода в БД
- Референсную целостность между событиями и их использованием
- Поддержку вебхуков для всех событий

## Компоненты архитектуры

### 1. EventTypesEnum

**Расположение:** `src/domain/common/enums.py`

Единый enum для всех типов событий в системе. Заменяет строковые литералы и старый `WebhookEventType`.

```python
class EventTypesEnum(enum.Enum):
    BATCH_CREATED = "batch.created"
    BATCH_CLOSED = "batch.closed"
    # ... другие события
```

**Особенности:**
- Значения enum соответствуют именам событий (с точками, например `"batch.created"`)
- Все события по умолчанию пригодны для вебхуков
- Используется во всех слоях приложения

### 2. EventRegistry

**Расположение:** `src/infrastructure/events/registry.py`

Whitelist-реестр доменных событий для стабильной (де)сериализации. Использует `EventTypesEnum` вместо строк.

**Основные методы:**
- `register(event_type: EventTypesEnum, version: int, event_class: type[DomainEvent])` - регистрация события
- `get_event_class(event_name: str, version: int)` - получение класса события
- `get_event_metadata(event_class: type[DomainEvent])` - получение имени и версии события
- `get_all_registered()` - список всех зарегистрированных событий

**Пример регистрации:**
```python
EventRegistry.register(EventTypesEnum.BATCH_CREATED, 1, BatchCreatedEvent)
```

### 3. EventType (модель БД)

**Расположение:** `src/infrastructure/persistence/models/event_type.py`

Модель для хранения метаданных типов событий в базе данных.

**Поля:**
- `uuid` - уникальный идентификатор
- `name` - имя события (например, `"batch.created"`)
- `version` - версия события (по умолчанию 1)
- `webhook_enabled` - флаг доступности для вебхуков (по умолчанию `true`)
- `description` - описание события (опционально)
- `created_at`, `updated_at` - временные метки

**Индексы:**
- `idx_event_type_name` - на поле `name`
- `idx_event_type_version` - на поле `version`
- Уникальный индекс на `name`

### 4. EventTypeRepository

**Расположение:** `src/infrastructure/persistence/repositories/event_type.py`

Репозиторий для работы с типами событий в БД.

**Основные методы:**
- `get_by_name(name: str, version: int)` - получение по имени и версии
- `get_by_event_type(event_type: EventTypesEnum, version: int)` - получение по enum
- `get_or_create(name: str, version: int, webhook_enabled: bool)` - получение или создание
- `list(webhook_enabled: bool | None)` - список событий с фильтрацией
- `update_webhook_enabled(event_type_id: UUID, enabled: bool)` - обновление флага вебхука

### 5. EventTypeSyncService

**Расположение:** `src/infrastructure/events/sync_service.py`

Сервис автоматической синхронизации событий из `EventRegistry` в базу данных.

**Функциональность:**
- Синхронизирует все события из `EventRegistry` при старте приложения
- Создает новые события, если их нет в БД
- Устанавливает `webhook_enabled = true` по умолчанию
- Обновляет версии существующих событий при необходимости

**Использование:**
Сервис автоматически вызывается при старте приложения в `lifespan()` функции.

### 6. OutboxEvent

**Расположение:** `src/infrastructure/persistence/models/outbox_event.py`

Transactional Outbox для доменных событий с ссылкой на `EventType`.

**Связи:**
- `event_type_id` - внешний ключ на `event_types.uuid` (обязательное поле)
- `event_name` - строковое имя события (nullable, для обратной совместимости)
- `event_type` - relationship к `EventType`

**Особенности:**
- При создании `OutboxEvent` автоматически устанавливается `event_type_id` на основе `event_name`
- Поле `event_name` оставлено для обратной совместимости со старыми записями

### 7. WebhookDelivery

**Расположение:** `src/infrastructure/persistence/models/webhook.py`

Модель доставки вебхука с ссылкой на `EventType`.

**Связи:**
- `event_type_id` - внешний ключ на `event_types.uuid` (обязательное поле)
- `event_type` - enum `EventTypesEnum` (nullable, для обратной совместимости)
- `event_type` - relationship к `EventType`

**Особенности:**
- При создании `WebhookDelivery` автоматически устанавливается `event_type_id` на основе `event_type` enum
- Поле `event_type` оставлено для обратной совместимости

## Поток данных

### Регистрация и синхронизация событий

```
1. Разработчик добавляет новое событие в EventTypesEnum
2. Создает доменный класс события (наследник DomainEvent)
3. Регистрирует событие в EventRegistry
4. При старте приложения EventTypeSyncService синхронизирует события в БД
5. Новое событие автоматически появляется в таблице event_types
```

### Создание и обработка событий

```
1. Доменная сущность создает DomainEvent
2. EventSerializer сериализует событие с использованием EventTypesEnum
3. OutboxEvent создается с автоматической установкой event_type_id
4. Событие сохраняется в outbox_events
5. Воркер обрабатывает события из outbox
6. Для вебхуков: событие преобразуется в EventTypesEnum и создается WebhookDelivery
```

### Получение списка событий

```
GET /api/events?webhook_enabled=true
    ↓
EventsRouter → ListEventsQuery → EventQueryService → EventTypeRepository
    ↓
Список EventType из БД
```

## Добавление нового события

### Шаг 1: Добавить в EventTypesEnum

Откройте `src/domain/common/enums.py` и добавьте новое значение:

```python
class EventTypesEnum(enum.Enum):
    # ... существующие события
    NEW_EVENT = "new.event"  # Используйте формат "module.action"
```

**Правила именования:**
- Используйте формат `"module.action"` (например, `"batch.created"`, `"product.aggregated"`)
- Имя enum должно быть в UPPER_SNAKE_CASE (например, `NEW_EVENT`)
- Значение должно быть в lowercase с точками (например, `"new.event"`)

### Шаг 2: Создать доменный класс события

Создайте файл в соответствующем доменном модуле, например `src/domain/module/events/new_event.py`:

```python
from dataclasses import dataclass
from uuid import UUID

from src.domain.common.events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class NewEvent(DomainEvent):
    """Событие создания нового объекта"""
    
    # Добавьте необходимые поля
    field1: str
    field2: UUID
    # ...
```

**Требования:**
- Класс должен наследоваться от `DomainEvent`
- Класс должен быть `@dataclass(frozen=True)`
- Используйте `kw_only=True` для явного указания аргументов
- Обязательное поле `aggregate_id: UUID` наследуется от `DomainEvent`

### Шаг 3: Зарегистрировать в EventRegistry

Откройте `src/infrastructure/events/registry.py` и добавьте регистрацию:

```python
from src.domain.module.events.new_event import NewEvent

def _initialize_registry() -> None:
    # ... существующие регистрации
    EventRegistry.register(EventTypesEnum.NEW_EVENT, 1, NewEvent)
```

**Важно:**
- Версия события начинается с `1`
- При изменении структуры события создайте новую версию (например, `2`)
- Старые версии должны оставаться в реестре для обратной совместимости

### Шаг 4: Экспортировать событие

Добавьте импорт в `__init__.py` модуля событий, например `src/domain/module/events/__init__.py`:

```python
from src.domain.module.events.new_event import NewEvent

__all__ = [
    # ... существующие события
    "NewEvent",
]
```

### Шаг 5: Использовать в доменной логике

В доменной сущности создайте и добавьте событие:

```python
from src.domain.module.events.new_event import NewEvent

class MyEntity(BaseEntity):
    def do_something(self) -> None:
        # Бизнес-логика
        # ...
        
        # Создание события
        event = NewEvent(
            aggregate_id=self.uuid,
            field1="value1",
            field2=some_uuid,
        )
        self.add_domain_event(event)
```

### Шаг 6: Проверить синхронизацию

При следующем запуске приложения:
1. `EventTypeSyncService` автоматически обнаружит новое событие в `EventRegistry`
2. Создаст запись в таблице `event_types` с `webhook_enabled=true`
3. Событие станет доступно через API `GET /api/events`

**Проверка:**
```bash
# После запуска приложения проверьте БД
SELECT * FROM event_types WHERE name = 'new.event';

# Или через API
curl http://localhost:8000/api/events?webhook_enabled=true
```

## Версионирование событий

### Когда создавать новую версию

Создавайте новую версию события, если:
- Изменяется структура события (добавление/удаление полей)
- Меняется семантика существующих полей
- Требуется обратная совместимость со старыми версиями

### Как создать новую версию

1. Создайте новый класс события с суффиксом версии:
   ```python
   @dataclass(frozen=True, kw_only=True)
   class NewEventV2(DomainEvent):
       # Новая структура
       ...
   ```

2. Зарегистрируйте новую версию:
   ```python
   EventRegistry.register(EventTypesEnum.NEW_EVENT, 2, NewEventV2)
   ```

3. Старая версия остается в реестре:
   ```python
   EventRegistry.register(EventTypesEnum.NEW_EVENT, 1, NewEvent)  # Старая
   EventRegistry.register(EventTypesEnum.NEW_EVENT, 2, NewEventV2)  # Новая
   ```

4. Обновите логику использования события в коде

## API для работы с событиями

### GET /api/events

Получение списка всех типов событий.

**Query параметры:**
- `webhook_enabled` (bool, optional) - фильтр по доступности для вебхуков

**Пример запроса:**
```bash
GET /api/events?webhook_enabled=true
```

**Пример ответа:**
```json
{
  "items": [
    {
      "uuid": "123e4567-e89b-12d3-a456-426614174000",
      "name": "batch.created",
      "version": 1,
      "webhook_enabled": true,
      "description": null,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 11,
  "limit": 100,
  "offset": 0
}
```

## Миграции базы данных

### Первичная миграция

Первичная миграция `67822cfb3d92` создает:
- Таблицу `event_types` с захардкоженными 11 событиями
- Колонку `event_type_id` в `outbox_events` с внешним ключом
- Колонку `event_type_id` в `webhook_deliveries` с внешним ключом

**Важно:** Новые события добавляются автоматически через `EventTypeSyncService`, миграции не требуются.

## Best Practices

### 1. Именование событий

- Используйте формат `"module.action"` (например, `"batch.created"`)
- Действие должно быть в прошедшем времени (например, `created`, `updated`, `deleted`)
- Избегайте слишком длинных имен

### 2. Структура событий

- События должны быть immutable (`frozen=True`)
- Включайте только необходимые данные
- Избегайте включения полных агрегатов в события

### 3. Регистрация событий

- Всегда регистрируйте события в `EventRegistry`
- Используйте `EventTypesEnum` вместо строк
- Начинайте версию с `1`

### 4. Обработка событий

- Используйте `event_type_id` для связи с `EventType`
- Не полагайтесь на `event_name` (оно для обратной совместимости)
- Все события по умолчанию пригодны для вебхуков

### 5. Тестирование

- Тестируйте создание событий в доменной логике
- Проверяйте регистрацию в `EventRegistry`
- Убедитесь, что события синхронизируются в БД

## Troubleshooting

### Событие не появляется в БД

1. Проверьте, что событие зарегистрировано в `EventRegistry`
2. Убедитесь, что `EventTypeSyncService` выполняется при старте
3. Проверьте логи приложения на наличие ошибок синхронизации

### Ошибка "Event not registered"

1. Убедитесь, что событие зарегистрировано в `EventRegistry`
2. Проверьте, что используется правильный `EventTypesEnum`
3. Проверьте версию события

### Событие не отправляется через вебхук

1. Проверьте, что `webhook_enabled = true` в БД
2. Убедитесь, что есть активные подписки на это событие
3. Проверьте логи обработки вебхуков

## Связанные документы

- [CQRS Query Guidelines](CQRS_QUERY_GUIDELINES.md) - правила работы с запросами
- [Domain Events](https://martinfowler.com/eaaDev/DomainEvent.html) - паттерн доменных событий
- [Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html) - паттерн транзакционного outbox

