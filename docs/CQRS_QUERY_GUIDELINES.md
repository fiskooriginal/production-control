# CQRS Query Side - Правила расширения и best practices

## Обзор архитектуры

В проекте реализован CQRS-подход для разделения операций чтения и записи:

### Write-side (Command)

- **Repositories** (domain protocols + infrastructure) - только `get_or_raise`, `create`, `update`, `delete`
- **Commands** - работают с репозиториями через UoW для транзакций
- **Доменные сущности** - полные агрегаты с бизнес-логикой и событиями

### Read-side (Query)

- **Query Objects** (application layer) - типизированные модели запросов
- **Query Handlers** (application layer) - бизнес-логика для чтения
- **Query Service Protocols** (application layer) - порты/интерфейсы
- **Query Services** (infrastructure layer) - SQLAlchemy реализации
- **Read DTOs** (application layer) - проекции данных без бизнес-логики

## Поток данных

### Read-side (GET /list, GET /id)

```
API Route → Query Params → Query Object → Query Handler → Query Service Protocol → SQLAlchemy Query Service → Database
                ↓                                                                              ↓
        Mapper (presentation)                                                         Mapper (infrastructure)
                                                                                                ↓
                                                                                           Read DTO
```

### Write-side (POST, PATCH, DELETE)

```
API Route → Request → Input DTO → Command → Repository (через UoW) → Database
                ↓                        ↓                    ↓
        Mapper (presentation)    Domain Logic      Domain Entity (полный агрегат)
```

## Ключевое разделение

### Repositories (write-only)

- `get_or_raise(uuid)` - **только для загрузки агрегата перед изменением** (update/delete/бизнес-операции)
- `create(entity)` - создание нового агрегата
- `update(entity)` - сохранение изменённого агрегата
- `delete(uuid)` - удаление агрегата
- Специфичные методы для бизнес-логики (например `get_by_batch_number`, `get_by_identifier`)

### Query Services (read-only)

- `get(uuid)` - получение проекции для отображения (возвращает ReadDTO)
- `list(query)` - получение списка проекций с фильтрацией/сортировкой/пагинацией

**Важно**: `get_or_raise` в репозиториях возвращает **полную доменную сущность** с бизнес-логикой, а `get` в query service возвращает **ReadDTO** без методов.

## Правила добавления новых фильтров

### 1. Добавить поле в Read Filters (application layer)

**Файл**: `src/application/queries/{entity}.py`

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class BatchReadFilters:
    is_closed: bool | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    work_center_id: UUID | None = None
    shift: str | None = None
    # НОВЫЙ ФИЛЬТР:
    team: str | None = None  # добавляем новое поле
```

**Важно**:

- Всегда используйте `| None` для опциональных фильтров
- Используйте доменные типы (UUID, date, etc.), а не строки
- Не используйте `dict[str, Any]` - только строго типизированные поля

### 2. Обновить Query Service (infrastructure layer)

**Файл**: `src/infrastructure/persistence/query_services/{entity}.py`

В методе `_apply_filters` добавьте обработку нового фильтра:

```python
def _apply_filters(self, stmt, count_stmt, filters):
    """Применяет фильтры к запросу"""
    from src.application.queries.batches import BatchReadFilters

    if not isinstance(filters, BatchReadFilters):
        raise ValueError("filters должен быть типа BatchReadFilters")

    # ... существующие фильтры ...

    # НОВЫЙ ФИЛЬТР:
    if filters.team is not None:
        stmt = stmt.where(Batch.team == filters.team)
        count_stmt = count_stmt.where(Batch.team == filters.team)

    return stmt, count_stmt
```

**Важно**:

- Применяйте фильтр И к `stmt`, И к `count_stmt` (иначе total будет неверным)
- Используйте whitelist подход - проверяйте каждое поле явно
- НЕ используйте `getattr(Model, field_name)` с произвольными строками

### 3. Обновить API схемы (presentation layer)

**Файл**: `src/presentation/api/schemas/{entity}.py`

```python
class BatchFiltersParams(BaseModel):
    """Query параметры для фильтрации партий"""

    is_closed: Annotated[bool | None, Query(description="Фильтр по статусу закрытия")] = None
    batch_number: Annotated[int | None, Query(gt=0, description="Фильтр по номеру партии")] = None
    # ... существующие поля ...
    # НОВЫЙ ФИЛЬТР:
    team: Annotated[str | None, Query(description="Фильтр по бригаде")] = None
