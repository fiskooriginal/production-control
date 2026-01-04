# Руководство для разработчиков

Подробное руководство по разработке в проекте Production Control.

## Содержание

- [Начало работы](#начало-работы)
- [Структура проекта](#структура-проекта)
- [Архитектурные принципы](#архитектурные-принципы)
- [Добавление новой функциональности](#добавление-новой-функциональности)
- [Работа с Celery](#работа-с-celery)
- [Работа с миграциями](#работа-с-миграциями)
- [Тестирование](#тестирование)
- [Форматирование и линтинг](#форматирование-и-линтинг)
- [Git workflow](#git-workflow)
- [Полезные команды](#полезные-команды)

## Начало работы

### Настройка окружения разработки

1. Клонируйте репозиторий
2. Установите зависимости: `uv sync`
3. Настройте `.env` файл (см. [CONFIGURATION.md](CONFIGURATION.md))
4. Запустите инфраструктурные сервисы: `docker compose --profile app up -d postgres redis rabbitmq minio`
5. Примените миграции: `alembic upgrade head`
6. Запустите приложение: `uvicorn src.presentation.main:app --reload`

### Использование Dev Containers

Для быстрой настройки среды разработки используйте Dev Containers. Подробности см. в [DEVCONTAINERS.md](DEVCONTAINERS.md).

## Структура проекта

```
src/
├── core/                    # Общие настройки и утилиты
│   ├── config.py            # Конфигурация приложения
│   ├── database.py          # Настройка БД
│   ├── logging.py            # Настройка логирования
│   ├── settings.py           # Pydantic settings
│   └── time.py               # Утилиты для работы со временем
│
├── domain/                   # Доменный слой (Clean Architecture)
│   ├── batches/              # Доменная логика партий
│   │   ├── entities.py      # Сущности
│   │   ├── events/           # Доменные события
│   │   ├── interfaces/      # Интерфейсы репозиториев
│   │   ├── services/         # Доменные сервисы
│   │   └── value_objects/   # Value objects
│   ├── products/             # Доменная логика продуктов
│   ├── work_centers/         # Доменная логика рабочих центров
│   ├── webhooks/             # Доменная логика вебхуков
│
├── application/              # Слой приложения (Use Cases)
│   ├── batches/              # Use cases для партий
│   │   ├── commands/         # Команды (write operations)
│   │   ├── queries/          # Запросы (read operations)
│   │   ├── dtos/            # Data Transfer Objects
│   │   └── events/          # Обработчики событий
│   ├── products/             # Use cases для продуктов
│   ├── work_centers/         # Use cases для рабочих центров
│   ├── webhooks/             # Use cases для вебхуков
│   └── analytics/            # Аналитические запросы
│
├── infrastructure/           # Инфраструктурный слой
│   ├── persistence/          # Работа с БД
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── repositories/    # Реализация репозиториев
│   │   ├── mappers/         # Маппинг domain <-> persistence
│   │   └── migrations/      # Alembic миграции
│   ├── background_tasks/     # Celery задачи
│   │   ├── app.py           # Celery приложение
│   │   ├── beat_schedule.py  # Расписание периодических задач
│   │   └── tasks/           # Celery задачи
│   ├── events/               # Обработка событий
│   │   ├── registry.py      # Реестр событий
│   │   └── serializer.py    # Сериализация событий
│   ├── webhooks/             # Отправка вебхуков
│   └── common/               # Общие инфраструктурные компоненты
│
└── presentation/             # Слой представления (API)
    ├── api/                  # FastAPI endpoints
    │   ├── routes/          # Маршруты API
    │   ├── schemas/         # Pydantic схемы для API
    │   └── middleware/      # Middleware
    ├── di/                   # Dependency Injection
    └── mappers/              # Маппинг domain <-> API
```

## Архитектурные принципы

### Clean Architecture

Проект следует принципам Clean Architecture:

1. **Domain Layer** — не зависит ни от чего, содержит бизнес-логику
2. **Application Layer** — зависит только от Domain, содержит use cases
3. **Infrastructure Layer** — зависит от Domain и Application, реализует порты
4. **Presentation Layer** — зависит от всех слоев, предоставляет API

### CQRS

Разделение команд и запросов:

- **Commands** — операции записи, изменяющие состояние
- **Queries** — операции чтения, не изменяющие состояние

### Dependency Inversion

Все зависимости направлены внутрь к Domain слою:

```python
# Domain определяет интерфейс
class BatchRepositoryProtocol(Protocol):
    async def get_by_id(self, batch_id: UUID) -> BatchEntity: ...

# Infrastructure реализует интерфейс
class BatchRepository(BatchRepositoryProtocol):
    async def get_by_id(self, batch_id: UUID) -> BatchEntity:
        # реализация
```

### Domain Events

Используйте доменные события для слабой связанности:

```python
# В доменной сущности
class BatchEntity:
    def close(self, closed_date: date) -> None:
        self.status = BatchStatus.CLOSED
        self.closed_date = closed_date
        self.add_event(BatchClosedEvent(...))  # Доменное событие
```

## Добавление новой функциональности

### Пример: Добавление нового домена "Orders"

#### 1. Создание доменного слоя

```python
# src/domain/orders/entities.py
@dataclass(slots=True, kw_only=True)
class OrderEntity(BaseEntity):
    order_number: OrderNumber
    customer_id: UUID
    status: OrderStatus
    # ...
```

```python
# src/domain/orders/interfaces/repository.py
class OrderRepositoryProtocol(Protocol):
    async def get_by_id(self, order_id: UUID) -> OrderEntity: ...
    async def create(self, order: OrderEntity) -> None: ...
```

#### 2. Создание слоя приложения

```python
# src/application/orders/commands/create.py
@dataclass
class CreateOrderInputDTO:
    order_number: str
    customer_id: UUID

class CreateOrderCommand:
    def __init__(self, order_repo: OrderRepositoryProtocol, uow: UnitOfWorkProtocol):
        self._order_repo = order_repo
        self._uow = uow
    
    async def execute(self, dto: CreateOrderInputDTO) -> OrderEntity:
        order = OrderEntity(...)
        await self._order_repo.create(order)
        await self._uow.commit()
        return order
```

```python
# src/application/orders/queries/get.py
class GetOrderQuery:
    def __init__(self, order_repo: OrderRepositoryProtocol):
        self._order_repo = order_repo
    
    async def execute(self, order_id: UUID) -> OrderDTO:
        order = await self._order_repo.get_by_id(order_id)
        return order_to_dto(order)
```

#### 3. Создание инфраструктурного слоя

```python
# src/infrastructure/persistence/models/orders.py
class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(UUID, primary_key=True)
    order_number = Column(String, nullable=False)
    # ...
```

```python
# src/infrastructure/persistence/repositories/order.py
class OrderRepository(OrderRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, order_id: UUID) -> OrderEntity:
        model = await self._session.get(OrderModel, order_id)
        return order_model_to_entity(model)
```

#### 4. Создание слоя представления

```python
# src/presentation/api/schemas/orders.py
class CreateOrderRequest(BaseModel):
    order_number: str
    customer_id: UUID

class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    # ...
```

```python
# src/presentation/api/routes/orders.py
router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    command: create_order = Depends(get_create_order_command)
) -> OrderResponse:
    dto = CreateOrderInputDTO(...)
    order = await command.execute(dto)
    return order_to_response(order)
```

#### 5. Настройка Dependency Injection

```python
# src/presentation/di/orders.py
def get_create_order_command() -> CreateOrderCommand:
    session = get_session()
    order_repo = OrderRepository(session)
    uow = UnitOfWork(session)
    return CreateOrderCommand(order_repo, uow)
```

#### 6. Регистрация маршрута

```python
# src/presentation/main.py
from src.presentation.api.routes import orders

app.include_router(orders.router)
```

## Работа с Celery

### Добавление новой задачи Celery

#### 1. Создание задачи

```python
# src/infrastructure/background_tasks/tasks/orders.py
from src.infrastructure.background_tasks.app import celery_app

@celery_app.task(name="orders.process_order")
def process_order(order_id: str) -> dict:
    # ваша логика
    return {"status": "processed", "order_id": order_id}
```

#### 2. Регистрация задачи

```python
# src/infrastructure/background_tasks/tasks/__init__.py
from src.infrastructure.background_tasks.tasks.orders import process_order

__all__ = [..., "process_order"]
```

#### 3. Добавление в Celery app

```python
# src/infrastructure/background_tasks/app.py
celery_app = Celery(
    "production_control",
    include=[
        "src.infrastructure.background_tasks.tasks.outbox",
        "src.infrastructure.background_tasks.tasks.orders",  # добавить
    ],
)
```

### Добавление периодической задачи

```python
# src/infrastructure/background_tasks/beat_schedule.py
from celery.schedules import crontab

beat_schedule = {
    "process-pending-orders": {
        "task": "orders.process_pending_orders",
        "schedule": crontab(minute="*/5"),  # каждые 5 минут
    },
}
```

### Примеры расписаний

```python
# Каждый день в 01:00
crontab(hour=1, minute=0)

# Каждые 5 минут
crontab(minute="*/5")

# Каждые 3 часа
crontab(minute=0, hour="*/3")

# Каждый понедельник в 7:30
crontab(hour=7, minute=30, day_of_week=1)

# Первое число месяца в полночь
crontab(day_of_month="1", hour=0)

# Каждый чётный день месяца
crontab(day_of_month="2-30/2", hour=0)
```

### Просмотр зарегистрированных задач

```bash
# Список всех задач
docker compose exec celery_worker celery -A src.infrastructure.background_tasks.app:celery_app inspect registered

# Активные периодические задачи
docker compose exec celery_beat celery -A src.infrastructure.background_tasks.app:celery_app inspect scheduled
```

## Работа с миграциями

### Создание миграции

```bash
# Автоматическая генерация на основе изменений моделей
alembic revision --autogenerate -m "add orders table"

# Ручное создание пустой миграции
alembic revision -m "add orders table"
```

### Применение миграций

```bash
# Применить все миграции
alembic upgrade head

# Применить конкретную миграцию
alembic upgrade <revision_hash>

# Откатить последнюю миграцию
alembic downgrade -1

# Откатить до конкретной ревизии
alembic downgrade <revision_hash>
```

### Просмотр информации

```bash
# Текущая версия БД
alembic current

# История миграций
alembic history

# Детальная история
alembic history --verbose
```

### Важные замечания

1. **Всегда проверяйте автогенерированные миграции** перед применением
2. **Не редактируйте примененные миграции** — создавайте новые
3. **Тестируйте миграции** на тестовой БД перед production
4. **Используйте конкретные ревизии** вместо относительных (`-1`, `-10`)

## Тестирование

### Структура тестов

```
tests/
├── unit/              # Юнит-тесты
├── integration/      # Интеграционные тесты
└── e2e/              # End-to-end тесты
```

### Запуск тестов

```bash
# Все тесты
pytest

# Конкретный файл
pytest tests/unit/test_batches.py

# С покрытием
pytest --cov=src --cov-report=html
```

## Форматирование и линтинг

### Ruff

Проект использует Ruff для линтинга и форматирования.

```bash
# Проверка форматирования
ruff check .

# Автоматическое исправление
ruff check --fix .

# Форматирование кода
ruff format .
```

### Pre-commit хуки

```bash
# Установка хуков
pre-commit install

# Ручной запуск
pre-commit run --all-files
```

### Настройки Ruff

Настройки находятся в `pyproject.toml`:

```toml
[tool.ruff]
line-length = 120
target-version = "py313"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "TCH", "PTH", "RUF"]
```

## Git workflow

### Создание ветки

```bash
# От основной ветки
git checkout main
git pull
git checkout -b feature/add-orders
```

### Коммиты

Используйте понятные сообщения коммитов:

```bash
git commit -m "feat: add orders domain and API endpoints"
git commit -m "fix: correct order status validation"
git commit -m "docs: update API documentation for orders"
```

### Типы коммитов

- `feat:` — новая функциональность
- `fix:` — исправление бага
- `docs:` — изменения в документации
- `refactor:` — рефакторинг кода
- `test:` — добавление тестов
- `chore:` — обновление зависимостей, конфигурации

## Полезные команды

### Разработка

```bash
# Запуск API с hot-reload
uvicorn src.presentation.main:app --reload

# Запуск Celery worker
celery -A src.infrastructure.background_tasks.app:celery_app worker -l DEBUG

# Запуск Celery beat
celery -A src.infrastructure.background_tasks.app:celery_app beat -l DEBUG

# Запуск Flower
celery -A src.infrastructure.background_tasks.app:celery_app flower
```

### Docker

```bash
# Просмотр логов
docker compose logs -f app
docker compose logs -f celery_worker

# Перезапуск сервиса
docker compose restart app

# Выполнение команды в контейнере
docker compose exec app alembic upgrade head
```

### База данных

```bash
# Подключение к PostgreSQL
docker compose exec postgres psql -U postgres -d production_control

# Просмотр таблиц
\dt

# Просмотр структуры таблицы
\d batches
```

### Отладка

```bash
# Запуск с отладчиком
python -m debugpy --listen 0.0.0.0:5678 -m uvicorn src.presentation.main:app --reload

# Просмотр переменных окружения
docker compose exec app env | grep DB_
```

## Дополнительная информация

- [Архитектура проекта](ARCHITECTURE_ANALYSIS.md)
- [Архитектура событий](EVENTS_ARCHITECTURE.md)
- [Руководство по CQRS и запросам](CQRS_QUERY_GUIDELINES.md)
- [Правила инициализации](INIT_RULES.md)
- [API документация](API.md)

