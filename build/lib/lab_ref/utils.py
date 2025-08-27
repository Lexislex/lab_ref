import json
import os

def validate_references_structure(data):
    if not isinstance(data, dict):
        raise ValueError("Reference file root must be a dictionary.")
    for test_name, test_ref in data.items():
        if isinstance(test_ref, dict):
            for sex, sex_refs in test_ref.items():
                if sex == "name_ru":
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
    if references_dir is not None:
        return references_dir
    env_dir = os.environ.get("LAB_REF_DIR")
    if env_dir:
        return env_dir
    return os.path.join(os.path.dirname(__file__), "references")

def load_references(test_type, references_dir=None):
    ref_dir = _get_references_dir(references_dir)
    path = os.path.join(ref_dir, f"{test_type}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    validate_references_structure(data)
    return data

def list_test_types(references_dir=None):
    ref_dir = _get_references_dir(references_dir)
    test_types = []
    for fname in os.listdir(ref_dir):
        if fname.endswith(".json"):
            test_types.append(os.path.splitext(fname)[0])
    return test_types

def get_reference(test_type, test_name=None, sex=None, age=None, references_dir=None):
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
    refs = load_references(test_type, references_dir=references_dir)
    header = f"{'Test Name':<12} | {'Sex':<7} | {'Age Range':<11} | {'Min':<6} | {'Max':<6} | {'Unit':<8}"
    print(header)
    print('-' * len(header))
    for test_name, test_ref in refs.items():
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

def print_test_names_report(test_type, references_dir=None):
    """
    Выводит таблицу: Название на русском | Ключ в json | Единицы измерения
    """
    refs = load_references(test_type, references_dir=references_dir)
    header = f"{'Название (RU)':<20} | {'Ключ':<15} | {'Ед. изм.':<10}"
    print(header)
    print('-' * len(header))
    for test_name, test_ref in refs.items():
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

def get_test_keys(test_type, references_dir=None):
    """
    Возвращает список всех ключей тестов (test_name) из JSON для указанного test_type.
    """
    refs = load_references(test_type, references_dir=references_dir)
    return list(refs.keys())
