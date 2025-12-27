# Правила организации __init__.py в проекте

## Основное правило

__`__init__.py` должен быть непустым ТОЛЬКО в подмодулях (на уровень ниже модулей) для реэкспорта.__

## Терминология

- __Модуль__ - директория первого уровня внутри пакета (например: `application/`, `batches/`, `products/`)
- __Подмодуль__ - директория второго уровня, когда мы разбиваем один файл на множество (например: `queries/`, `uow/`)

## Примеры

### ✅ Правильно

```
application/              # Модуль
├── __init__.py          # ПУСТОЙ
├── batches/             # Модуль
│   ├── __init__.py      # ПУСТОЙ
│   └── queries/         # Подмодуль (разбили queries на много файлов)
│       ├── __init__.py  # НЕПУСТОЙ - реэкспортирует все классы
│       ├── dtos.py
│       ├── filters.py
│       └── service.py
```

### ❌ Неправильно

```
application/              # Модуль
├── __init__.py          # НЕПУСТОЙ - ОШИБКА! Это модуль, не подмодуль
├── batches/             # Модуль
│   ├── __init__.py      # НЕПУСТОЙ - ОШИБКА! Это модуль, не подмодуль
│   └── queries/         # Подмодуль
│       └── __init__.py  # ПУСТОЙ - ОШИБКА! Это подмодуль, должен реэкспортировать
```

## Зачем это нужно?

### В подмодулях (НЕПУСТОЙ __init__.py)

Когда мы разбиваем один большой файл на несколько маленьких, `__init__.py` сохраняет интерфейс:

```python
# Вместо длинных импортов:
from src.application.batches.queries.dtos import BatchReadDTO
from src.application.batches.queries.filters import BatchReadFilters
from src.application.batches.queries.service import BatchQueryServiceProtocol

# Короткие и чистые:
from src.application.batches.queries import (
    BatchReadDTO,
    BatchReadFilters,
    BatchQueryServiceProtocol,
)
```

### В модулях (ПУСТОЙ __init__.py)

Модули должны иметь пустой `__init__.py`, чтобы:

- Не создавать лишнюю точку входа
- Сохранять явность импортов
- Избегать циклических зависимостей

## Текущая структура проекта

```
src/application/
├── __init__.py                      # ← ПУСТОЙ (модуль)
├── common/
│   └── __init__.py                  # ← ПУСТОЙ (модуль)
├── batches/
│   ├── __init__.py                  # ← ПУСТОЙ (модуль)
│   └── queries/
│       └── __init__.py              # ← НЕПУСТОЙ (подмодуль)
├── products/
│   ├── __init__.py                  # ← ПУСТОЙ (модуль)
│   └── queries/
│       └── __init__.py              # ← НЕПУСТОЙ (подмодуль)
├── work_centers/
│   ├── __init__.py                  # ← ПУСТОЙ (модуль)
│   └── queries/
│       └── __init__.py              # ← НЕПУСТОЙ (подмодуль)
├── events/
│   └── __init__.py                  # ← ПУСТОЙ (модуль)
└── uow/
    └── __init__.py                  # ← НЕПУСТОЙ (подмодуль)
```

## Проверка

Быстрая проверка правильности структуры:

```bash
find src/application -name "__init__.py" -exec sh -c 'lines=$(wc -l < "{}"); echo "{}: $lines строк"' \;
```

__Ожидаемый результат:__

- Модули (`application/`, `batches/`, `products/`, etc.) → 0 строк
- Подмодули (`queries/`, `uow/`) → > 0 строк
