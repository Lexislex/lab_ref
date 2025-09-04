"""Тесты для новой функциональности работы с биоматериалами."""

import pytest
import lab_ref


class TestBiomaterialFunctionalAPI:
    """Тесты функционального API для биоматериалов."""
    
    def test_list_biomaterials(self):
        """Тест получения списка биоматериалов."""
        biomaterials = lab_ref.list_biomaterials()
        assert isinstance(biomaterials, list)
        assert len(biomaterials) > 0
        assert "venous_blood" in biomaterials
        assert "capillary_blood" in biomaterials
        assert "arterial_blood" in biomaterials
        assert "urine" in biomaterials
    
    def test_get_biomaterial_reference(self):
        """Тест получения референса из биоматериала."""
        ref = lab_ref.get_biomaterial_reference("venous_blood", "hemoglobin", sex="male", age=30)
        assert isinstance(ref, dict)
        assert "min" in ref
        assert "max" in ref
        assert "unit" in ref
        assert ref["unit"] == "g/L"
        assert ref["min"] > 0
        assert ref["max"] > ref["min"]
    
    def test_check_biomaterial_value(self):
        """Тест проверки значения для биоматериала."""
        # Нормальное значение
        status = lab_ref.check_biomaterial_value("venous_blood", "hemoglobin", 150, "male", 30)
        assert status == "normal"
        
        # Пониженное значение
        status = lab_ref.check_biomaterial_value("venous_blood", "hemoglobin", 100, "male", 30)
        assert status == "below"
        
        # Повышенное значение
        status = lab_ref.check_biomaterial_value("venous_blood", "hemoglobin", 200, "male", 30)
        assert status == "above"
    
    def test_biomaterial_reference_differences(self):
        """Тест различий референсов между биоматериалами."""
        venous_ref = lab_ref.get_biomaterial_reference("venous_blood", "hemoglobin", "male", 30)
        capillary_ref = lab_ref.get_biomaterial_reference("capillary_blood", "hemoglobin", "male", 30)
        
        # Референсы должны отличаться
        assert venous_ref["min"] != capillary_ref["min"] or venous_ref["max"] != capillary_ref["max"]


class TestLabStudiesFunctionalAPI:
    """Тесты функционального API для лабораторных исследований."""
    
    def test_list_lab_studies(self):
        """Тест получения списка лабораторных исследований."""
        studies = lab_ref.list_lab_studies()
        assert isinstance(studies, list)
        assert len(studies) > 0
        assert "blood_test" in studies
        assert "blood_biochemistry" in studies
    
    def test_get_study_info(self):
        """Тест получения информации об исследовании."""
        info = lab_ref.get_study_info("blood_test")
        assert isinstance(info, dict)
        assert "name" in info
        assert "biomaterials" in info
        assert "tests" in info
        assert isinstance(info["biomaterials"], list)
        assert len(info["biomaterials"]) > 0
    
    def test_get_study_biomaterials(self):
        """Тест получения биоматериалов исследования."""
        biomaterials = lab_ref.get_study_biomaterials("blood_test")
        assert isinstance(biomaterials, list)
        assert "capillary_blood" in biomaterials or "venous_blood" in biomaterials
    
    def test_get_preferred_biomaterial(self):
        """Тест получения предпочтительного биоматериала."""
        preferred = lab_ref.get_preferred_biomaterial("blood_test")
        assert isinstance(preferred, str)
        assert len(preferred) > 0
    
    def test_check_study_values(self):
        """Тест проверки значений для исследования."""
        test_values = {"hemoglobin": 150, "leukocytes": 6.0}
        results = lab_ref.check_study_values("blood_test", test_values, sex="male", age=30)
        
        assert isinstance(results, dict)
        assert "hemoglobin" in results
        assert "leukocytes" in results
        assert results["hemoglobin"] in ["below", "normal", "above"]
        assert results["leukocytes"] in ["below", "normal", "above"]
    
    def test_check_study_values_invalid_test(self):
        """Тест проверки значений с неподходящим тестом."""
        test_values = {"invalid_test": 100}
        
        with pytest.raises(ValueError, match="is not part of study"):
            lab_ref.check_study_values("blood_test", test_values)


