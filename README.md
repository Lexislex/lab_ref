# lab_ref

Библиотека для работы с референсными значениями лабораторных исследований и утилитами для проверки результатов.

## Возможности

### Основные функции
- 🔍 Получение референсных значений с учетом пола и возраста
- ✅ Проверка значений относительно нормы (одного или множественных показателей)
- 📊 Красивые отчеты и таблицы (аналог sklearn classification_report)
- 📁 Поддержка пользовательских JSON-файлов с референсами
- 🛡️ Автоматическая валидация структуры данных
- 📝 Метаданные справочников через ключ `_info`

### Два API для разных задач
- **Функциональный API** - для быстрых проверок и простых скриптов
- **ООП API** - для сложных сценариев и приложений с состоянием
- **Fluent Interface** - для удобных цепочек вызовов
- **Гибридный подход** - максимальная гибкость

## Два подхода к использованию

Библиотека предоставляет **гибридный подход**: функциональный API для простых случаев и ООП API для сложных сценариев.

### Функциональный API (для простых случаев)

```python
import lab_ref

# Быстрая проверка одного показателя
status = lab_ref.check_value("blood_test", "hemoglobin", 145, sex="male", age=30)
print(status)  # 'normal'

# Получение референса
ref = lab_ref.get_reference("blood_test", "hemoglobin", sex="male", age=30)
print(ref)  # {'min': 130, 'max': 170, 'unit': 'g/L', ...}

# Проверка нескольких показателей сразу
results = lab_ref.check_value(
    "blood_test",
    {"hemoglobin": 125, "leukocytes": 5.5},
    sex="male", age=30
)
print(results)  # {'hemoglobin': 'below', 'leukocytes': 'normal'}

# Отчеты и справочная информация
lab_ref.print_reference_report("blood_test")
lab_ref.print_test_types_report()
print(lab_ref.list_test_types())
```

### ООП API (для сложных сценариев)

```python
import lab_ref

# Создание менеджера референсов
manager = lab_ref.ReferenceManager("blood_test")
print(f"Справочник: {manager.name}")  # "Общий анализ крови"

# Работа с отдельным показателем
test = manager.create_test("hemoglobin", 145, sex="male", age=30)
print(f"Результат: {test}")  # "Гемоглобин: 145 g/L [normal]"
print(f"В норме: {test.is_normal()}")  # True

# Обработка результатов целого анализа
result = lab_ref.LabResult("blood_test", sex="male", age=35)
result.add_results({
    "hemoglobin": 120,  # пониженный
    "leukocytes": 6.5   # нормальный
})

print(f"Есть отклонения: {result.has_abnormalities()}")  # True
result.print_report()  # Красивый отчет с анализом

# Получение только отклонений
abnormal = result.get_abnormal_tests()
summary = result.get_summary()  # {'normal': 1, 'below': 1, 'above': 0, 'total': 2}
```

### Fluent Interface (цепочки вызовов)

```python
# Создание через цепочку вызовов
result = (lab_ref.LabResult("blood_test")
          .set_patient_info("female", 28)
          .add_result("hemoglobin", 110)
          .add_result("leukocytes", 4.5))

# Отдельный тест
test = (manager.create_test("hemoglobin")
        .set_value(160)
        .set_patient_info("female", 30))
```

### Когда что использовать?

**Функциональный API** → для быстрых проверок, простых скриптов, получения справочной информации

**ООП API** → для обработки множественных результатов, сложной бизнес-логики, приложений с состоянием

**Гибридный подход** → когда нужна максимальная гибкость

## Дополнительные возможности

```python
# Использование пользовательских JSON-файлов
ref = lab_ref.get_reference("blood_test", "hemoglobin", 
                           sex="male", age=25, references_dir="my_refs")

# Или через переменную окружения
import os
os.environ["LAB_REF_DIR"] = "my_refs"

# Получение списков и справочной информации
print(lab_ref.list_test_types())
lab_ref.print_test_names_report("blood_test")
print(lab_ref.get_test_keys("blood_test"))
```

## Примеры использования

Подробные примеры смотрите в папке [`examples/`](examples/):
- `hybrid_approach_demo.py` - полная демонстрация возможностей
- `README.md` - руководство по выбору подходящего API

## Установка

Рекомендуемый способ при разработке — editable-режим (из корня репозитория):

```bash
python -m pip install -e .
```

Это позволит IDE видеть актуальные docstrings и автодополнение.

Установка в обычном режиме (если вы используете опубликованный дистрибутив):

```bash
python -m pip install lab_ref
```

Если в проекте используется виртуальное окружение — убедитесь, что IDE выбрала тот же интерпретатор, куда установлен пакет.


### Установка из исходников (клонирование репозитория)

```bash
# Клонировать репозиторий
git clone https://github.com/Lexislex/lab_ref.git
cd lab_ref

# (опционально) создать и активировать виртуальное окружение
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell

# Установить пакет в editable-режиме
python -m pip install -e .

# Проверить установку
python -c "import lab_ref; print(lab_ref.__version__ if hasattr(lab_ref, '__version__') else 'installed')"
```


## Формат метаданных справочника

Каждый JSON может содержать верхнеуровневый блок `_info` с названием и описанием справочника. Эти данные используются в `print_reference_report` и `print_test_types_report`.

```json
{
  "_info": {
    "name": "Общий анализ крови",
    "description": "Справочник референсов для показателей общего анализа крови"
  },
  "hemoglobin": { ... },
  "leukocytes": { ... }
}
```
