"""Тесты для ООП классов модуля lab_ref.models."""

import pytest
import tempfile
import os
import json
from lab_ref.models import AgeRange, Reference, Test, ReferenceManager, LabResult


class TestAgeRange:
    """Тесты для класса AgeRange."""
    
    def test_age_range_creation(self):
        age_range = AgeRange(18, 65, 130, 170, "g/L")
        assert age_range.age_min == 18
        assert age_range.age_max == 65
        assert age_range.min_value == 130
        assert age_range.max_value == 170
        assert age_range.unit == "g/L"

    def test_contains_age(self):
        age_range = AgeRange(18, 65, 130, 170, "g/L")
        assert age_range.contains_age(25) == True
        assert age_range.contains_age(18) == True  # включительно
        assert age_range.contains_age(65) == False  # не включительно
        assert age_range.contains_age(10) == False

    def test_check_value(self):
        age_range = AgeRange(18, 65, 130, 170, "g/L")
        assert age_range.check_value(140) == "normal"
        assert age_range.check_value(120) == "below"
        assert age_range.check_value(180) == "above"

    def test_str_representation(self):
        age_range = AgeRange(18, 65, 130, 170, "g/L")
        expected = "130-170 g/L (возраст 18-65)"
        assert str(age_range) == expected


class TestReference:
    """Тесты для класса Reference."""
    
    def test_reference_creation(self):
        ref = Reference("hemoglobin", "Гемоглобин")
        assert ref.name == "hemoglobin"
        assert ref.name_ru == "Гемоглобин"

    def test_reference_creation_without_ru_name(self):
        ref = Reference("test")
        assert ref.name == "test"
        assert ref.name_ru == "test"

    def test_add_age_range(self):
        ref = Reference("hemoglobin")
        age_range = AgeRange(18, 65, 130, 170, "g/L")
        ref.add_age_range("male", age_range)
        
        assert "male" in ref._age_ranges
        assert len(ref._age_ranges["male"]) == 1
        assert ref._age_ranges["male"][0] == age_range

    def test_add_simple_reference(self):
        ref = Reference("test")
        ref.add_simple_reference("all", 10, 20, "unit")
        
        assert "all" in ref._simple_refs
        assert ref._simple_refs["all"]["min"] == 10
        assert ref._simple_refs["all"]["max"] == 20
        assert ref._simple_refs["all"]["unit"] == "unit"

    def test_get_reference_age_range(self):
        ref = Reference("hemoglobin")
        age_range = AgeRange(18, 65, 130, 170, "g/L")
        ref.add_age_range("male", age_range)
        
        result = ref.get_reference("male", 25)
        expected = {
            "min": 130,
            "max": 170,
            "unit": "g/L",
            "age_min": 18,
            "age_max": 65
        }
        assert result == expected

    def test_get_reference_simple(self):
        ref = Reference("test")
        ref.add_simple_reference("all", 10, 20, "unit")
        
        result = ref.get_reference("all")
        expected = {"min": 10, "max": 20, "unit": "unit"}
        assert result == expected

    def test_get_reference_not_found(self):
        ref = Reference("test")
        with pytest.raises(ValueError):
            ref.get_reference("nonexistent", 25)

    def test_check_value(self):
        ref = Reference("test")
        ref.add_simple_reference("all", 10, 20, "unit")
        
        assert ref.check_value(15, "all") == "normal"
        assert ref.check_value(5, "all") == "below"
        assert ref.check_value(25, "all") == "above"

    def test_from_dict_with_age_ranges(self):
        data = {
            "name_ru": "Гемоглобин",
            "male": [
                {"age_min": 18, "age_max": 65, "min": 130, "max": 170, "unit": "g/L"}
            ]
        }
        ref = Reference.from_dict("hemoglobin", data)
        
        assert ref.name == "hemoglobin"
        assert ref.name_ru == "Гемоглобин"
        assert "male" in ref._age_ranges
        assert len(ref._age_ranges["male"]) == 1

    def test_from_dict_with_simple_ref(self):
        data = {
            "name_ru": "Тест",
            "all": {"min": 10, "max": 20, "unit": "unit"}
        }
        ref = Reference.from_dict("test", data)
        
        assert ref.name == "test"
        assert ref.name_ru == "Тест"
        assert "all" in ref._simple_refs


