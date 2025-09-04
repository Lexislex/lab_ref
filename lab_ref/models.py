"""ООП модели для работы с лабораторными референсами.

Этот модуль предоставляет объектно-ориентированный интерфейс для работы
с лабораторными референсами. Функциональный API остается доступным для
простых случаев использования.
"""

import json
import os
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from .utils import _get_references_dir, validate_references_structure


@dataclass
class AgeRange:
    """Представляет возрастной диапазон с референсными значениями."""
    age_min: float
    age_max: float
    min_value: float
    max_value: float
    unit: str

    def contains_age(self, age: float) -> bool:
        """Проверяет, попадает ли возраст в данный диапазон."""
        return self.age_min <= age < self.age_max

    def check_value(self, value: float) -> str:
        """Сравнивает значение с референсными границами.
        
        Returns:
            str: "below", "normal", или "above"
        """
        if value < self.min_value:
            return "below"
        elif value > self.max_value:
            return "above"
        else:
            return "normal"

    def __str__(self) -> str:
        return f"{self.min_value}-{self.max_value} {self.unit} (возраст {self.age_min}-{self.age_max})"


class Reference:
    """Класс для работы с референсными значениями одного показателя.
    
    Инкапсулирует логику получения референсов с учетом пола и возраста,
    а также проверки значений относительно нормы.
    """
    
    def __init__(self, name: str, name_ru: Optional[str] = None):
        self.name = name
        self.name_ru = name_ru or name
        self._age_ranges: Dict[str, List[AgeRange]] = {}
        self._simple_refs: Dict[str, Dict[str, Any]] = {}

    def add_age_range(self, sex: str, age_range: AgeRange) -> None:
        """Добавляет возрастной диапазон для указанного пола."""
        if sex not in self._age_ranges:
            self._age_ranges[sex] = []
        self._age_ranges[sex].append(age_range)

    def add_simple_reference(self, sex: str, min_val: float, max_val: float, unit: str) -> None:
        """Добавляет простой референс без возрастных диапазонов."""
        self._simple_refs[sex] = {
            "min": min_val,
            "max": max_val,
            "unit": unit
        }

    def get_reference(self, sex: Optional[str] = None, age: Optional[float] = None) -> Dict[str, Any]:
        """Получает подходящий референс по полу и возрасту.
        
        Args:
            sex: Пол ("male", "female", "all" или None)
            age: Возраст (необходим при наличии возрастных диапазонов)
            
        Returns:
            dict: Словарь с ключами min, max, unit (и age_min/age_max для возрастных диапазонов)
            
        Raises:
            ValueError: Если не найден подходящий референс
        """
        # Определяем приоритет поиска по полу
        search_order = []
        if sex:
            search_order.append(sex)
        search_order.extend(["all", "male", "female"])
        
        # Сначала ищем в возрастных диапазонах
        if age is not None:
            for s in search_order:
                if s in self._age_ranges:
                    for age_range in self._age_ranges[s]:
                        if age_range.contains_age(age):
                            return {
                                "min": age_range.min_value,
                                "max": age_range.max_value,
                                "unit": age_range.unit,
                                "age_min": age_range.age_min,
                                "age_max": age_range.age_max
                            }
        
        # Затем ищем в простых референсах
        for s in search_order:
            if s in self._simple_refs:
                return self._simple_refs[s]
        
        raise ValueError(f"No reference found for {self.name} with sex={sex}, age={age}")

    def check_value(self, value: float, sex: Optional[str] = None, age: Optional[float] = None) -> str:
        """Проверяет значение относительно референсных границ.
        
        Returns:
            str: "below", "normal", или "above"
        """
        ref = self.get_reference(sex, age)
        if value < ref["min"]:
            return "below"
        elif value > ref["max"]:
            return "above"
        else:
            return "normal"

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'Reference':
        """Создает объект Reference из словаря (данных JSON).
        
        Args:
            name: Имя показателя
            data: Данные из JSON файла
            
        Returns:
            Reference: Новый объект Reference
        """
        ref = cls(name, data.get("name_ru"))
        
        # Обрабатываем данные в зависимости от их структуры
        for key, value in data.items():
            if key == "name_ru":
                continue
                
            if isinstance(value, list):
                # Список возрастных диапазонов
                for item in value:
                    age_range = AgeRange(
                        age_min=item["age_min"],
                        age_max=item["age_max"],
                        min_value=item["min"],
                        max_value=item["max"],
                        unit=item["unit"]
                    )
                    ref.add_age_range(key, age_range)
            elif isinstance(value, dict) and "min" in value:
                # Простой референс
                ref.add_simple_reference(key, value["min"], value["max"], value["unit"])
        
        return ref

    def __str__(self) -> str:
        return f"Reference({self.name_ru} [{self.name}])"

    def __repr__(self) -> str:
        return f"Reference(name='{self.name}', name_ru='{self.name_ru}')"


