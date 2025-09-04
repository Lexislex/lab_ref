#!/usr/bin/env python3
"""Демонстрация гибридного подхода в библиотеке lab_ref.

Этот пример показывает, как использовать функциональный и ООП API
в зависимости от сложности задачи.
"""

import lab_ref


def demo_functional_api():
    """Демонстрация функционального API для простых случаев."""
    print("=== ФУНКЦИОНАЛЬНЫЙ API (для простых случаев) ===\n")
    
    # Быстрая проверка одного значения
    print("1. Быстрая проверка одного показателя:")
    status = lab_ref.check_value("blood_test", "hemoglobin", 145, sex="male", age=30)
    print(f"   lab_ref.check_value(...) -> {status}")
    
    # Получение референса
    print("\n2. Получение референсной информации:")
    ref = lab_ref.get_reference("blood_test", "hemoglobin", sex="male", age=30)
    print(f"   Референс: {ref['min']}-{ref['max']} {ref['unit']}")
    
    # Проверка нескольких значений сразу
    print("\n3. Проверка нескольких показателей:")
    results = lab_ref.check_value(
        "blood_test",
        {"hemoglobin": 125, "leukocytes": 5.5},
        sex="male",
        age=30
    )
    print(f"   Результаты: {results}")
    
    print("\n" + "="*60 + "\n")


def demo_oop_api():
    """Демонстрация ООП API для сложных сценариев."""
    print("=== ООП API (для сложных сценариев) ===\n")
    
    # Создание менеджера референсов
    print("1. Работа с менеджером референсов:")
    manager = lab_ref.ReferenceManager("blood_test")
    print(f"   Справочник: {manager.name}")
    print(f"   Доступные показатели: {len(manager)} штук")
    print(f"   Список: {', '.join(manager.list_tests()[:3])}...")
    
    # Создание отдельного теста
    print("\n2. Создание отдельного теста:")
    test = manager.create_test("hemoglobin", 145, "male", 30)
    print(f"   Тест: {test}")
    print(f"   Статус: {test.status}")
    print(f"   В норме: {test.is_normal()}")
    
    # Работа с результатами анализов
    print("\n3. Обработка результатов целого анализа:")
    lab_result = lab_ref.LabResult("blood_test", sex="male", age=35)
    lab_result.add_results({
        "hemoglobin": 120,  # пониженный
        "leukocytes": 6.5   # нормальный
    })
    
    print(f"   Результатов: {len(lab_result)}")
    print(f"   Есть отклонения: {lab_result.has_abnormalities()}")
    
    # Анализ отклонений
    abnormal = lab_result.get_abnormal_tests()
    print(f"   Отклонения: {list(abnormal.keys())}")
    
    summary = lab_result.get_summary()
    print(f"   Сводка: {summary}")
    
    print("\n" + "="*60 + "\n")


def demo_fluent_interface():
    """Демонстрация fluent interface."""
    print("=== FLUENT INTERFACE (цепочки вызовов) ===\n")
    
    # Создание результата через цепочку вызовов
    result = (lab_ref.LabResult("blood_test")
              .set_patient_info("female", 28)
              .add_result("hemoglobin", 110)  # пониженный для женщин
              .add_result("leukocytes", 4.5))
    
    print("Результат создан через цепочку вызовов:")
    print(f"  Пациент: {result.sex}, {result.age} лет")
    print(f"  Показателей: {len(result)}")
    print(f"  Отклонения: {result.has_abnormalities()}")
    
    # Fluent interface для отдельного теста
    manager = lab_ref.ReferenceManager("blood_test")
    test = (manager.create_test("hemoglobin")
            .set_value(160)
            .set_patient_info("female", 30))
    
    print(f"\nОтдельный тест: {test}")
    
    print("\n" + "="*60 + "\n")


def demo_integration():
    """Демонстрация интеграции функционального и ООП подходов."""
    print("=== ИНТЕГРАЦИЯ ПОДХОДОВ ===\n")
    
    # ООП объект использует функциональный API
    result = lab_ref.LabResult("blood_test", "male", 30)
    
    print("1. ООП объект вызывает функциональный API:")
    functional_status = result.check_value_functional("hemoglobin", 145)
    print(f"   Функциональный результат: {functional_status}")
    
    # Сравнение результатов
    result.add_result("hemoglobin", 145)
    oop_status = result.get_test("hemoglobin").status
    print(f"   ООП результат: {oop_status}")
    print(f"   Результаты совпадают: {functional_status == oop_status}")
    
    print("\n2. Использование ООП для получения данных, функций для вывода:")
    # Получаем данные через ООП
    manager = lab_ref.ReferenceManager("blood_test")
    
    # Выводим отчет через функциональный API
    print("   Отчет через функциональный API:")
    lab_ref.print_reference_report("blood_test")
    
    print("\n" + "="*60 + "\n")