```

### 4. Обновить mapper presentation → application (presentation layer)

**Файл**: `src/presentation/mappers/query_params.py`

```python
def batch_filters_params_to_query(params: BatchFiltersParams) -> BatchReadFilters | None:
    """Конвертирует BatchFiltersParams в BatchReadFilters"""
    try:
        filter_dict = {}

        # ... существующие поля ...

        # НОВЫЙ ФИЛЬТР:
        if params.team:
            filter_dict["team"] = params.team

        return BatchReadFilters(**filter_dict) if filter_dict else None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации BatchFiltersParams: {e}") from e
```

## Правила добавления новых полей сортировки

### 1. Добавить поле в SortField enum (application layer)

**Файл**: `src/application/queries/{entity}.py`

```python
class BatchSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    BATCH_NUMBER = "batch_number"
    # ... существующие поля ...
    # НОВОЕ ПОЛЕ:
    TEAM = "team"
```

**Важно**:

- Используйте snake_case для значений enum (соответствует колонкам БД)
- Enum = whitelist разрешённых полей сортировки

### 2. Обновить SORT_FIELD_MAPPING в Query Service (infrastructure layer)

**Файл**: `src/infrastructure/persistence/query_services/{entity}.py`

```python
class BatchQueryService(BatchQueryServiceProtocol):
    SORT_FIELD_MAPPING: ClassVar = {
        BatchSortField.CREATED_AT: Batch.created_at,
        BatchSortField.UPDATED_AT: Batch.updated_at,
        BatchSortField.BATCH_NUMBER: Batch.batch_number,
        # ... существующие поля ...
        # НОВОЕ ПОЛЕ:
        BatchSortField.TEAM: Batch.team,
    }
```

**Важно**:

- Используйте `ClassVar` аннотацию
- Маппинг должен быть словарём enum → SQLAlchemy column
- НЕ используйте `getattr(Model, field_name)` динамически

## Правила добавления новых полей в Read DTO

### 1. Обновить Read DTO (application layer)

**Файл**: `src/application/queries/{entity}.py`

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class BatchReadDTO:
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    # ... существующие поля ...
    # НОВОЕ ПОЛЕ:
    notes: str | None
```

### 2. Обновить маппер в Query Service (infrastructure layer)

**Файл**: `src/infrastructure/persistence/query_services/{entity}.py`

```python
@staticmethod
def _to_dto(model: Batch) -> BatchReadDTO:
    """Преобразует модель SQLAlchemy в DTO"""
    # ... существующий код ...
    return BatchReadDTO(
        uuid=model.uuid,
        # ... существующие поля ...
        # НОВОЕ ПОЛЕ:
        notes=model.notes,
    )
```

### 3. Обновить Response mapper (presentation layer)

**Файл**: `src/presentation/mappers/query_responses.py`

```python
def batch_read_dto_to_response(dto: BatchReadDTO) -> BatchResponse:
    """Конвертирует BatchReadDTO в BatchResponse"""
    # ... существующий код ...
    return BatchResponse(
        uuid=dto.uuid,
        # ... существующие поля ...
        # НОВОЕ ПОЛЕ:
        notes=dto.notes,
    )
```

### 4. Обновить API схему (presentation layer)

**Файл**: `src/presentation/api/schemas/{entity}.py`

```python
class BatchResponse(UUIDSchema, TimestampSchema, BaseModel):
    """Response schema для партии"""
    # ... существующие поля ...
    # НОВОЕ ПОЛЕ:
    notes: str | None = Field(None, description="Примечания")
```

## Запрещённые практики

### ❌ НЕ используйте dict для фильтров в публичных API

```python
# ПЛОХО
async def list(self, filters: dict[str, Any]) -> QueryResult[T]:
    ...

# ХОРОШО
async def list(self, query: ListBatchesQuery) -> QueryResult[BatchReadDTO]:
    ...
```

### ❌ НЕ используйте getattr с произвольными строками

