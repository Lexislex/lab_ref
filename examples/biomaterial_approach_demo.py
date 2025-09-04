#!/usr/bin/env python3
"""Демонстрация новой архитектуры с биоматериалами в библиотеке lab_ref.

Этот пример показывает, как использовать новую функциональность для работы
с биоматериалами и лабораторными исследованиями.
"""

import lab_ref


def demo_biomaterial_functional_api():
    """Демонстрация функционального API для работы с биоматериалами."""
    print("=== ФУНКЦИОНАЛЬНЫЙ API ДЛЯ БИОМАТЕРИАЛОВ ===\n")
    
    # Получение списка доступных биоматериалов
    print("1. Доступные биоматериалы:")
    biomaterials = lab_ref.list_biomaterials()
    print(f"   {', '.join(biomaterials)}")
    
    # Получение референса для теста из конкретного биоматериала
    print("\n2. Референс гемоглобина для венозной крови:")
    ref = lab_ref.get_biomaterial_reference("venous_blood", "hemoglobin", sex="male", age=30)
    print(f"   Венозная кровь: {ref['min']}-{ref['max']} {ref['unit']}")
    
    # Сравнение с капиллярной кровью
    ref_cap = lab_ref.get_biomaterial_reference("capillary_blood", "hemoglobin", sex="male", age=30)
    print(f"   Капиллярная кровь: {ref_cap['min']}-{ref_cap['max']} {ref_cap['unit']}")
    
    # Проверка значения для разных биоматериалов
    print("\n3. Проверка значения 140 г/л для мужчины 30 лет:")
    status_venous = lab_ref.check_biomaterial_value("venous_blood", "hemoglobin", 140, "male", 30)
    status_capillary = lab_ref.check_biomaterial_value("capillary_blood", "hemoglobin", 140, "male", 30)
    print(f"   Венозная кровь: {status_venous}")
    print(f"   Капиллярная кровь: {status_capillary}")
    
    print("\n" + "="*60 + "\n")


def demo_lab_studies_functional_api():
    """Демонстрация функционального API для лабораторных исследований."""
    print("=== ФУНКЦИОНАЛЬНЫЙ API ДЛЯ ЛАБОРАТОРНЫХ ИССЛЕДОВАНИЙ ===\n")
    
    # Получение списка доступных исследований
    print("1. Доступные лабораторные исследования:")
    studies = lab_ref.list_lab_studies()
    print(f"   {', '.join(studies)}")
    
    # Информация о конкретном исследовании
    print("\n2. Информация об общем анализе крови:")
    study_info = lab_ref.get_study_info("blood_test")
    print(f"   Название: {study_info['name']}")
    print(f"   Биоматериалы: {', '.join(study_info['biomaterials'])}")
    print(f"   Предпочтительный: {study_info['preferred_biomaterial']}")
    
    # Получение тестов исследования
    tests = lab_ref.get_study_tests("blood_test")
    required_tests = [t["test_name"] for t in tests if t.get("required", False)]
    print(f"   Обязательные тесты: {', '.join(required_tests)}")
    
    # Проверка значений для исследования
    print("\n3. Проверка результатов общего анализа крови:")
    test_values = {
        "hemoglobin": 125,  # пониженный
        "leukocytes": 7.5   # нормальный
    }
    
    results = lab_ref.check_study_values("blood_test", test_values, sex="male", age=30)
    for test_name, status in results.items():
        print(f"   {test_name}: {status}")
    
    print("\n" + "="*60 + "\n")


def demo_biomaterial_oop_api():
    """Демонстрация ООП API для работы с биоматериалами."""
    print("=== ООП API ДЛЯ БИОМАТЕРИАЛОВ ===\n")
    
    # Создание менеджера биоматериала
    print("1. Работа с менеджером венозной крови:")
    venous_manager = lab_ref.BiomaterialManager("venous_blood")
    print(f"   Биоматериал: {venous_manager.name}")
    print(f"   Способ взятия: {venous_manager.collection_method}")
    print(f"   Доступные тесты: {len(venous_manager)} штук")
    
    # Создание теста
    print("\n2. Создание теста для глюкозы:")
    glucose_test = venous_manager.create_test("glucose", 5.8, "female", 25)
    print(f"   Тест: {glucose_test}")
    print(f"   Статус: {glucose_test.status}")
    
    # Сравнение с другим биоматериалом
    print("\n3. Сравнение с артериальной кровью:")
    arterial_manager = lab_ref.BiomaterialManager("arterial_blood")
    print(f"   Артериальная кровь: {arterial_manager.name}")
    print(f"   Доступные тесты: {', '.join(arterial_manager.list_tests())}")
    
    print("\n" + "="*60 + "\n")