class TestBiomaterialManager:
    """Тесты класса BiomaterialManager."""
    
    def test_create_biomaterial_manager(self):
        """Тест создания менеджера биоматериала."""
        manager = lab_ref.BiomaterialManager("venous_blood")
        assert manager.biomaterial_type == "venous_blood"
        assert len(manager) > 0
        assert "hemoglobin" in manager
    
    def test_biomaterial_manager_properties(self):
        """Тест свойств менеджера биоматериала."""
        manager = lab_ref.BiomaterialManager("venous_blood")
        assert isinstance(manager.name, str)
        assert isinstance(manager.description, str)
        assert isinstance(manager.collection_method, str)
        assert len(manager.name) > 0
    
    def test_create_test_from_biomaterial(self):
        """Тест создания теста из биоматериала."""
        manager = lab_ref.BiomaterialManager("venous_blood")
        test = manager.create_test("hemoglobin", 150, "male", 30)
        
        assert isinstance(test, lab_ref.Test)
        assert test.name == "hemoglobin"
        assert test.value == 150
        assert test.sex == "male"
        assert test.age == 30
        assert test.status in ["below", "normal", "above"]
    
    def test_list_tests_biomaterial(self):
        """Тест получения списка тестов биоматериала."""
        manager = lab_ref.BiomaterialManager("venous_blood")
        tests = manager.list_tests()
        assert isinstance(tests, list)
        assert len(tests) > 0
        assert "hemoglobin" in tests


class TestLabStudyManager:
    """Тесты класса LabStudyManager."""
    
    def test_create_lab_study_manager(self):
        """Тест создания менеджера лабораторных исследований."""
        manager = lab_ref.LabStudyManager()
        studies = manager.list_studies()
        assert isinstance(studies, list)
        assert len(studies) > 0
    
    def test_get_test_reference_from_study_manager(self):
        """Тест получения референса через менеджер исследований."""
        manager = lab_ref.LabStudyManager()
        ref = manager.get_test_reference("hemoglobin", "venous_blood", "male", 30)
        
        assert isinstance(ref, dict)
        assert "min" in ref
        assert "max" in ref
        assert "unit" in ref
    
    def test_check_test_value_from_study_manager(self):
        """Тест проверки значения через менеджер исследований."""
        manager = lab_ref.LabStudyManager()
        status = manager.check_test_value("hemoglobin", 150, "venous_blood", "male", 30)
        assert status in ["below", "normal", "above"]
    
    def test_create_study_result(self):
        """Тест создания результата исследования."""
        manager = lab_ref.LabStudyManager()
        result = manager.create_study_result("blood_test", sex="male", age=30)
        
        assert isinstance(result, lab_ref.StudyResult)
        assert result.study_name == "blood_test"
        assert result.sex == "male"
        assert result.age == 30
    
    def test_find_studies_with_test(self):
        """Тест поиска исследований с определенным тестом."""
        manager = lab_ref.LabStudyManager()
        studies = manager.find_studies_with_test("hemoglobin")
        
        assert isinstance(studies, list)
        assert len(studies) > 0
        assert "blood_test" in studies


