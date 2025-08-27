# lab_ref

Библиотека для работы с референсными значениями лабораторных исследований и утилитами для проверки результатов.

## Возможности
- Получение данных о норме одного теста или исследования с учетом пола и возраста
- Проверка, входит ли значение показателя в границы нормы (одного или сразу нескольких показателей)
- Получение всех референсов по типу исследования (test_type)
- Красивый вывод всех референсов по test_type в виде таблицы (аналог sklearn classification_report)
- Получение списка всех доступных исследований (test_type)
- Печать перечня всех справочников с названиями и описаниями
- Печать таблицы ключей показателей с единицами измерения
- Использование пользовательских JSON-файлов с референсами (через параметр или переменную окружения)
- Автоматическая проверка структуры JSON-файлов с информативными ошибками
- Поддержка метаданных справочника через верхнеуровневый ключ `_info`

## Пример использования

```python
import lab_ref

# Получить референс для одного показателя
ref = lab_ref.get_reference("blood_test", "hemoglobin", sex="male", age=25)
print(ref)
# {'age_min': 18, 'age_max': 150, 'min': 130, 'max': 170, 'unit': 'g/L'}

# Проверить значение одного показателя
status = lab_ref.check_value("blood_test", "hemoglobin", value=125, sex="male", age=25)
print(status)
# 'below'

# Проверить значения сразу нескольких показателей
results = lab_ref.check_value(
    "blood_test",
    {"hemoglobin": 125, "leukocytes": 5.5},
    sex="male",
    age=25
)
print(results)
# {'hemoglobin': 'below', 'leukocytes': 'normal'}

# Получить все референсы по test_type
all_refs = lab_ref.get_reference("blood_test")
print(all_refs)

# Красивый вывод всех референсов по test_type
lab_ref.print_reference_report("blood_test")

# Получить список всех доступных исследований
print(lab_ref.list_test_types())

# Печать всех справочников (test_type) с названием и описанием
lab_ref.print_test_types_report()

# Таблица ключей показателей для конкретного справочника
lab_ref.print_test_names_report("blood_test")

# Получить список ключей показателей (test_name)
print(lab_ref.get_test_keys("blood_test"))

# Использовать пользовательскую папку с JSON-файлами
ref = lab_ref.get_reference("blood_test", "hemoglobin", sex="male", age=25, references_dir="my_refs")

# Или через переменную окружения
import os
os.environ["LAB_REF_DIR"] = "my_refs"
ref = lab_ref.get_reference("blood_test", "hemoglobin", sex="male", age=25)
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