class TestTest:
    """Тесты для класса Test."""
    
    def setup_method(self):
        self.ref = Reference("hemoglobin", "Гемоглобин")
        self.ref.add_simple_reference("all", 130, 170, "g/L")

    def test_test_creation(self):
        test = Test(self.ref, 150, "male", 30)
        assert test.reference == self.ref
        assert test.value == 150
        assert test.sex == "male"
        assert test.age == 30

    def test_test_properties(self):
        test = Test(self.ref, 150)
        assert test.name == "hemoglobin"
        assert test.name_ru == "Гемоглобин"

    def test_status_property(self):
        test = Test(self.ref, 150)
        assert test.status == "normal"
        
        test.value = 120
        assert test.status == "below"
        
        test.value = 180
        assert test.status == "above"

    def test_status_without_value(self):
        test = Test(self.ref)
        assert test.status is None

    def test_set_value(self):
        test = Test(self.ref)
        result = test.set_value(150)
        assert result is test  # fluent interface
        assert test.value == 150

    def test_set_patient_info(self):
        test = Test(self.ref)
        result = test.set_patient_info("male", 30)
        assert result is test  # fluent interface
        assert test.sex == "male"
        assert test.age == 30

    def test_is_normal(self):
        test = Test(self.ref, 150)
        assert test.is_normal() == True
        
        test.value = 120
        assert test.is_normal() == False

    def test_is_abnormal(self):
        test = Test(self.ref, 150)
        assert test.is_abnormal() == False
        
        test.value = 120
        assert test.is_abnormal() == True


class TestReferenceManager:
    """Тесты для класса ReferenceManager."""
    
    def test_manager_creation(self):
        manager = ReferenceManager("blood_test")
        assert manager.test_type == "blood_test"
        assert len(manager) > 0  # должен загрузить референсы из blood_test.json

    def test_manager_properties(self):
        manager = ReferenceManager("blood_test")
        assert manager.name == "Общий анализ крови"
        assert "справочник референсов" in manager.description.lower()

    def test_get_reference(self):
        manager = ReferenceManager("blood_test")
        ref = manager.get_reference("hemoglobin")
        assert isinstance(ref, Reference)
        assert ref.name == "hemoglobin"

    def test_get_reference_not_found(self):
        manager = ReferenceManager("blood_test")
        with pytest.raises(ValueError):
            manager.get_reference("nonexistent")

    def test_create_test(self):
        manager = ReferenceManager("blood_test")
        test = manager.create_test("hemoglobin", 150, "male", 30)
        assert isinstance(test, Test)
        assert test.name == "hemoglobin"
        assert test.value == 150

    def test_list_tests(self):
        manager = ReferenceManager("blood_test")
        tests = manager.list_tests()
        assert isinstance(tests, list)
        assert "hemoglobin" in tests
        assert "leukocytes" in tests

    def test_get_test_names_ru(self):
        manager = ReferenceManager("blood_test")
        names_ru = manager.get_test_names_ru()
        assert isinstance(names_ru, dict)
        assert names_ru["hemoglobin"] == "Гемоглобин"

    def test_contains(self):
        manager = ReferenceManager("blood_test")
        assert "hemoglobin" in manager
        assert "nonexistent" not in manager

    def test_iteration(self):
        manager = ReferenceManager("blood_test")
        items = list(manager)
        assert len(items) > 0
        assert all(isinstance(item[1], Reference) for item in items)


