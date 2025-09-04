"""Тесты для функциональности пользовательских папок с референсами."""

import os
import tempfile
import json
import pytest
import lab_ref


class TestCustomReferencesDirectory:
    """Тесты для работы с пользовательскими папками референсов."""
    
    def test_get_current_references_dir_default(self):
        """Тест получения стандартной папки с референсами."""
        # Убеждаемся, что переменная окружения не установлена
        old_env = os.environ.get("LAB_REF_DIR")
        if "LAB_REF_DIR" in os.environ:
            del os.environ["LAB_REF_DIR"]
        
        try:
            current_dir = lab_ref.get_current_references_dir()
            assert current_dir.endswith("references")
            assert os.path.exists(current_dir)
        finally:
            if old_env:
                os.environ["LAB_REF_DIR"] = old_env
    
    def test_set_and_reset_references_dir(self):
        """Тест установки и сброса пользовательской папки."""
        original_dir = lab_ref.get_current_references_dir()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Устанавливаем пользовательскую папку
            lab_ref.set_references_dir(temp_dir)
            
            # Проверяем, что папка изменилась
            current_dir = lab_ref.get_current_references_dir()
            assert current_dir == temp_dir
            
            # Сбрасываем к исходной папке
            lab_ref.reset_references_dir()
            
            # Проверяем, что папка вернулась к исходной
            reset_dir = lab_ref.get_current_references_dir()
            assert reset_dir == original_dir
    
    def test_environment_variable_priority(self):
        """Тест приоритета переменной окружения."""
        original_dir = lab_ref.get_current_references_dir()
        old_env = os.environ.get("LAB_REF_DIR")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Устанавливаем переменную окружения
                os.environ["LAB_REF_DIR"] = temp_dir
                
                # Проверяем, что библиотека использует папку из переменной
                current_dir = lab_ref.get_current_references_dir()
                assert current_dir == temp_dir
        finally:
            # Восстанавливаем переменную окружения
            if old_env:
                os.environ["LAB_REF_DIR"] = old_env
            elif "LAB_REF_DIR" in os.environ:
                del os.environ["LAB_REF_DIR"]
    
    def test_copy_references_template(self):
        """Тест копирования шаблона референсов."""
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = os.path.join(temp_dir, "test_references")
            
            # Копируем шаблон
            copied_files = lab_ref.copy_references_template(destination)
            
            # Проверяем, что файлы скопированы
            assert isinstance(copied_files, list)
            assert len(copied_files) > 0
            assert all(f.endswith('.json') for f in copied_files)
            
            # Проверяем, что папка создана
            assert os.path.exists(destination)
            
            # Проверяем, что файлы действительно существуют
            for filename in copied_files:
                file_path = os.path.join(destination, filename)
                assert os.path.exists(file_path)
                
                # Проверяем, что файл содержит валидный JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    assert isinstance(data, dict)
    
    def test_copy_references_template_creates_directory(self):
        """Тест создания папки при копировании шаблона."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Указываем несуществующую папку
            destination = os.path.join(temp_dir, "nested", "test_references")
            
            # Копируем шаблон
            copied_files = lab_ref.copy_references_template(destination)
            
            # Проверяем, что папка создана
            assert os.path.exists(destination)
            assert len(copied_files) > 0


class TestCustomReferencesUsage:
    """Тесты использования пользовательских референсов в функциях."""
    
    def test_explicit_references_dir_parameter(self):
        """Тест явного указания папки в функциях."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Копируем шаблон
            lab_ref.copy_references_template(temp_dir)
            
            # Проверяем функциональный API
            biomaterials = lab_ref.list_biomaterials(references_dir=temp_dir)
            assert isinstance(biomaterials, list)
            assert len(biomaterials) > 0
            
            studies = lab_ref.list_lab_studies(references_dir=temp_dir)
            assert isinstance(studies, list)
            assert len(studies) > 0
            
            # Проверяем получение референса
            if "venous_blood" in biomaterials:
                ref = lab_ref.get_biomaterial_reference(
                    "venous_blood", "hemoglobin", "male", 30, 
                    references_dir=temp_dir
                )
                assert isinstance(ref, dict)
                assert "min" in ref and "max" in ref
    
    def test_oop_api_with_custom_references(self):
        """Тест ООП API с пользовательскими референсами."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Копируем шаблон
            lab_ref.copy_references_template(temp_dir)
            
            # Тестируем BiomaterialManager
            manager = lab_ref.BiomaterialManager("venous_blood", references_dir=temp_dir)
            assert isinstance(manager.name, str)
            assert len(manager) > 0
            
            # Тестируем LabStudyManager
            study_manager = lab_ref.LabStudyManager(references_dir=temp_dir)
            studies = study_manager.list_studies()
            assert len(studies) > 0
            
            # Тестируем создание результата исследования
            if "blood_test" in studies:
                result = study_manager.create_study_result("blood_test", sex="male", age=30)
                assert isinstance(result, lab_ref.StudyResult)
    
    def test_priority_order(self):
        """Тест порядка приоритета папок."""
        original_dir = lab_ref.get_current_references_dir()
        old_env = os.environ.get("LAB_REF_DIR")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                env_dir = os.path.join(temp_dir, "env_refs")
                explicit_dir = os.path.join(temp_dir, "explicit_refs")
                
                # Создаем папки
                lab_ref.copy_references_template(env_dir)
                lab_ref.copy_references_template(explicit_dir)
                
                # Устанавливаем переменную окружения
                os.environ["LAB_REF_DIR"] = env_dir
                
                # Без явного параметра должна использоваться переменная окружения
                current_dir = lab_ref.get_current_references_dir()
                assert current_dir == env_dir
                
                # С явным параметром должна использоваться явная папка
                biomaterials = lab_ref.list_biomaterials(references_dir=explicit_dir)
                assert isinstance(biomaterials, list)
                
        finally:
            # Восстанавливаем переменную окружения
            if old_env:
                os.environ["LAB_REF_DIR"] = old_env
            elif "LAB_REF_DIR" in os.environ:
                del os.environ["LAB_REF_DIR"]


class TestCustomReferencesModification:
    """Тесты модификации пользовательских референсов."""
    
    def test_modified_references_work(self):
        """Тест работы с модифицированными референсами."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Копируем шаблон
            lab_ref.copy_references_template(temp_dir)
            
            # Модифицируем один из файлов
            venous_file = os.path.join(temp_dir, "venous_blood.json")
            
            # Читаем файл
            with open(venous_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Добавляем новый тест
            data["test_custom"] = {
                "name_ru": "Тестовый показатель",
                "test_code": "TEST",
                "all": [
                    {"age_min": 0, "age_max": 150, "min": 5, "max": 10, "unit": "test_unit"}
                ]
            }
            
            # Записываем обратно
            with open(venous_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Проверяем, что новый тест доступен
            manager = lab_ref.BiomaterialManager("venous_blood", references_dir=temp_dir)
            tests = manager.list_tests()
            
            assert "test_custom" in tests
            
            # Создаем тест с новым показателем
            test = manager.create_test("test_custom", 7, age=25)
            assert test.name == "test_custom"
            assert test.value == 7
            assert test.status == "normal"  # 7 между 5 и 10
    
    def test_invalid_references_directory(self):
        """Тест обработки несуществующей папки с референсами."""
        nonexistent_dir = "/path/that/does/not/exist"
        
        with pytest.raises(FileNotFoundError):
            lab_ref.list_biomaterials(references_dir=nonexistent_dir)
    
    def test_empty_references_directory(self):
        """Тест обработки пустой папки с референсами."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Пустая папка
            biomaterials = lab_ref.list_biomaterials(references_dir=temp_dir)
            assert biomaterials == []
            
            # Должна быть ошибка, так как lab_studies.json отсутствует
            with pytest.raises(FileNotFoundError):
                studies = lab_ref.list_lab_studies(references_dir=temp_dir)


class TestBackwardCompatibility:
    """Тесты обратной совместимости."""
    
    def test_old_api_still_works_with_custom_dir(self):
        """Тест работы старого API с пользовательскими папками."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Копируем шаблон
            lab_ref.copy_references_template(temp_dir)
            
            # Устанавливаем пользовательскую папку
            lab_ref.set_references_dir(temp_dir)
            
            try:
                # Проверяем старые функции
                if "blood_test" in os.listdir(temp_dir):
                    ref = lab_ref.get_reference("blood_test", "hemoglobin", "male", 30)
                    assert isinstance(ref, dict)
                    
                    status = lab_ref.check_value("blood_test", "hemoglobin", 150, "male", 30)
                    assert status in ["below", "normal", "above"]
                
                # Проверяем старые классы
                if "blood_test" in os.listdir(temp_dir):
                    manager = lab_ref.ReferenceManager("blood_test")
                    assert len(manager) > 0
                    
                    result = lab_ref.LabResult("blood_test", "male", 30)
                    assert isinstance(result, lab_ref.LabResult)
                
            finally:
                lab_ref.reset_references_dir()
    
    def test_functions_without_references_dir_parameter(self):
        """Тест функций без параметра references_dir."""
        # Проверяем, что функции работают без явного указания папки
        biomaterials = lab_ref.list_biomaterials()
        assert isinstance(biomaterials, list)
        
        studies = lab_ref.list_lab_studies()
        assert isinstance(studies, list)
        
        current_dir = lab_ref.get_current_references_dir()
        assert isinstance(current_dir, str)
        assert os.path.exists(current_dir)