class Test:
    """Класс для представления отдельного лабораторного показателя с его значением.
    
    Объединяет референсную информацию с конкретным значением и данными пациента.
    """
    
    def __init__(self, reference: Reference, value: Optional[float] = None, 
                 sex: Optional[str] = None, age: Optional[float] = None):
        self.reference = reference
        self.value = value
        self.sex = sex
        self.age = age

    @property
    def name(self) -> str:
        """Английское название показателя."""
        return self.reference.name

    @property
    def name_ru(self) -> str:
        """Русское название показателя."""
        return self.reference.name_ru

    @property
    def status(self) -> Optional[str]:
        """Статус значения относительно нормы."""
        if self.value is not None:
            return self.reference.check_value(self.value, self.sex, self.age)
        return None

    def set_value(self, value: float) -> 'Test':
        """Устанавливает значение показателя (fluent interface)."""
        self.value = value
        return self

    def set_patient_info(self, sex: Optional[str] = None, age: Optional[float] = None) -> 'Test':
        """Устанавливает информацию о пациенте (fluent interface)."""
        if sex is not None:
            self.sex = sex
        if age is not None:
            self.age = age
        return self

    def get_reference_info(self) -> Dict[str, Any]:
        """Получает референсную информацию для текущих параметров пациента."""
        return self.reference.get_reference(self.sex, self.age)

    def is_normal(self) -> bool:
        """Проверяет, находится ли значение в норме."""
        return self.status == "normal"

    def is_abnormal(self) -> bool:
        """Проверяет, отклоняется ли значение от нормы."""
        status = self.status
        return status in ["below", "above"]

    def __str__(self) -> str:
        if self.value is not None:
            ref_info = self.get_reference_info()
            status_str = f" [{self.status}]" if self.status else ""
            return f"{self.name_ru}: {self.value} {ref_info['unit']}{status_str}"
        return f"{self.name_ru}: не задано значение"

    def __repr__(self) -> str:
        return f"Test(name='{self.name}', value={self.value}, sex='{self.sex}', age={self.age})"