def demo_lab_study_manager():
    """Демонстрация ООП API для лабораторных исследований."""
    print("=== ООП API ДЛЯ ЛАБОРАТОРНЫХ ИССЛЕДОВАНИЙ ===\n")
    
    # Создание менеджера исследований
    print("1. Работа с менеджером лабораторных исследований:")
    study_manager = lab_ref.LabStudyManager()
    print(f"   Доступные исследования: {', '.join(study_manager.list_studies())}")
    
    # Получение информации о биохимии крови
    print("\n2. Информация о биохимическом анализе:")
    biochemistry_info = study_manager.get_study_info("blood_biochemistry")
    print(f"   Название: {biochemistry_info['name']}")
    print(f"   Биоматериалы: {', '.join(biochemistry_info['biomaterials'])}")
    
    # Проверка отдельного теста
    print("\n3. Проверка креатинина в венозной крови:")
    creatinine_status = study_manager.check_test_value(
        "creatinine", 95, "venous_blood", sex="male", age=40
    )
    print(f"   Креатинин 95 мкмоль/л: {creatinine_status}")
    
    # Поиск исследований с определенным тестом
    print("\n4. Исследования, содержащие гемоглобин:")
    studies_with_hb = study_manager.find_studies_with_test("hemoglobin")
    print(f"   {', '.join(studies_with_hb)}")
    
    print("\n" + "="*60 + "\n")


def demo_study_result():
    """Демонстрация класса StudyResult."""
    print("=== РЕЗУЛЬТАТЫ ЛАБОРАТОРНОГО ИССЛЕДОВАНИЯ ===\n")
    
    # Создание результата исследования
    print("1. Создание результата общего анализа крови:")
    study_manager = lab_ref.LabStudyManager()
    blood_result = study_manager.create_study_result(
        "blood_test", "capillary_blood", "female", 28
    )
    print(f"   Исследование: {blood_result}")
    
    # Добавление результатов
    print("\n2. Добавление результатов анализов:")
    blood_result.add_results({
        "hemoglobin": 110,  # пониженный для женщин
        "leukocytes": 5.5   # нормальный
    })
    
    # Анализ результатов
    print(f"   Всего результатов: {len(blood_result)}")
    print(f"   Есть отклонения: {blood_result.has_abnormalities()}")
    
    abnormal = blood_result.get_abnormal_tests()
    for name, test in abnormal.items():
        print(f"   Отклонение: {test}")
    
    # Информация о биоматериале
    print("\n3. Информация о биоматериале:")
    biomaterial_info = blood_result.get_biomaterial_info()
    print(f"   Биоматериал: {biomaterial_info['name']}")
    print(f"   Способ взятия: {biomaterial_info['collection_method']}")
    
    # Печать отчета
    print("\n4. Отчет по результатам:")
    blood_result.print_report()
    
    print("\n" + "="*60 + "\n")


def demo_comparison_biomaterials():
    """Демонстрация сравнения результатов для разных биоматериалов."""
    print("=== СРАВНЕНИЕ БИОМАТЕРИАЛОВ ===\n")
    
    print("Сравнение гемоглобина для разных способов взятия крови:")
    print("Пациент: мужчина, 35 лет, значение 135 г/л\n")
    
    # Проверяем для разных биоматериалов
    biomaterials = ["capillary_blood", "venous_blood"]
    
    for biomaterial in biomaterials:
        try:
            manager = lab_ref.BiomaterialManager(biomaterial)
            test = manager.create_test("hemoglobin", 135, "male", 35)
            ref_info = test.get_reference_info()
            
            print(f"📋 {manager.name}:")
            print(f"   Способ взятия: {manager.collection_method}")
            print(f"   Референс: {ref_info['min']}-{ref_info['max']} {ref_info['unit']}")
            print(f"   Результат: {test.status}")
            
            status_symbol = {"normal": "✅", "below": "⬇️", "above": "⬆️"}.get(test.status, "❓")
            print(f"   Оценка: {status_symbol}")
            print()
        except Exception as e:
            print(f"❌ Ошибка для {biomaterial}: {e}\n")
    
    print("="*60 + "\n")


