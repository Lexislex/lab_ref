"""Утилиты для работы с референсами лабораторных тестов.

Функции этого модуля ре-экспортируются в `lab_ref.__init__`,
поэтому доступны как `lab_ref.get_reference`, `lab_ref.check_value`, и т.д.
"""

import json
import os

def validate_references_structure(data):
    """Проверяет структуру словаря с референсами.

    Parameters:
        data (dict): Загруженные из JSON референсы.

    Raises:
        ValueError: Если структура не соответствует ожидаемому формату.
    """
    if not isinstance(data, dict):
        raise ValueError("Reference file root must be a dictionary.")
    for test_name, test_ref in data.items():
        # Разрешаем служебный блок метаданных на верхнем уровне
        if test_name == "_info":
            if not isinstance(test_ref, dict):
                raise ValueError("_info must be a dictionary with metadata fields.")
            # Поля name/description опциональны, поэтому дополнительная строгая проверка не требуется
            continue
        if isinstance(test_ref, dict):
            for sex, sex_refs in test_ref.items():
                if sex in ["name_ru", "test_code"]:
                    continue
                if isinstance(sex_refs, list):
                    for r in sex_refs:
                        if not all(k in r for k in ("min", "max", "unit", "age_min", "age_max")):
                            raise ValueError(f"Missing keys in age range for '{test_name}'/{sex}: {r}")
                elif isinstance(sex_refs, dict):
                    if not all(k in sex_refs for k in ("min", "max", "unit")):
                        raise ValueError(f"Missing keys in dict for '{test_name}'/{sex}: {sex_refs}")
                else:
                    raise ValueError(f"Invalid value for '{test_name}'/{sex}: {sex_refs}")
        elif isinstance(test_ref, list):
            for r in test_ref:
                if not all(k in r for k in ("min", "max", "unit", "age_min", "age_max")):
                    raise ValueError(f"Missing keys in age range for '{test_name}': {r}")
        elif isinstance(test_ref, dict):
            if not all(k in test_ref for k in ("min", "max", "unit")):
                raise ValueError(f"Missing keys in dict for '{test_name}': {test_ref}")
        else:
            raise ValueError(f"Invalid value for '{test_name}': {test_ref}")

def _get_references_dir(references_dir=None):
    """Возвращает путь к папке с референсами.

    Приоритет: явный параметр -> переменная окружения `LAB_REF_DIR` ->
    стандартная папка `lab_ref/references`.
    """
    if references_dir is not None:
        return references_dir
    env_dir = os.environ.get("LAB_REF_DIR")
    if env_dir:
        return env_dir
    return os.path.join(os.path.dirname(__file__), "references")


def set_references_dir(path):
    """Устанавливает пользовательскую папку с референсами через переменную окружения.
    
    Это глобально изменяет папку с референсами для всех последующих вызовов
    функций библиотеки, если они не указывают явно параметр references_dir.
    
    Parameters:
        path (str): Путь к папке с пользовательскими референсами.
        
    Example:
        import lab_ref
        lab_ref.set_references_dir("/path/to/my/references")
        # Теперь все функции будут использовать эту папку по умолчанию
    """
    os.environ["LAB_REF_DIR"] = str(path)


def get_current_references_dir():
    """Возвращает текущую папку с референсами.
    
    Returns:
        str: Путь к папке с референсами, которая будет использоваться по умолчанию.
    """
    return _get_references_dir()


def reset_references_dir():
    """Сбрасывает пользовательскую папку с референсами, возвращая к стандартной.
    
    Удаляет переменную окружения LAB_REF_DIR, после чего библиотека
    будет использовать встроенную папку с референсами.
    """
    if "LAB_REF_DIR" in os.environ:
        del os.environ["LAB_REF_DIR"]