class ReferenceManager:
    """Менеджер для работы с коллекцией референсов определенного типа исследования.
    
    Обеспечивает загрузку, валидацию и предоставление доступа к референсам.
    Является фабрикой для создания объектов Test.
    """
    
    def __init__(self, test_type: str, references_dir: Optional[str] = None):
        self.test_type = test_type
        self.references_dir = references_dir
        self._references: Dict[str, Reference] = {}
        self._metadata: Dict[str, Any] = {}
        self._load_references()

    def _load_references(self) -> None:
        """Загружает референсы из JSON файла."""
        ref_dir = _get_references_dir(self.references_dir)
        path = os.path.join(ref_dir, f"{self.test_type}.json")
        
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        
        validate_references_structure(data)
        
        # Извлекаем метаданные
        if "_info" in data:
            self._metadata = data["_info"]
        
        # Создаем объекты Reference
        for test_name, test_data in data.items():
            if test_name == "_info":
                continue
            self._references[test_name] = Reference.from_dict(test_name, test_data)

    @property
    def name(self) -> str:
        """Название типа исследования."""
        return self._metadata.get("name", self.test_type)

    @property
    def description(self) -> str:
        """Описание типа исследования."""
        return self._metadata.get("description", "")

    def get_reference(self, test_name: str) -> Reference:
        """Получает объект Reference по имени показателя."""
        if test_name not in self._references:
            raise ValueError(f"Test '{test_name}' not found in {self.test_type}")
        return self._references[test_name]

    def create_test(self, test_name: str, value: Optional[float] = None,
                   sex: Optional[str] = None, age: Optional[float] = None) -> Test:
        """Создает объект Test для указанного показателя."""
        reference = self.get_reference(test_name)
        return Test(reference, value, sex, age)

    def list_tests(self) -> List[str]:
        """Возвращает список всех доступных показателей."""
        return list(self._references.keys())

    def get_test_names_ru(self) -> Dict[str, str]:
        """Возвращает словарь соответствия английских и русских названий."""
        return {name: ref.name_ru for name, ref in self._references.items()}

    def print_reference_report(self) -> None:
        """Печатает таблицу всех референсов (использует функциональный API)."""
        # Переиспользуем существующую функцию для совместимости
        from .utils import print_reference_report
        print_reference_report(self.test_type, self.references_dir)

    def __len__(self) -> int:
        return len(self._references)

    def __contains__(self, test_name: str) -> bool:
        return test_name in self._references

    def __iter__(self):
        return iter(self._references.items())

    def __str__(self) -> str:
        return f"ReferenceManager({self.name} - {len(self)} показателей)"

    def __repr__(self) -> str:
        return f"ReferenceManager(test_type='{self.test_type}', tests={len(self)})"


