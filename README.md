# 🔬 lab_ref

> **Библиотека для работы с референсными значениями лабораторных исследований и утилитами для проверки результатов**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](https://en.wikipedia.org/wiki/Software_release_life_cycle#Alpha)

> ⚠️ **Статус проекта: Alpha** - Библиотека находится в стадии активной разработки. API может изменяться. Используйте с осторожностью в продакшене.

## ✨ Основные возможности

- 📊 **Получение референсных значений** с учетом пола и возраста пациентов
- ✅ **Проверка результатов анализов** на соответствие норме
- 📋 **Пакетная обработка** множественных показателей одновременно
- 🎨 **Красивые табличные отчеты** для визуального анализа
- 🔧 **Пользовательские справочники** через JSON файлы
- 🛡️ **Автоматическая валидация** структуры данных
- 🌍 **Поддержка метаданных** с русскими названиями

## 🚀 Быстрый старт

### Установка

```bash
# Рекомендуемый способ для разработки
pip install -e .

# Обычная установка
pip install lab_ref
```

### Простые примеры

```python
import lab_ref

# 🔍 Получить референсные значения для показателя
ref = lab_ref.get_reference("blood_test", "hemoglobin", sex="male", age=25)
print(ref)
# {'age_min': 18, 'age_max': 150, 'min': 130, 'max': 170, 'unit': 'g/L'}

# ✅ Проверить одно значение
status = lab_ref.check_value("blood_test", "hemoglobin", value=125, sex="male", age=25)
print(status)  # 'below' (ниже нормы)

# 📊 Проверить несколько показателей сразу
results = lab_ref.check_value(
    "blood_test",
    {"hemoglobin": 125, "leukocytes": 5.5},
    sex="male",
    age=25
)
print(results)
# {'hemoglobin': 'below', 'leukocytes': 'normal'}
```

## 📚 Подробное руководство

### 🔬 Работа с отдельными показателями

```python
import lab_ref

# Получение референса для конкретного показателя
ref = lab_ref.get_reference(
    test_type="blood_test",
    test_name="hemoglobin", 
    sex="female", 
    age=30
)

# Проверка значения
result = lab_ref.check_value(
    test_type="blood_test",
    test_name="hemoglobin",
    value=140,
    sex="female",
    age=30
)

print(f"Статус: {result}")  # 'normal', 'below' или 'above'
```

### 📋 Работа с множественными показателями

```python
# Данные анализа крови
blood_results = {
    "hemoglobin": 125,
    "leukocytes": 4.2,
    "platelets": 180
}

# Проверка всех показателей сразу
results = lab_ref.check_value(
    "blood_test", 
    blood_results, 
    sex="male", 
    age=35
)

# Анализ результатов
for test_name, status in results.items():
    if status != 'normal':
        print(f"⚠️ {test_name}: {status}")
    else:
        print(f"✅ {test_name}: в норме")
```

### 📊 Просмотр справочников

```python
# Список всех доступных типов исследований
available_tests = lab_ref.list_test_types()
print("Доступные исследования:", available_tests)

# Красивый отчет по всем справочникам
lab_ref.print_test_types_report()

# Подробная таблица по конкретному исследованию
lab_ref.print_reference_report("blood_test")

# Таблица показателей с русскими названиями
lab_ref.print_test_names_report("blood_test")

# Получить список ключей показателей
test_keys = lab_ref.get_test_keys("blood_test")
print("Показатели:", test_keys)
```

### 🔧 Пользовательские справочники

```python
# Использование собственной папки с JSON файлами
ref = lab_ref.get_reference(
    "my_test_type", 
    "my_parameter",
    sex="male", 
    age=25,
    references_dir="/path/to/my/references"
)

# Или через переменную окружения
import os
os.environ["LAB_REF_DIR"] = "/path/to/my/references"

# Теперь все функции будут использовать вашу папку
ref = lab_ref.get_reference("my_test_type", "my_parameter", sex="male", age=25)
```

## 📁 Структура проекта

```
lab_ref/
├── lab_ref/
│   ├── __init__.py              # Публичный API
│   ├── utils.py                 # Основная логика
│   └── references/              # Встроенные справочники
│       ├── __init__.py
│       └── blood_test.json      # Общий анализ крови
├── tests/
│   └── test_utils.py            # Тесты
├── pyproject.toml               # Конфигурация проекта
└── README.md                    # Документация
```

## 📊 Формат справочников

### Структура JSON файла

```json
{
  "_info": {
    "name": "Общий анализ крови",
    "description": "Справочник референсов для показателей общего анализа крови"
  },
  "hemoglobin": {
    "name_ru": "Гемоглобин",
    "male": [
      {"age_min": 0, "age_max": 1, "min": 110, "max": 140, "unit": "g/L"},
      {"age_min": 1, "age_max": 18, "min": 120, "max": 160, "unit": "g/L"},
      {"age_min": 18, "age_max": 150, "min": 130, "max": 170, "unit": "g/L"}
    ],
    "female": [
      {"age_min": 0, "age_max": 1, "min": 110, "max": 140, "unit": "g/L"},
      {"age_min": 1, "age_max": 18, "min": 115, "max": 155, "unit": "g/L"},
      {"age_min": 18, "age_max": 150, "min": 120, "max": 150, "unit": "g/L"}
    ]
  },
  "leukocytes": {
    "name_ru": "Лейкоциты",
    "all": [
      {"age_min": 0, "age_max": 1, "min": 6.0, "max": 18.0, "unit": "10^9/L"},
      {"age_min": 1, "age_max": 18, "min": 5.0, "max": 12.0, "unit": "10^9/L"},
      {"age_min": 18, "age_max": 150, "min": 4.0, "max": 9.0, "unit": "10^9/L"}
    ]
  }
}
```

### Возможные статусы

| Статус | Описание |
|--------|----------|
| `"below"` | Значение ниже нормы |
| `"normal"` | Значение в пределах нормы |
| `"above"` | Значение выше нормы |

## 🧪 Разработка и тестирование

> 📋 **Примечание**: Проект находится в alpha-статусе. Мы активно работаем над стабилизацией API и добавлением новых функций. Ваши отзывы и предложения приветствуются!

### Установка для разработки

```bash
# Клонирование репозитория
git clone https://github.com/Lexislex/lab_ref.git
cd lab_ref

# Создание виртуального окружения
python -m venv .venv
.venv\Scripts\activate  # Windows

# Установка в режиме разработки
pip install -e .

# Установка зависимостей для тестирования
pip install -e ".[test]"
```

### Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск с подробным выводом
pytest -v

# Запуск конкретного теста
pytest tests/test_utils.py::test_get_reference_hemoglobin_male_adult
```

### Проверка установки

```bash
python -c "import lab_ref; print('Version:', lab_ref.__version__)"
python -c "import lab_ref; lab_ref.print_test_types_report()"
```

## 💡 Практические примеры

### Анализ результатов пациента

```python
import lab_ref

def analyze_blood_test(patient_results, sex, age):
    """Анализ результатов общего анализа крови"""
    
    results = lab_ref.check_value("blood_test", patient_results, sex=sex, age=age)
    
    normal_count = sum(1 for status in results.values() if status == 'normal')
    total_count = len(results)
    
    print(f"📊 Анализ результатов:")
    print(f"   Всего показателей: {total_count}")
    print(f"   В норме: {normal_count}")
    print(f"   Отклонения: {total_count - normal_count}")
    print()
    
    for test_name, status in results.items():
        emoji = "✅" if status == "normal" else "⚠️"
        ref = lab_ref.get_reference("blood_test", test_name, sex=sex, age=age)
        value = patient_results[test_name]
        
        print(f"{emoji} {test_name}: {value} {ref['unit']} [{status}]")
        if status != "normal":
            print(f"   Норма: {ref['min']}-{ref['max']} {ref['unit']}")

# Пример использования
patient_data = {
    "hemoglobin": 95,   # пониженный
    "leukocytes": 5.2,  # нормальный
}

analyze_blood_test(patient_data, sex="female", age=28)
```

### Создание собственного справочника

```python
# my_references/custom_test.json
{
  "_info": {
    "name": "Мой анализ",
    "description": "Пользовательский справочник"
  },
  "my_parameter": {
    "name_ru": "Мой показатель",
    "all": [
      {"age_min": 18, "age_max": 100, "min": 10.0, "max": 20.0, "unit": "units"}
    ]
  }
}
```

```python
import lab_ref

# Использование пользовательского справочника
result = lab_ref.check_value(
    "custom_test", 
    "my_parameter", 
    value=15.5,
    age=30,
    references_dir="my_references"
)
print(f"Результат: {result}")  # 'normal'
```

## 🤝 Вклад в проект

Мы приветствуем любой вклад в развитие проекта:

1. 🍴 Сделайте форк репозитория
2. 🌿 Создайте ветку для новой функции
3. ✨ Внесите изменения и добавьте тесты
4. ✅ Убедитесь, что все тесты проходят
5. 📤 Создайте Pull Request

### Добавление новых справочников

Для добавления нового справочника:
- Создайте JSON файл в `lab_ref/references/`
- Следуйте существующему формату данных
- Добавьте блок `_info` с метаданными
- Добавьте соответствующие тесты

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

---

<div align="center">
  <b>Сделано с ❤️ для медицинского сообщества</b>
</div>