def copy_references_template(destination_dir):
    """Копирует встроенные референсы в указанную папку как шаблон.
    
    Полезно для создания пользовательской копии референсов,
    которую можно затем модифицировать под свои нужды.
    
    Parameters:
        destination_dir (str): Папка, куда скопировать файлы референсов.
        
    Returns:
        list: Список скопированных файлов.
        
    Example:
        import lab_ref
        lab_ref.copy_references_template("./my_references")
        lab_ref.set_references_dir("./my_references")
    """
    import shutil
    
    # Получаем стандартную папку с референсами
    source_dir = os.path.join(os.path.dirname(__file__), "references")
    
    # Создаем папку назначения, если её нет
    os.makedirs(destination_dir, exist_ok=True)
    
    copied_files = []
    
    # Копируем все .json файлы
    for filename in os.listdir(source_dir):
        if filename.endswith('.json'):
            source_file = os.path.join(source_dir, filename)
            dest_file = os.path.join(destination_dir, filename)
            shutil.copy2(source_file, dest_file)
            copied_files.append(filename)
    
    return copied_files

def load_references(test_type, references_dir=None):
    """Загружает референсы из JSON по указанному типу исследования.

    Parameters:
        test_type (str): Имя файла без .json (например, "blood_test").
        references_dir (str | None): Путь к пользовательской папке с JSON.

    Returns:
        dict: Содержимое JSON после валидации структуры.
    """
    ref_dir = _get_references_dir(references_dir)
    path = os.path.join(ref_dir, f"{test_type}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    validate_references_structure(data)
    return data

def list_test_types(references_dir=None):
    """Возвращает список доступных типов исследований (имена JSON-файлов без расширения)."""
    ref_dir = _get_references_dir(references_dir)
    test_types = []
    for fname in os.listdir(ref_dir):
        if fname.endswith(".json"):
            test_types.append(os.path.splitext(fname)[0])
    return test_types

def get_reference(test_type, test_name=None, sex=None, age=None, references_dir=None):
    """Возвращает референс(ы) по параметрам.

    Если `test_name` не указан, возвращает все референсы по `test_type`.
    При наличии возрастных диапазонов необходимо передать `age`.

    Parameters:
        test_type (str): Тип исследования, например "blood_test".
        test_name (str | None): Ключ показателя в JSON.
        sex (str | None): "male" | "female" | "all" (если применимо).
        age (float | int | None): Возраст для выбора корректного диапазона.
        references_dir (str | None): Пользовательская папка с JSON.

    Returns:
        dict: Словарь с полями min, max, unit (и age_min/age_max при списке).

    Raises:
        ValueError: Если показатель не найден или нет подходящего возрастного диапазона.
    """
    refs = load_references(test_type, references_dir=references_dir)
    if test_name is None:
        return refs
    ref = refs.get(test_name)
    if not ref:
        raise ValueError(f"Test '{test_name}' not found in {test_type}")
    if sex and sex in ref:
        sex_refs = ref[sex]
    elif "all" in ref:
        sex_refs = ref["all"]
    else:
        sex_refs = ref

    # Если это список (есть возрастные диапазоны)
    if isinstance(sex_refs, list) and age is not None:
        for r in sex_refs:
            if r["age_min"] <= age < r["age_max"]:
                return r
        raise ValueError(f"No reference for age {age}")
    # Старый формат (dict)
    elif isinstance(sex_refs, dict):
        return sex_refs
    else:
        raise ValueError("Reference format error")

def check_value(test_type, test_name, value=None, sex=None, age=None, references_dir=None):
    """Сравнивает значение(я) с референсами и возвращает статус.

    Parameters:
        test_type (str): Тип исследования.
        test_name (str | dict): Имя показателя или mapping {name: value}.
        value (float | int | None): Значение показателя (игнорируется при dict в `test_name`).
        sex (str | None): Пол, если применимо.
        age (float | int | None): Возраст, если есть возрастные диапазоны.
        references_dir (str | None): Путь к папке с JSON.

    Returns:
        str | dict: "below" | "normal" | "above" для одного значения или
                    словарь name -> статус для нескольких значений.
    """
    # Если test_name - dict, то value игнорируется, а test_name - это mapping test_name: value
    if isinstance(test_name, dict):
        results = {}
        for tname, val in test_name.items():
            results[tname] = check_value(test_type, tname, val, sex=sex, age=age, references_dir=references_dir)
        return results
    # Обычный режим
    ref = get_reference(test_type, test_name, sex, age, references_dir=references_dir)
    if value < ref["min"]:
        return "below"
    elif value > ref["max"]:
        return "above"
    else:
        return "normal"

def print_reference_report(test_type, references_dir=None):
    """Печатает таблицу всех референсов по `test_type` для визуального просмотра."""
    refs = load_references(test_type, references_dir=references_dir)
    # Шапка с названием/описанием справочника, если есть
    meta = refs.get("_info", {}) if isinstance(refs, dict) else {}
    title = meta.get("name") or test_type
    description = meta.get("description")
    print(title)
    if description:
        print(description)
    header = f"{'Test Name':<12} | {'Sex':<7} | {'Age Range':<11} | {'Min':<6} | {'Max':<6} | {'Unit':<8}"
    print(header)
    print('-' * len(header))
    for test_name, test_ref in refs.items():
        if test_name == "_info":
            continue
        if isinstance(test_ref, dict):
            for sex, sex_refs in test_ref.items():
                if isinstance(sex_refs, list):
                    for r in sex_refs:
                        age_range = f"{r['age_min']}-{r['age_max']}"
                        print(f"{test_name:<12} | {sex:<7} | {age_range:<11} | {r['min']:<6} | {r['max']:<6} | {r['unit']:<8}")
                elif isinstance(sex_refs, dict):
                    print(f"{test_name:<12} | {sex:<7} | {'-':<11} | {sex_refs['min']:<6} | {sex_refs['max']:<6} | {sex_refs['unit']:<8}")
        elif isinstance(test_ref, list):
            for r in test_ref:
                age_range = f"{r['age_min']}-{r['age_max']}"
                print(f"{test_name:<12} | {'all':<7} | {age_range:<11} | {r['min']:<6} | {r['max']:<6} | {r['unit']:<8}")
        elif isinstance(test_ref, dict):
            print(f"{test_name:<12} | {'all':<7} | {'-':<11} | {test_ref['min']:<6} | {test_ref['max']:<6} | {test_ref['unit']:<8}")
    return ""

def print_test_types_report(references_dir=None):
    """Печатает перечень всех доступных `test_type` с именем и описанием.

    Формат близок к sklearn classification_report: заголовок и табличные колонки.
    Имя и описание берутся из метаданных `_info` каждого JSON.
    """
    ref_dir = _get_references_dir(references_dir)
    types = []
    for fname in os.listdir(ref_dir):
        if not fname.endswith(".json"):
            continue
        test_type = os.path.splitext(fname)[0]
        try:
            refs = load_references(test_type, references_dir=ref_dir)
        except Exception:
            # Если файл битый, отображаем без метаданных
            refs = {}
        meta = refs.get("_info", {}) if isinstance(refs, dict) else {}
        name = meta.get("name", test_type)
        description = meta.get("description", "-")
        types.append((test_type, name, description))

    header = f"{'test_type':<16} | {'Name':<30} | {'Description':<50}"
    print(header)
    print('-' * len(header))
    for t, name, desc in sorted(types, key=lambda x: x[0]):
        print(f"{t:<16} | {name:<30} | {desc:<50}")
    return ""

def print_test_names_report(test_type, references_dir=None):
    """Печатает таблицу: Название на русском | Ключ | Единицы измерения."""
    refs = load_references(test_type, references_dir=references_dir)
    header = f"{'Название (RU)':<20} | {'Ключ':<15} | {'Ед. изм.':<10}"
    print(header)
    print('-' * len(header))
    for test_name, test_ref in refs.items():
        if test_name == "_info":
            continue
        # Получаем русское название
        name_ru = test_ref.get("name_ru", "-")
        # Получаем единицы измерения (берём из первого диапазона)
        unit = None
        # Ищем первую подходящую структуру с unit
        for v in test_ref.values():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "unit" in v[0]:
                unit = v[0]["unit"]
                break
            elif isinstance(v, dict) and "unit" in v:
                unit = v["unit"]
                break
        if not unit:
            unit = "-"
        print(f"{name_ru:<20} | {test_name:<15} | {unit:<10}")
    return ""

def get_test_keys(test_type, references_dir=None):
    """Возвращает список всех ключей показателей (test_name) для `test_type`."""
    refs = load_references(test_type, references_dir=references_dir)
    return list(refs.keys())


# === НОВЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С БИОМАТЕРИАЛАМИ ===

def list_biomaterials(references_dir=None):
    """Возвращает список доступных биоматериалов."""
    ref_dir = _get_references_dir(references_dir)
    biomaterials = []
    for fname in os.listdir(ref_dir):
        if fname.endswith(".json") and fname not in ["lab_studies.json"]:
            # Проверяем, является ли файл биоматериалом
            try:
                with open(os.path.join(ref_dir, fname), encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "_info" in data and "biomaterial_type" in data["_info"]:
                    biomaterials.append(os.path.splitext(fname)[0])
            except Exception:
                continue
    return biomaterials


def get_biomaterial_reference(biomaterial_type, test_name, sex=None, age=None, references_dir=None):
    """Получает референс для теста из указанного биоматериала.
    
    Parameters:
        biomaterial_type (str): Тип биоматериала, например "venous_blood".
        test_name (str): Имя теста.
        sex (str | None): Пол пациента.
        age (float | int | None): Возраст пациента.
        references_dir (str | None): Пользовательская папка с JSON.
    
    Returns:
        dict: Словарь с полями min, max, unit (и age_min/age_max при возрастных диапазонах).
    """
    return get_reference(biomaterial_type, test_name, sex, age, references_dir)


def check_biomaterial_value(biomaterial_type, test_name, value, sex=None, age=None, references_dir=None):
    """Проверяет значение теста относительно референса биоматериала.
    
    Parameters:
        biomaterial_type (str): Тип биоматериала.
        test_name (str | dict): Имя теста или словарь {test_name: value}.
        value (float | int | None): Значение теста.
        sex (str | None): Пол пациента.
        age (float | int | None): Возраст пациента.
        references_dir (str | None): Пользовательская папка с JSON.
    
    Returns:
        str | dict: "below" | "normal" | "above" или словарь результатов.
    """
    return check_value(biomaterial_type, test_name, value, sex, age, references_dir)


def load_lab_studies(references_dir=None):
    """Загружает определения лабораторных исследований из lab_studies.json.
    
    Parameters:
        references_dir (str | None): Пользовательская папка с JSON.
    
    Returns:
        dict: Содержимое файла lab_studies.json.
    """
    ref_dir = _get_references_dir(references_dir)
    path = os.path.join(ref_dir, "lab_studies.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data


def list_lab_studies(references_dir=None):
    """Возвращает список доступных лабораторных исследований."""
    studies = load_lab_studies(references_dir)
    return [name for name in studies.keys() if name != "_info"]


def get_study_info(study_name, references_dir=None):
    """Получает информацию о лабораторном исследовании.
    
    Parameters:
        study_name (str): Название исследования.
        references_dir (str | None): Пользовательская папка с JSON.
    
    Returns:
        dict: Информация об исследовании.
    """
    studies = load_lab_studies(references_dir)
    if study_name not in studies:
        raise ValueError(f"Study '{study_name}' not found")
    return studies[study_name]


def get_study_tests(study_name, references_dir=None):
    """Получает список тестов для исследования.
    
    Parameters:
        study_name (str): Название исследования.
        references_dir (str | None): Пользовательская папка с JSON.
    
    Returns:
        list: Список тестов исследования.
    """
    study_info = get_study_info(study_name, references_dir)
    return study_info.get("tests", [])


def get_study_biomaterials(study_name, references_dir=None):
    """Получает список биоматериалов для исследования.
    
    Parameters:
        study_name (str): Название исследования.
        references_dir (str | None): Пользовательская папка с JSON.
    
    Returns:
        list: Список биоматериалов.
    """
    study_info = get_study_info(study_name, references_dir)
    return study_info.get("biomaterials", [])


def get_preferred_biomaterial(study_name, references_dir=None):
    """Получает предпочтительный биоматериал для исследования.
    
    Parameters:
        study_name (str): Название исследования.
        references_dir (str | None): Пользовательская папка с JSON.
    
    Returns:
        str: Предпочтительный биоматериал.
    """
    study_info = get_study_info(study_name, references_dir)
    return study_info.get("preferred_biomaterial", study_info.get("biomaterials", [])[0] if study_info.get("biomaterials") else "")


def check_study_values(study_name, test_values, biomaterial_type=None, sex=None, age=None, references_dir=None):
    """Проверяет значения тестов для лабораторного исследования.
    
    Parameters:
        study_name (str): Название исследования.
        test_values (dict): Словарь {test_name: value}.
        biomaterial_type (str | None): Тип биоматериала (если None, используется предпочтительный).
        sex (str | None): Пол пациента.
        age (float | int | None): Возраст пациента.
        references_dir (str | None): Пользовательская папка с JSON.
    
    Returns:
        dict: Словарь результатов {test_name: status}.
    """
    if biomaterial_type is None:
        biomaterial_type = get_preferred_biomaterial(study_name, references_dir)
    
    # Проверяем, что все тесты входят в исследование
    study_tests = [t["test_name"] for t in get_study_tests(study_name, references_dir)]
    for test_name in test_values.keys():
        if test_name not in study_tests:
            raise ValueError(f"Test '{test_name}' is not part of study '{study_name}'")
    
    # Проверяем значения
    results = {}
    for test_name, value in test_values.items():
        results[test_name] = check_biomaterial_value(
            biomaterial_type, test_name, value, sex, age, references_dir
        )
    
    return results


def print_biomaterials_report(references_dir=None):
    """Печатает отчет по всем доступным биоматериалам."""
    biomaterials = list_biomaterials(references_dir)
    
    print("=== ДОСТУПНЫЕ БИОМАТЕРИАЛЫ ===\n")
    
    header = f"{'Тип':<18} | {'Название':<25} | {'Способ взятия':<35}"
    print(header)
    print('-' * len(header))
    
    for biomaterial_type in sorted(biomaterials):
        try:
            refs = load_references(biomaterial_type, references_dir)
            meta = refs.get("_info", {})
            name = meta.get("name", biomaterial_type)
            collection_method = meta.get("collection_method", "-")
            print(f"{biomaterial_type:<18} | {name:<25} | {collection_method:<35}")
        except Exception:
            print(f"{biomaterial_type:<18} | {'Ошибка загрузки':<25} | {'-':<35}")
    
    return ""


def print_lab_studies_report(references_dir=None):
    """Печатает отчет по всем лабораторным исследованиям."""
    studies = list_lab_studies(references_dir)
    
    print("=== ЛАБОРАТОРНЫЕ ИССЛЕДОВАНИЯ ===\n")
    
    for study_name in sorted(studies):
        try:
            study_info = get_study_info(study_name, references_dir)
            print(f"📋 {study_info.get('name', study_name)}")
            print(f"   Описание: {study_info.get('description', '-')}")
            print(f"   Биоматериалы: {', '.join(study_info.get('biomaterials', []))}")
            print(f"   Предпочтительный: {study_info.get('preferred_biomaterial', '-')}")
            
            tests = study_info.get("tests", [])
            required_tests = [t["test_name"] for t in tests if t.get("required", False)]
            optional_tests = [t["test_name"] for t in tests if not t.get("required", False)]
            
            if required_tests:
                print(f"   Обязательные тесты: {', '.join(required_tests)}")
            if optional_tests:
                print(f"   Дополнительные тесты: {', '.join(optional_tests)}")
            print()
        except Exception as e:
            print(f"❌ {study_name}: Ошибка загрузки ({e})")
            print()
    
    return ""