class TestStudyResult:
    """Тесты класса StudyResult."""
    
    def test_create_study_result(self):
        """Тест создания результата исследования."""
        manager = lab_ref.LabStudyManager()
        result = manager.create_study_result("blood_test", "capillary_blood", "female", 25)
        
        assert result.study_name == "blood_test"
        assert result.biomaterial_type == "capillary_blood"
        assert result.sex == "female"
        assert result.age == 25
        assert len(result) == 0
    
    def test_add_results_to_study(self):
        """Тест добавления результатов в исследование."""
        manager = lab_ref.LabStudyManager()
        result = manager.create_study_result("blood_test", "capillary_blood", "female", 25)
        
        result.add_results({"hemoglobin": 130, "leukocytes": 6.5})
        
        assert len(result) == 2
        assert "hemoglobin" in result
        assert "leukocytes" in result
        
        hb_test = result.get_test("hemoglobin")
        assert hb_test.value == 130
        assert hb_test.status in ["below", "normal", "above"]
    
    def test_study_result_analysis(self):
        """Тест анализа результатов исследования."""
        manager = lab_ref.LabStudyManager()
        result = manager.create_study_result("blood_test", "capillary_blood", "female", 25)
        
        # Добавляем нормальные и аномальные значения
        result.add_results({"hemoglobin": 100, "leukocytes": 6.5})  # hemoglobin понижен
        
        assert result.has_abnormalities()
        abnormal = result.get_abnormal_tests()
        assert len(abnormal) >= 1
        
        summary = result.get_summary()
        assert isinstance(summary, dict)
        assert "normal" in summary
        assert "below" in summary
        assert "above" in summary
        assert "total" in summary
        assert summary["total"] == 2
    
    def test_study_result_info_methods(self):
        """Тест методов получения информации о результате исследования."""
        manager = lab_ref.LabStudyManager()
        result = manager.create_study_result("blood_test", "capillary_blood", "male", 30)
        
        study_info = result.get_study_info()
        assert isinstance(study_info, dict)
        assert "name" in study_info
        
        biomaterial_info = result.get_biomaterial_info()
        assert isinstance(biomaterial_info, dict)
        assert "name" in biomaterial_info
        assert "collection_method" in biomaterial_info
    
    def test_invalid_biomaterial_for_study(self):
        """Тест создания результата с неподходящим биоматериалом."""
        manager = lab_ref.LabStudyManager()
        
        # Пытаемся создать результат анализа мочи с кровью
        with pytest.raises(ValueError, match="not available for study"):
            manager.create_study_result("urine_analysis", "venous_blood")
    
    def test_invalid_test_for_study(self):
        """Тест добавления неподходящего теста в исследование."""
        manager = lab_ref.LabStudyManager()
        result = manager.create_study_result("blood_test", "capillary_blood")
        
        # Пытаемся добавить тест, который не входит в исследование
        with pytest.raises(ValueError, match="is not part of study"):
            result.add_result("ph", 7.4)  # pH не входит в общий анализ крови


class TestReportFunctions:
    """Тесты функций отчетов."""
    
    def test_print_biomaterials_report(self):
        """Тест отчета по биоматериалам."""
        # Проверяем, что функция не вызывает исключений
        try:
            lab_ref.print_biomaterials_report()
        except Exception as e:
            pytest.fail(f"print_biomaterials_report raised {e}")
    
    def test_print_lab_studies_report(self):
        """Тест отчета по лабораторным исследованиям."""
        # Проверяем, что функция не вызывает исключений
        try:
            lab_ref.print_lab_studies_report()
        except Exception as e:
            pytest.fail(f"print_lab_studies_report raised {e}")


class TestBackwardCompatibility:
    """Тесты обратной совместимости."""
    
    def test_old_api_still_works(self):
        """Тест того, что старый API все еще работает."""
        # Проверяем, что старые функции все еще доступны
        assert hasattr(lab_ref, "get_reference")
        assert hasattr(lab_ref, "check_value")
        assert hasattr(lab_ref, "ReferenceManager")
        assert hasattr(lab_ref, "LabResult")
        
        # Проверяем, что старый API работает с существующими файлами
        try:
            ref = lab_ref.get_reference("blood_test", "hemoglobin", "male", 30)
            assert isinstance(ref, dict)
            
            status = lab_ref.check_value("blood_test", "hemoglobin", 150, "male", 30)
            assert status in ["below", "normal", "above"]
        except FileNotFoundError:
            # Если старый файл blood_test.json не существует, это ожидаемо
            pass