class LabResult:
    """Класс для представления результатов лабораторного исследования.
    
    Объединяет множественные результаты анализов для одного пациента,
    предоставляет методы для анализа и генерации отчетов.
    """
    
    def __init__(self, test_type: str, sex: Optional[str] = None, age: Optional[float] = None,
                 references_dir: Optional[str] = None):
        self.manager = ReferenceManager(test_type, references_dir)
        self.sex = sex
        self.age = age
        self._tests: Dict[str, Test] = {}

    def add_result(self, test_name: str, value: float) -> 'LabResult':
        """Добавляет результат анализа (fluent interface)."""
        test = self.manager.create_test(test_name, value, self.sex, self.age)
        self._tests[test_name] = test
        return self

    def add_results(self, results: Dict[str, float]) -> 'LabResult':
        """Добавляет несколько результатов анализов (fluent interface)."""
        for test_name, value in results.items():
            self.add_result(test_name, value)
        return self

    def get_test(self, test_name: str) -> Test:
        """Получает объект Test по имени показателя."""
        if test_name not in self._tests:
            raise ValueError(f"No result for test '{test_name}'")
        return self._tests[test_name]

    def get_all_tests(self) -> Dict[str, Test]:
        """Возвращает все тесты."""
        return self._tests.copy()

    def get_abnormal_tests(self) -> Dict[str, Test]:
        """Возвращает только тесты с отклонениями от нормы."""
        return {name: test for name, test in self._tests.items() if test.is_abnormal()}

    def get_normal_tests(self) -> Dict[str, Test]:
        """Возвращает только тесты в пределах нормы."""
        return {name: test for name, test in self._tests.items() if test.is_normal()}

    def has_abnormalities(self) -> bool:
        """Проверяет, есть ли отклонения от нормы."""
        return bool(self.get_abnormal_tests())

    def get_summary(self) -> Dict[str, int]:
        """Возвращает сводку по статусам результатов."""
        summary = {"normal": 0, "below": 0, "above": 0, "total": 0}
        for test in self._tests.values():
            if test.status:
                summary[test.status] += 1
            summary["total"] += 1
        return summary

    def print_report(self, show_only_abnormal: bool = False) -> None:
        """Печатает отчет по результатам анализов."""
        print(f"\n=== {self.manager.name} ===")
        if self.sex or self.age:
            patient_info = []
            if self.sex:
                patient_info.append(f"пол: {self.sex}")
            if self.age:
                patient_info.append(f"возраст: {self.age}")
            print(f"Пациент: {', '.join(patient_info)}")
        
        print()
        tests_to_show = self.get_abnormal_tests() if show_only_abnormal else self._tests
        
        if not tests_to_show:
            print("Нет результатов для отображения")
            return
            
        for test_name, test in tests_to_show.items():
            ref_info = test.get_reference_info()
            status_symbol = {"normal": "✓", "below": "↓", "above": "↑"}.get(test.status, "?")
            print(f"{status_symbol} {test}")
            print(f"   Норма: {ref_info['min']}-{ref_info['max']} {ref_info['unit']}")
            if 'age_min' in ref_info:
                print(f"   Возрастной диапазон: {ref_info['age_min']}-{ref_info['age_max']} лет")
            print()
        
        # Сводка
        summary = self.get_summary()
        print(f"Сводка: {summary['normal']} в норме, {summary['below']} понижено, {summary['above']} повышено")

    def set_patient_info(self, sex: Optional[str] = None, age: Optional[float] = None) -> 'LabResult':
        """Обновляет информацию о пациенте для всех тестов (fluent interface)."""
        if sex is not None:
            self.sex = sex
        if age is not None:
            self.age = age
        
        for test in self._tests.values():
            test.set_patient_info(sex, age)
        
        return self

    def check_value_functional(self, test_name: str, value: float) -> str:
        """Проверяет значение используя функциональный API (для совместимости).
        
        Этот метод демонстрирует интеграцию ООП и функционального подходов.
        """
        from .utils import check_value
        return check_value(self.manager.test_type, test_name, value, 
                          self.sex, self.age, self.manager.references_dir)

    def __len__(self) -> int:
        return len(self._tests)

    def __contains__(self, test_name: str) -> bool:
        return test_name in self._tests

    def __str__(self) -> str:
        return f"LabResult({self.manager.test_type} - {len(self)} результатов)"

    def __repr__(self) -> str:
        return f"LabResult(test_type='{self.manager.test_type}', results={len(self)}, sex='{self.sex}', age={self.age})"


class BiomaterialManager:
    """Менеджер для работы с биоматериалами и их референсами.
    
    Обеспечивает загрузку референсов для конкретного биоматериала
    и предоставляет доступ к тестам с учетом способа взятия материала.
    """
    
    def __init__(self, biomaterial_type: str, references_dir: Optional[str] = None):
        self.biomaterial_type = biomaterial_type
        self.references_dir = references_dir
        self._references: Dict[str, Reference] = {}
        self._metadata: Dict[str, Any] = {}
        self._load_references()

    def _load_references(self) -> None:
        """Загружает референсы биоматериала из JSON файла."""
        ref_dir = _get_references_dir(self.references_dir)
        path = os.path.join(ref_dir, f"{self.biomaterial_type}.json")
        
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        
        validate_references_structure(data)
        
        # Извлекаем метаданные
        if "_info" in data:
            self._metadata = data["_info"]
        
        # Создаем объекты Reference
        for test_name, test_data in data.items():
            if test_name == "_info":
                continue
            self._references[test_name] = Reference.from_dict(test_name, test_data)

    @property
    def name(self) -> str:
        """Название биоматериала."""
        return self._metadata.get("name", self.biomaterial_type)

    @property
    def description(self) -> str:
        """Описание биоматериала."""
        return self._metadata.get("description", "")

    @property
    def collection_method(self) -> str:
        """Способ взятия биоматериала."""
        return self._metadata.get("collection_method", "")

    def get_reference(self, test_name: str) -> Reference:
        """Получает объект Reference по имени теста."""
        if test_name not in self._references:
            raise ValueError(f"Test '{test_name}' not found in biomaterial {self.biomaterial_type}")
        return self._references[test_name]

    def create_test(self, test_name: str, value: Optional[float] = None,
                   sex: Optional[str] = None, age: Optional[float] = None) -> Test:
        """Создает объект Test для указанного показателя."""
        reference = self.get_reference(test_name)
        return Test(reference, value, sex, age)

    def list_tests(self) -> List[str]:
        """Возвращает список всех доступных тестов в данном биоматериале."""
        return list(self._references.keys())

    def get_test_names_ru(self) -> Dict[str, str]:
        """Возвращает словарь соответствия английских и русских названий."""
        return {name: ref.name_ru for name, ref in self._references.items()}

    def __len__(self) -> int:
        return len(self._references)

    def __contains__(self, test_name: str) -> bool:
        return test_name in self._references

    def __str__(self) -> str:
        return f"BiomaterialManager({self.name} - {len(self)} тестов)"

    def __repr__(self) -> str:
        return f"BiomaterialManager(biomaterial_type='{self.biomaterial_type}', tests={len(self)})"