class TestLabResult:
    """Тесты для класса LabResult."""
    
    def test_lab_result_creation(self):
        result = LabResult("blood_test", "male", 30)
        assert result.sex == "male"
        assert result.age == 30
        assert isinstance(result.manager, ReferenceManager)

    def test_add_result(self):
        result = LabResult("blood_test")
        returned = result.add_result("hemoglobin", 150)
        
        assert returned is result  # fluent interface
        assert "hemoglobin" in result
        assert len(result) == 1

    def test_add_results(self):
        result = LabResult("blood_test")
        results_dict = {"hemoglobin": 150, "leukocytes": 5.0}
        returned = result.add_results(results_dict)
        
        assert returned is result  # fluent interface
        assert len(result) == 2

    def test_get_test(self):
        result = LabResult("blood_test")
        result.add_result("hemoglobin", 150)
        
        test = result.get_test("hemoglobin")
        assert isinstance(test, Test)
        assert test.value == 150

    def test_get_test_not_found(self):
        result = LabResult("blood_test")
        with pytest.raises(ValueError):
            result.get_test("nonexistent")

    def test_get_all_tests(self):
        result = LabResult("blood_test")
        result.add_results({"hemoglobin": 150, "leukocytes": 5.0})
        
        all_tests = result.get_all_tests()
        assert len(all_tests) == 2
        assert isinstance(all_tests, dict)

    def test_get_abnormal_tests(self):
        result = LabResult("blood_test", "male", 30)
        result.add_results({"hemoglobin": 100, "leukocytes": 5.0})  # hemoglobin будет below
        
        abnormal = result.get_abnormal_tests()
        assert "hemoglobin" in abnormal
        assert "leukocytes" not in abnormal

    def test_get_normal_tests(self):
        result = LabResult("blood_test", "male", 30)
        result.add_results({"hemoglobin": 100, "leukocytes": 5.0})  # hemoglobin будет below
        
        normal = result.get_normal_tests()
        assert "hemoglobin" not in normal
        assert "leukocytes" in normal

    def test_has_abnormalities(self):
        result = LabResult("blood_test", "male", 30)
        assert result.has_abnormalities() == False
        
        result.add_result("hemoglobin", 100)  # below normal
        assert result.has_abnormalities() == True

    def test_get_summary(self):
        result = LabResult("blood_test", "male", 30)
        result.add_results({"hemoglobin": 100, "leukocytes": 5.0})  # below, normal
        
        summary = result.get_summary()
        assert summary["total"] == 2
        assert summary["below"] == 1
        assert summary["normal"] == 1
        assert summary["above"] == 0

    def test_set_patient_info(self):
        result = LabResult("blood_test")
        result.add_result("hemoglobin", 150)
        
        returned = result.set_patient_info("female", 25)
        assert returned is result  # fluent interface
        assert result.sex == "female"
        assert result.age == 25
        
        # Проверяем, что информация обновилась в тестах
        test = result.get_test("hemoglobin")
        assert test.sex == "female"
        assert test.age == 25

    def test_check_value_functional_integration(self):
        """Тест интеграции с функциональным API."""
        result = LabResult("blood_test", "male", 30)
        
        # Используем ООП объект для вызова функционального API
        status = result.check_value_functional("hemoglobin", 145)
        assert status in ["below", "normal", "above"]

    def test_print_report_smoke(self, capsys):
        """Smoke-тест для метода print_report."""
        result = LabResult("blood_test", "male", 30)
        result.add_results({"hemoglobin": 150, "leukocytes": 5.0})
        
        result.print_report()
        captured = capsys.readouterr()
        assert "Общий анализ крови" in captured.out
        assert "Гемоглобин" in captured.out

    def test_print_report_abnormal_only(self, capsys):
        """Тест печати только отклонений."""
        result = LabResult("blood_test", "male", 30)
        result.add_results({"hemoglobin": 100, "leukocytes": 5.0})  # below, normal
        
        result.print_report(show_only_abnormal=True)
        captured = capsys.readouterr()
        assert "Гемоглобин" in captured.out
        # leukocytes может не отображаться, если он в норме


class TestHybridApproach:
    """Тесты для демонстрации гибридного подхода."""
    
    def test_functional_vs_oop_same_result(self):
        """Проверяем, что функциональный и ООП подходы дают одинаковые результаты."""
        import lab_ref
        
        # Функциональный подход
        functional_result = lab_ref.check_value("blood_test", "hemoglobin", 145, sex="male", age=30)
        
        # ООП подход
        manager = lab_ref.ReferenceManager("blood_test")
        test = manager.create_test("hemoglobin", 145, "male", 30)
        oop_result = test.status
        
        assert functional_result == oop_result

    def test_functional_api_still_works(self):
        """Проверяем, что функциональный API не сломался после добавления ООП."""
        import lab_ref
        
        # Все функциональные методы должны работать
        ref = lab_ref.get_reference("blood_test", "hemoglobin", sex="male", age=30)
        assert "min" in ref and "max" in ref
        
        status = lab_ref.check_value("blood_test", "hemoglobin", 145, sex="male", age=30)
        assert status in ["below", "normal", "above"]
        
        test_types = lab_ref.list_test_types()
        assert "blood_test" in test_types

    def test_oop_classes_available(self):
        """Проверяем, что ООП классы доступны через lab_ref."""
        import lab_ref
        
        # Проверяем, что все классы импортируются
        assert hasattr(lab_ref, "AgeRange")
        assert hasattr(lab_ref, "Reference")
        assert hasattr(lab_ref, "Test")
        assert hasattr(lab_ref, "ReferenceManager")
        assert hasattr(lab_ref, "LabResult")
        
        # Проверяем, что можно создавать объекты
        manager = lab_ref.ReferenceManager("blood_test")
        assert isinstance(manager, lab_ref.ReferenceManager)
        
        result = lab_ref.LabResult("blood_test")
        assert isinstance(result, lab_ref.LabResult)

    def test_fluent_interface_chain(self):
        """Тест цепочки вызовов (fluent interface)."""
        import lab_ref
        
        # Создаем результат через цепочку вызовов
        result = (lab_ref.LabResult("blood_test")
                  .set_patient_info("male", 30)
                  .add_result("hemoglobin", 145)
                  .add_result("leukocytes", 6.5))
        
        assert len(result) == 2
        assert result.sex == "male"
        assert result.age == 30
        assert "hemoglobin" in result
        assert "leukocytes" in result