```python
# ПЛОХО
column = getattr(Batch, sort_field)

# ХОРОШО
column = self.SORT_FIELD_MAPPING.get(sort.field)
if column is None:
    raise ValueError(f"Неизвестное поле сортировки: {sort.field}")
```

### ❌ НЕ дублируйте where-условия для count

```python
# ПЛОХО - дублирование логики
stmt = select(Batch).where(Batch.is_closed == True)
count_stmt = select(func.count()).select_from(Batch).where(Batch.is_closed == True)

# ХОРОШО - переиспользование stmt
stmt = select(Batch)
count_stmt = select(Batch)
if filters.is_closed is not None:
    stmt = stmt.where(Batch.is_closed == filters.is_closed)
    count_stmt = count_stmt.where(Batch.is_closed == filters.is_closed)
# ...
total = await session.execute(select(func.count()).select_from(count_stmt.subquery()))
```

### ❌ НЕ возвращайте доменные сущности из Query Service

```python
# ПЛОХО - Query Service возвращает доменную сущность
async def list(self, query: ListBatchesQuery) -> QueryResult[BatchEntity]:
    ...

# ХОРОШО - Query Service возвращает Read DTO
async def list(self, query: ListBatchesQuery) -> QueryResult[BatchReadDTO]:
    ...
```

## Рекомендованные практики

### ✅ Используйте immutable dataclasses для Query Objects

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ListBatchesQuery:
    filters: BatchReadFilters | None = None
    pagination: PaginationSpec | None = None
    sort: BatchSortSpec | None = None
```

### ✅ Всегда валидируйте типы фильтров в Query Service

```python
def _apply_filters(self, stmt, count_stmt, filters):
    if not isinstance(filters, BatchReadFilters):
        raise ValueError("filters должен быть типа BatchReadFilters")
    # ...
```

### ✅ Используйте ClassVar для статических маппингов

```python
class BatchQueryService(BatchQueryServiceProtocol):
    SORT_FIELD_MAPPING: ClassVar = {
        BatchSortField.CREATED_AT: Batch.created_at,
        # ...
    }
```

### ✅ Создавайте отдельные DTO для вложенных сущностей

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ProductReadDTONested:  # для вложения в BatchReadDTO
    uuid: UUID
    unique_code: str
    # ...

@dataclass(frozen=True, slots=True, kw_only=True)
class BatchReadDTO:
    uuid: UUID
    products: list[ProductReadDTONested]  # вложенные продукты
```

## Расширение на новые сущности

Для добавления read-стороны для новой сущности:

1. Создайте Query Object модели в `src/application/queries/{entity}.py`:
   - `{Entity}ReadDTO`
   - `{Entity}ReadFilters` (если нужны фильтры)
   - `{Entity}SortField`
   - `{Entity}SortSpec`
   - `List{Entity}Query`

2. Создайте порт в `src/application/queries/ports.py`:
   - `{Entity}QueryServiceProtocol`

3. Создайте Query Handler в `src/application/{entity}/queries/handlers/{entity}.py`:
   - `List{Entity}QueryHandler`

4. Создайте SQLAlchemy Query Service в `src/infrastructure/persistence/query_services/{entity}.py`:
   - `{Entity}QueryService` с методом `list(query)` и `_to_dto(model)`

5. Подключите через DI в `src/presentation/api/dependencies.py`

6. Обновите presentation layer:
   - Добавьте filter params схему в `src/presentation/api/schemas/{entity}.py`
   - Добавьте mapper функции в `src/presentation/mappers/query_params.py`
   - Добавьте response mapper в `src/presentation/mappers/query_responses.py`
   - Обновите роут в `src/presentation/api/routes/{entity}.py`

## Контрольный чеклист при добавлении фильтра/сортировки

- [ ] Добавлено поле в `{Entity}ReadFilters` или `{Entity}SortField`
- [ ] Обновлён Query Service (`_apply_filters` или `SORT_FIELD_MAPPING`)
- [ ] Обновлена API схема (`{Entity}FiltersParams`)
- [ ] Обновлён mapper (presentation → application)
- [ ] Фильтр применяется и к `stmt`, и к `count_stmt`
- [ ] Маппинг сортировки через словарь, не `getattr`
- [ ] Нет `dict[str, Any]` в публичных сигнатурах