class LabStudyManager:
    """Менеджер для работы с лабораторными исследованиями.
    
    Управляет составом исследований, связывает тесты с биоматериалами,
    и предоставляет методы для получения референсов различными способами.
    """
    
    def __init__(self, references_dir: Optional[str] = None):
        self.references_dir = references_dir
        self._studies: Dict[str, Dict[str, Any]] = {}
        self._biomaterial_managers: Dict[str, BiomaterialManager] = {}
        self._metadata: Dict[str, Any] = {}
        self._load_studies()

    def _load_studies(self) -> None:
        """Загружает определения лабораторных исследований."""
        ref_dir = _get_references_dir(self.references_dir)
        path = os.path.join(ref_dir, "lab_studies.json")
        
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        
        # Извлекаем метаданные
        if "_info" in data:
            self._metadata = data["_info"]
        
        # Сохраняем исследования
        for study_name, study_data in data.items():
            if study_name == "_info":
                continue
            self._studies[study_name] = study_data

    def _get_biomaterial_manager(self, biomaterial_type: str) -> BiomaterialManager:
        """Получает или создает менеджер биоматериала."""
        if biomaterial_type not in self._biomaterial_managers:
            self._biomaterial_managers[biomaterial_type] = BiomaterialManager(
                biomaterial_type, self.references_dir
            )
        return self._biomaterial_managers[biomaterial_type]

    def get_study_info(self, study_name: str) -> Dict[str, Any]:
        """Получает информацию о лабораторном исследовании."""
        if study_name not in self._studies:
            raise ValueError(f"Study '{study_name}' not found")
        return self._studies[study_name].copy()

    def list_studies(self) -> List[str]:
        """Возвращает список всех доступных исследований."""
        return list(self._studies.keys())

    def get_study_tests(self, study_name: str) -> List[Dict[str, Any]]:
        """Получает список тестов для исследования."""
        study = self.get_study_info(study_name)
        return study.get("tests", [])

    def get_study_biomaterials(self, study_name: str) -> List[str]:
        """Получает список биоматериалов для исследования."""
        study = self.get_study_info(study_name)
        return study.get("biomaterials", [])

    def get_preferred_biomaterial(self, study_name: str) -> str:
        """Получает предпочтительный биоматериал для исследования."""
        study = self.get_study_info(study_name)
        return study.get("preferred_biomaterial", study.get("biomaterials", [])[0] if study.get("biomaterials") else "")

    def get_test_reference(self, test_name: str, biomaterial_type: str, 
                          sex: Optional[str] = None, age: Optional[float] = None) -> Dict[str, Any]:
        """Получает референс для теста из указанного биоматериала."""
        manager = self._get_biomaterial_manager(biomaterial_type)
        reference = manager.get_reference(test_name)
        return reference.get_reference(sex, age)

    def check_test_value(self, test_name: str, value: float, biomaterial_type: str,
                        sex: Optional[str] = None, age: Optional[float] = None) -> str:
        """Проверяет значение теста относительно референса биоматериала."""
        manager = self._get_biomaterial_manager(biomaterial_type)
        reference = manager.get_reference(test_name)
        return reference.check_value(value, sex, age)

    def create_study_result(self, study_name: str, biomaterial_type: Optional[str] = None,
                           sex: Optional[str] = None, age: Optional[float] = None) -> 'StudyResult':
        """Создает объект StudyResult для указанного исследования."""
        study = self.get_study_info(study_name)
        
        # Выбираем биоматериал
        if biomaterial_type is None:
            biomaterial_type = self.get_preferred_biomaterial(study_name)
        elif biomaterial_type not in study.get("biomaterials", []):
            raise ValueError(f"Biomaterial '{biomaterial_type}' not available for study '{study_name}'")
        
        return StudyResult(study_name, biomaterial_type, sex, age, self)

    def get_available_tests_for_biomaterial(self, biomaterial_type: str) -> List[str]:
        """Получает список всех доступных тестов для биоматериала."""
        manager = self._get_biomaterial_manager(biomaterial_type)
        return manager.list_tests()

    def find_studies_with_test(self, test_name: str) -> List[str]:
        """Находит все исследования, содержащие указанный тест."""
        studies = []
        for study_name, study_data in self._studies.items():
            for test in study_data.get("tests", []):
                if test.get("test_name") == test_name:
                    studies.append(study_name)
                    break
        return studies

    def __str__(self) -> str:
        return f"LabStudyManager({len(self._studies)} исследований)"

    def __repr__(self) -> str:
        return f"LabStudyManager(studies={len(self._studies)})"