def demo_reports():
    """Демонстрация отчетов."""
    print("=== ОТЧЕТЫ ===\n")
    
    print("1. Отчет по биоматериалам:")
    lab_ref.print_biomaterials_report()
    print()
    
    print("2. Отчет по лабораторным исследованиям:")
    lab_ref.print_lab_studies_report()
    
    print("="*60 + "\n")


def demo_real_world_scenarios():
    """Реальные сценарии использования новой архитектуры."""
    print("=== РЕАЛЬНЫЕ СЦЕНАРИИ С БИОМАТЕРИАЛАМИ ===\n")
    
    print("🏥 Сценарий 1: Выбор биоматериала для исследования")
    print("   Пациент: ребенок 5 лет, нужен общий анализ крови")
    
    study_manager = lab_ref.LabStudyManager()
    available_biomaterials = study_manager.get_study_biomaterials("blood_test")
    preferred = study_manager.get_preferred_biomaterial("blood_test")
    
    print(f"   Доступные биоматериалы: {', '.join(available_biomaterials)}")
    print(f"   Предпочтительный: {preferred}")
    
    # Для ребенка лучше капиллярная кровь
    child_result = study_manager.create_study_result("blood_test", "capillary_blood", age=5)
    child_result.add_results({"hemoglobin": 125, "leukocytes": 8.5})
    
    print("   Результаты для капиллярной крови:")
    summary = child_result.get_summary()
    print(f"   {summary['normal']} в норме, {summary['below'] + summary['above']} отклонений")
    
    print("\n🔬 Сценарий 2: Исследование газов крови")
    print("   Пациент в реанимации, нужна оценка кислотно-щелочного состояния")
    
    gas_result = study_manager.create_study_result("blood_gas_analysis", "arterial_blood", "male", 45)
    gas_result.add_results({
        "ph": 7.32,      # слегка пониженный
        "pco2": 48,      # повышенный
        "po2": 85        # нормальный
    })
    
    print("   Результаты анализа газов:")
    if gas_result.has_abnormalities():
        print("   ⚠️ Обнаружены отклонения:")
        for name, test in gas_result.get_abnormal_tests().items():
            print(f"      • {test.name_ru}: {test.value} [{test.status}]")
    
    print("\n💊 Сценарий 3: Мониторинг биохимических показателей")
    print("   Пациент с диабетом, контроль глюкозы и почечной функции")
    
    biochem_result = study_manager.create_study_result("blood_biochemistry", "venous_blood", "female", 55)
    biochem_result.add_results({
        "glucose": 8.2,      # повышенная
        "creatinine": 95,    # норма
        "urea": 7.8          # норма
    })
    
    print("   Биохимические показатели:")
    biochem_result.print_report(show_only_abnormal=True)
    
    print("\n" + "="*60 + "\n")


def main():
    """Главная функция демонстрации."""
    print("🧪 ДЕМОНСТРАЦИЯ НОВОЙ АРХИТЕКТУРЫ С БИОМАТЕРИАЛАМИ\n")
    print("Новая архитектура позволяет:")
    print("• Работать с референсами по типам биоматериалов")
    print("• Учитывать способы взятия материала")
    print("• Гибко определять состав лабораторных исследований")
    print("• Получать референсы как для отдельных тестов, так и для исследований\n")
    
    try:
        demo_biomaterial_functional_api()
        demo_lab_studies_functional_api()
        demo_biomaterial_oop_api()
        demo_lab_study_manager()
        demo_study_result()
        demo_comparison_biomaterials()
        demo_reports()
        demo_real_world_scenarios()
        
        print("✅ ВСЕ ДЕМОНСТРАЦИИ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("\nПреимущества новой архитектуры:")
        print("• 🎯 Точность: учет способа взятия биоматериала")
        print("• 🔄 Гибкость: легкое добавление новых биоматериалов")
        print("• 📊 Удобство: автоматический выбор подходящего биоматериала")
        print("• 🏥 Практичность: соответствие реальным лабораторным процессам")
        
    except Exception as e:
        print(f"❌ Ошибка во время демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
