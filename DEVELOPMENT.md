# 🛠️ Руководство по разработке

## 📋 Рабочий процесс с ветками

### 🌿 Создание новой ветки для задачи

```bash
# 1. Переключиться на main и обновить
git checkout main
git pull origin main

# 2. Создать новую ветку для задачи
git checkout -b feature/task-name
# или
git checkout -b bugfix/issue-name
# или  
git checkout -b docs/documentation-update
```

### 📝 Соглашения по названиям веток

| Префикс | Назначение | Пример |
|---------|------------|--------|
| `feature/` | Новая функциональность | `feature/add-biochemistry-tests` |
| `bugfix/` | Исправление ошибок | `bugfix/fix-age-validation` |
| `docs/` | Обновление документации | `docs/api-examples` |
| `refactor/` | Рефакторинг кода | `refactor/optimize-utils` |
| `test/` | Добавление тестов | `test/coverage-improvement` |

### 🔄 Завершение работы над задачей

```bash
# 1. Добавить изменения и создать коммит
git add .
git commit -m "feat: добавить поддержку биохимического анализа

- Добавлен новый справочник biochemistry.json
- Обновлены функции для работы с биохимией
- Добавлены тесты для новых функций"

# 2. Переключиться на main и влить изменения
git checkout main
git merge feature/task-name

# 3. Отправить в удаленный репозиторий
git push origin main

# 4. Удалить локальную ветку
git branch -d feature/task-name
```

### 📋 Соглашения по коммитам

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Типы коммитов:
feat:     # новая функциональность
fix:      # исправление ошибки
docs:     # изменения в документации
style:    # форматирование, отсутствующие точки с запятой и т.д.
refactor: # рефакторинг кода
test:     # добавление тестов
chore:    # изменения в процессе сборки или вспомогательных инструментах

# Примеры:
git commit -m "feat: добавить экспорт в Excel"
git commit -m "fix: исправить валидацию возраста"
git commit -m "docs: обновить примеры в README"
```

## 🎯 Идеи для будущих задач

### 📊 Новые справочники
- `feature/add-biochemistry-references` - биохимический анализ крови
- `feature/add-hormones-references` - гормональные исследования  
- `feature/add-coagulation-references` - коагулограмма
- `feature/add-immunology-references` - иммунологические тесты

### 🔧 Улучшения функциональности
- `feature/export-to-excel` - экспорт результатов в Excel
- `feature/multi-language-support` - поддержка нескольких языков
- `feature/units-conversion` - конвертация единиц измерения
- `feature/batch-processing` - пакетная обработка файлов

### 📖 Документация
- `docs/api-reference` - подробная документация API
- `docs/integration-examples` - примеры интеграции
- `docs/custom-references-guide` - руководство по созданию справочников

### 🧪 Тестирование
- `test/integration-tests` - интеграционные тесты
- `test/performance-tests` - тесты производительности
- `test/edge-cases` - тесты граничных случаев

## 🏷️ Управление версиями

### Alpha версии (0.x.xa)
- Активная разработка
- API может изменяться
- Подходит для тестирования

### Beta версии (0.x.xb)
- Стабилизация API
- Исправление багов
- Подготовка к релизу

### Stable версии (0.x.x)
- Стабильный API
- Готово к продакшену
- Семантическое версионирование

## 🚀 Быстрые команды

```bash
# Проверить статус
git status

# Посмотреть все ветки
git branch -a

# Создать и переключиться на новую ветку
git checkout -b feature/new-task

# Быстрый коммит
git add . && git commit -m "feat: описание изменений"

# Влить и очистить
git checkout main && git merge feature/task-name && git branch -d feature/task-name
```

---

**Помните**: Каждая задача должна решаться в отдельной ветке для поддержания чистоты истории и упрощения code review! 🎯