class StudyResult:
    """Класс для представления результатов лабораторного исследования с учетом биоматериала.
    
    Объединяет результаты тестов одного исследования, учитывая тип биоматериала
    и предоставляет методы для анализа и отчетности.
    """
    
    def __init__(self, study_name: str, biomaterial_type: str, 
                 sex: Optional[str] = None, age: Optional[float] = None,
                 study_manager: Optional[LabStudyManager] = None):
        self.study_name = study_name
        self.biomaterial_type = biomaterial_type
        self.sex = sex
        self.age = age
        self.study_manager = study_manager or LabStudyManager()
        self._tests: Dict[str, Test] = {}
        
        # Проверяем, что исследование и биоматериал совместимы
        study_info = self.study_manager.get_study_info(study_name)
        if biomaterial_type not in study_info.get("biomaterials", []):
            raise ValueError(f"Biomaterial '{biomaterial_type}' not available for study '{study_name}'")

    def add_result(self, test_name: str, value: float) -> 'StudyResult':
        """Добавляет результат теста (fluent interface)."""
        # Проверяем, что тест входит в исследование
        study_tests = [t["test_name"] for t in self.study_manager.get_study_tests(self.study_name)]
        if test_name not in study_tests:
            raise ValueError(f"Test '{test_name}' is not part of study '{self.study_name}'")
        
        # Получаем референс из биоматериала
        manager = self.study_manager._get_biomaterial_manager(self.biomaterial_type)
        reference = manager.get_reference(test_name)
        test = Test(reference, value, self.sex, self.age)
        self._tests[test_name] = test
        return self

    def add_results(self, results: Dict[str, float]) -> 'StudyResult':
        """Добавляет несколько результатов тестов (fluent interface)."""
        for test_name, value in results.items():
            self.add_result(test_name, value)
        return self

    def get_test(self, test_name: str) -> Test:
        """Получает объект Test по имени."""
        if test_name not in self._tests:
            raise ValueError(f"No result for test '{test_name}'")
        return self._tests[test_name]

    def get_all_tests(self) -> Dict[str, Test]:
        """Возвращает все тесты."""
        return self._tests.copy()

    def get_abnormal_tests(self) -> Dict[str, Test]:
        """Возвращает только тесты с отклонениями от нормы."""
        return {name: test for name, test in self._tests.items() if test.is_abnormal()}

    def get_normal_tests(self) -> Dict[str, Test]:
        """Возвращает только тесты в пределах нормы."""
        return {name: test for name, test in self._tests.items() if test.is_normal()}

    def has_abnormalities(self) -> bool:
        """Проверяет, есть ли отклонения от нормы."""
        return bool(self.get_abnormal_tests())

    def get_summary(self) -> Dict[str, int]:
        """Возвращает сводку по статусам результатов."""
        summary = {"normal": 0, "below": 0, "above": 0, "total": 0}
        for test in self._tests.values():
            if test.status:
                summary[test.status] += 1
            summary["total"] += 1
        return summary

    def get_study_info(self) -> Dict[str, Any]:
        """Получает информацию об исследовании."""
        return self.study_manager.get_study_info(self.study_name)

    def get_biomaterial_info(self) -> Dict[str, Any]:
        """Получает информацию о биоматериале."""
        manager = self.study_manager._get_biomaterial_manager(self.biomaterial_type)
        return {
            "name": manager.name,
            "description": manager.description,
            "collection_method": manager.collection_method,
            "type": self.biomaterial_type
        }

    def print_report(self, show_only_abnormal: bool = False) -> None:
        """Печатает отчет по результатам исследования."""
        study_info = self.get_study_info()
        biomaterial_info = self.get_biomaterial_info()
        
        print(f"\n=== {study_info.get('name', self.study_name)} ===")
        print(f"Биоматериал: {biomaterial_info['name']} ({biomaterial_info['collection_method']})")
        
        if self.sex or self.age:
            patient_info = []
            if self.sex:
                patient_info.append(f"пол: {self.sex}")
            if self.age:
                patient_info.append(f"возраст: {self.age}")
            print(f"Пациент: {', '.join(patient_info)}")
        
        print()
        tests_to_show = self.get_abnormal_tests() if show_only_abnormal else self._tests
        
        if not tests_to_show:
            print("Нет результатов для отображения")
            return
            
        for test_name, test in tests_to_show.items():
            ref_info = test.get_reference_info()
            status_symbol = {"normal": "✓", "below": "↓", "above": "↑"}.get(test.status, "?")
            print(f"{status_symbol} {test}")
            print(f"   Норма: {ref_info['min']}-{ref_info['max']} {ref_info['unit']}")
            if 'age_min' in ref_info:
                print(f"   Возрастной диапазон: {ref_info['age_min']}-{ref_info['age_max']} лет")
            print()
        
        # Сводка
        summary = self.get_summary()
        print(f"Сводка: {summary['normal']} в норме, {summary['below']} понижено, {summary['above']} повышено")

    def set_patient_info(self, sex: Optional[str] = None, age: Optional[float] = None) -> 'StudyResult':
        """Обновляет информацию о пациенте для всех тестов (fluent interface)."""
        if sex is not None:
            self.sex = sex
        if age is not None:
            self.age = age
        
        for test in self._tests.values():
            test.set_patient_info(sex, age)
        
        return self

    def __len__(self) -> int:
        return len(self._tests)

    def __contains__(self, test_name: str) -> bool:
        return test_name in self._tests

    def __str__(self) -> str:
        return f"StudyResult({self.study_name} на {self.biomaterial_type} - {len(self)} результатов)"

    def __repr__(self) -> str:
        return f"StudyResult(study='{self.study_name}', biomaterial='{self.biomaterial_type}', results={len(self)}, sex='{self.sex}', age={self.age})"