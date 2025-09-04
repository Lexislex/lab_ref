# Использование пользовательских папок с референсами

Библиотека `lab_ref` поддерживает использование пользовательских папок с референсами вместо встроенных. Это позволяет:

- ✅ Модифицировать существующие референсы
- ✅ Добавлять новые биоматериалы
- ✅ Создавать собственные лабораторные исследования
- ✅ Адаптировать референсы под конкретные лаборатории

## 🎯 Способы использования

### 1. Глобальная установка папки

```python
import lab_ref

# Установить папку глобально для всех функций
lab_ref.set_references_dir("/path/to/my/references")

# Теперь все функции используют эту папку
biomaterials = lab_ref.list_biomaterials()
ref = lab_ref.get_biomaterial_reference("venous_blood", "hemoglobin", "male", 30)

# Сбросить к стандартной папке
lab_ref.reset_references_dir()
```

### 2. Переменная окружения

```python
import os
import lab_ref

# Установить через переменную окружения
os.environ["LAB_REF_DIR"] = "/path/to/my/references"

# Или в командной строке/скрипте:
# export LAB_REF_DIR="/path/to/my/references"
# python my_script.py
```

### 3. Явное указание в функциях

```python
import lab_ref

# Указать папку явно в каждой функции
biomaterials = lab_ref.list_biomaterials(references_dir="/path/to/my/references")
ref = lab_ref.get_biomaterial_reference(
    "venous_blood", "hemoglobin", "male", 30, 
    references_dir="/path/to/my/references"
)

# ООП API тоже поддерживает явное указание
manager = lab_ref.BiomaterialManager("venous_blood", references_dir="/path/to/my/references")
study_manager = lab_ref.LabStudyManager(references_dir="/path/to/my/references")
```

## 📋 Порядок приоритета

Библиотека определяет папку с референсами в следующем порядке:

1. **Явный параметр** `references_dir` в функции
2. **Переменная окружения** `LAB_REF_DIR`
3. **Стандартная папка** библиотеки

## 🔧 Создание пользовательских референсов

### Копирование шаблона

```python
import lab_ref

# Скопировать встроенные референсы как шаблон
copied_files = lab_ref.copy_references_template("./my_references")
print(f"Скопировано файлов: {len(copied_files)}")

# Установить пользовательскую папку
lab_ref.set_references_dir("./my_references")
```

### Структура файлов

После копирования шаблона вы получите:

```
my_references/
├── arterial_blood.json      # Артериальная кровь
├── capillary_blood.json     # Капиллярная кровь  
├── venous_blood.json        # Венозная кровь
├── urine.json              # Моча
└── lab_studies.json        # Определения исследований
```

### Модификация референсов

Вы можете модифицировать любой файл:

```python
import json

# Читаем существующий файл
with open("my_references/venous_blood.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Добавляем новый тест
data["my_custom_test"] = {
    "name_ru": "Мой тест",
    "test_code": "CUSTOM",
    "all": [
        {"age_min": 0, "age_max": 150, "min": 10, "max": 20, "unit": "units"}
    ]
}

# Записываем обратно
with open("my_references/venous_blood.json", 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## 💡 Практические примеры

### Пример 1: Локальные референсы лаборатории

```python
import lab_ref

# Настройка для конкретной лаборатории
lab_ref.copy_references_template("./lab_moscow_references")
lab_ref.set_references_dir("./lab_moscow_references")

# Теперь все анализы используют референсы московской лаборатории
result = lab_ref.check_biomaterial_value("venous_blood", "hemoglobin", 145, "male", 30)
```

### Пример 2: Временные референсы для исследования

```python
import lab_ref
import tempfile

# Создаем временные референсы для исследования
with tempfile.TemporaryDirectory() as temp_dir:
    lab_ref.copy_references_template(temp_dir)
    
    # Модифицируем референсы для исследования
    # ... изменяем файлы ...
    
    # Используем в анализе
    manager = lab_ref.LabStudyManager(references_dir=temp_dir)
    result = manager.create_study_result("blood_test", "venous_blood")
```

### Пример 3: Разные референсы для разных возрастных групп

```python
import lab_ref

# Педиатрические референсы
lab_ref.set_references_dir("./pediatric_references")
pediatric_result = lab_ref.check_biomaterial_value("capillary_blood", "hemoglobin", 110, "male", 5)

# Взрослые референсы  
lab_ref.set_references_dir("./adult_references")
adult_result = lab_ref.check_biomaterial_value("venous_blood", "hemoglobin", 150, "male", 30)
```

## 🛠️ Утилитные функции

```python
import lab_ref

# Получить текущую папку
current_dir = lab_ref.get_current_references_dir()
print(f"Используется папка: {current_dir}")

# Скопировать шаблон
copied = lab_ref.copy_references_template("./new_refs")
print(f"Скопировано: {', '.join(copied)}")

# Установить новую папку
lab_ref.set_references_dir("./new_refs")

# Сбросить к стандартной
lab_ref.reset_references_dir()
```

## ⚠️ Важные замечания

1. **Формат файлов**: Пользовательские файлы должны соответствовать тому же JSON формату, что и встроенные
2. **Валидация**: Библиотека автоматически валидирует структуру файлов при загрузке
3. **Кодировка**: Используйте UTF-8 для корректного отображения русских названий
4. **Обратная совместимость**: Старый API продолжает работать с пользовательскими папками

## 🔍 Отладка

Если что-то не работает:

```python
import lab_ref

# Проверьте текущую папку
print("Текущая папка:", lab_ref.get_current_references_dir())

# Проверьте доступные биоматериалы
print("Биоматериалы:", lab_ref.list_biomaterials())

# Проверьте доступные исследования
print("Исследования:", lab_ref.list_lab_studies())
```

Для подробных примеров см. `examples/custom_references_demo.py`.