def demo_when_to_use_what():
    """Рекомендации по выбору подхода."""
    print("=== КОГДА ЧТО ИСПОЛЬЗОВАТЬ ===\n")
    
    print("🔧 ФУНКЦИОНАЛЬНЫЙ API - используйте для:")
    print("   • Быстрой проверки одного-двух показателей")
    print("   • Получения справочной информации")
    print("   • Простых скриптов и разовых задач")
    print("   • Интеграции в существующий функциональный код")
    
    print("\n📦 ООП API - используйте для:")
    print("   • Обработки результатов целых анализов")
    print("   • Работы с множественными пациентами")
    print("   • Сложной бизнес-логики")
    print("   • Приложений с состоянием")
    print("   • Когда нужны отчеты и аналитика")
    
    print("\n💡 ПРИМЕРЫ ВЫБОРА:")
    
    print("\n   Задача: Проверить один показатель")
    print("   ✅ Функциональный: lab_ref.check_value('blood_test', 'hemoglobin', 145)")
    print("   ❌ ООП: слишком сложно для простой задачи")
    
    print("\n   Задача: Обработать результаты анализа пациента")
    print("   ❌ Функциональный: много повторяющегося кода")
    print("   ✅ ООП: LabResult с методами анализа и отчетности")
    
    print("\n   Задача: Веб-приложение с пациентами")
    print("   ✅ ООП: удобное состояние, методы, интеграция с ORM")
    
    print("\n   Задача: CLI утилита для быстрой проверки")
    print("   ✅ Функциональный: минимум кода, быстрый результат")
    
    print("\n" + "="*60 + "\n")


def demo_real_world_scenarios():
    """Реальные сценарии использования."""
    print("=== РЕАЛЬНЫЕ СЦЕНАРИИ ===\n")
    
    print("📋 Сценарий 1: Медицинская лаборатория")
    print("   Обрабатывает сотни анализов в день")
    
    # Функциональный подход для быстрой проверки
    print("\n   Быстрая проверка критических показателей:")
    critical_hemoglobin = lab_ref.check_value("blood_test", "hemoglobin", 80, "female", 45)
    if critical_hemoglobin == "below":
        print("   🚨 КРИТИЧЕСКИ низкий гемоглобин! Требуется внимание врача")
    
    # ООП подход для полного анализа
    print("\n   Полный анализ пациента:")
    patient_results = lab_ref.LabResult("blood_test", "female", 45)
    patient_results.add_results({
        "hemoglobin": 80,
        "leukocytes": 12.5  # повышенный
    })
    
    if patient_results.has_abnormalities():
        print("   📊 Найдены отклонения, генерируем отчет...")
        abnormal = patient_results.get_abnormal_tests()
        for name, test in abnormal.items():
            print(f"      • {test.name_ru}: {test.value} [{test.status}]")
    
    print("\n🏥 Сценарий 2: Персональное здоровье")
    print("   Пользователь отслеживает свои показатели")
    
    # Создаем профиль пользователя
    user_profile = lab_ref.LabResult("blood_test", "male", 32)
    
    # Добавляем результаты за разные периоды
    print("\n   Отслеживание динамики:")
    monthly_results = [
        {"hemoglobin": 140, "leukocytes": 6.0},  # январь
        {"hemoglobin": 135, "leukocytes": 5.8},  # февраль
        {"hemoglobin": 145, "leukocytes": 6.2},  # март
    ]
    
    for i, results in enumerate(monthly_results, 1):
        month_result = lab_ref.LabResult("blood_test", "male", 32)
        month_result.add_results(results)
        summary = month_result.get_summary()
        print(f"      Месяц {i}: {summary['normal']} в норме, {summary['below'] + summary['above']} отклонений")
    
    print("\n🔬 Сценарий 3: Исследовательская работа")
    print("   Анализ данных для научной статьи")
    
    # Функциональный подход для массовой обработки
    print("\n   Обработка данных 1000 пациентов:")
    sample_data = [
        ("male", 25, 145), ("female", 30, 125), ("male", 45, 150)
    ]
    
    results_distribution = {"normal": 0, "below": 0, "above": 0}
    for sex, age, hb_value in sample_data:
        status = lab_ref.check_value("blood_test", "hemoglobin", hb_value, sex, age)
        results_distribution[status] += 1
    
    print(f"      Распределение: {results_distribution}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Главная функция демонстрации."""
    print("🩺 ДЕМОНСТРАЦИЯ ГИБРИДНОГО ПОДХОДА В LAB_REF\n")
    print("Библиотека предоставляет два API для разных сценариев:\n")
    
    try:
        demo_functional_api()
        demo_oop_api()
        demo_fluent_interface()
        demo_integration()
        demo_when_to_use_what()
        demo_real_world_scenarios()
        
        print("✅ ВСЕ ДЕМОНСТРАЦИИ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("\nТеперь вы можете выбирать подходящий API для ваших задач:")
        print("• Простые проверки → Функциональный API")
        print("• Сложная обработка → ООП API")
        print("• Интеграция → Гибридный подход")
        
    except Exception as e:
        print(f"❌ Ошибка во время демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
