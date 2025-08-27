import pytest
from lab_ref.utils import get_reference, check_value, validate_references_structure, list_test_types, print_reference_report, print_test_names_report
import tempfile
import os
import json

# Тесты для get_reference с учетом возраста

def test_get_reference_hemoglobin_male_adult():
    ref = get_reference("blood_test", "hemoglobin", sex="male", age=30)
    assert ref == {"age_min": 18, "age_max": 150, "min": 130, "max": 170, "unit": "g/L"}

def test_get_reference_hemoglobin_male_child():
    ref = get_reference("blood_test", "hemoglobin", sex="male", age=5)
    assert ref == {"age_min": 1, "age_max": 18, "min": 120, "max": 160, "unit": "g/L"}

def test_get_reference_hemoglobin_female_infant():
    ref = get_reference("blood_test", "hemoglobin", sex="female", age=0.5)
    assert ref == {"age_min": 0, "age_max": 1, "min": 110, "max": 140, "unit": "g/L"}

def test_get_reference_leukocytes_adult():
    ref = get_reference("blood_test", "leukocytes", age=30)
    assert ref == {"age_min": 18, "age_max": 150, "min": 4.0, "max": 9.0, "unit": "10^9/L"}

def test_get_reference_leukocytes_child():
    ref = get_reference("blood_test", "leukocytes", age=10)
    assert ref == {"age_min": 1, "age_max": 18, "min": 5.0, "max": 12.0, "unit": "10^9/L"}

# Тесты для check_value с учетом возраста

def test_check_value_below_age():
    assert check_value("blood_test", "hemoglobin", 100, sex="male", age=30) == "below"

def test_check_value_above_age():
    assert check_value("blood_test", "hemoglobin", 180, sex="male", age=30) == "above"

def test_check_value_normal_age():
    assert check_value("blood_test", "hemoglobin", 140, sex="male", age=30) == "normal"

def test_check_value_leukocytes_normal_age():
    assert check_value("blood_test", "leukocytes", 5.0, age=10) == "normal"

def test_check_value_leukocytes_below_age():
    assert check_value("blood_test", "leukocytes", 3.0, age=10) == "below"

def test_check_value_leukocytes_above_age():
    assert check_value("blood_test", "leukocytes", 13.0, age=10) == "above"

def test_check_value_multiple():
    results = check_value(
        "blood_test",
        {"hemoglobin": 100, "leukocytes": 5.0},
        sex="male",
        age=30
    )
    assert results == {"hemoglobin": "below", "leukocytes": "normal"}

# Проверка ошибки для несуществующего теста или возраста

def test_get_reference_not_found():
    with pytest.raises(ValueError):
        get_reference("blood_test", "nonexistent", age=30)

def test_get_reference_no_age_match():
    with pytest.raises(ValueError):
        get_reference("blood_test", "hemoglobin", sex="male", age=200)

def test_validate_references_structure_missing_key():
    # Нет ключа 'min' в диапазоне
    bad_data = {
        "hemoglobin": {
            "male": [
                {"age_min": 0, "age_max": 1, "max": 140, "unit": "g/L"}
            ]
        }
    }
    with pytest.raises(ValueError, match="Missing keys in age range"):
        validate_references_structure(bad_data)

def test_validate_references_structure_invalid_root():
    with pytest.raises(ValueError, match="root must be a dictionary"):
        validate_references_structure([1, 2, 3])

def test_list_test_types(tmp_path):
    # Создаем временную папку с двумя json-файлами
    ref_dir = tmp_path / "refs"
    ref_dir.mkdir()
    (ref_dir / "blood_test.json").write_text("{}", encoding="utf-8")
    (ref_dir / "urine_test.json").write_text("{}", encoding="utf-8")
    types = list_test_types(references_dir=str(ref_dir))
    assert set(types) == {"blood_test", "urine_test"}

def test_print_reference_report_smoke(capsys):
    # Smoke-тест: функция не должна выбрасывать исключение
    print_reference_report("blood_test")
    out = capsys.readouterr().out
    assert "Test Name" in out and "hemoglobin" in out

def test_print_test_names_report_smoke(capsys):
    print_test_names_report("blood_test")
    out = capsys.readouterr().out
    assert "Название (RU)" in out and "Гемоглобин" in out and "hemoglobin" in out
