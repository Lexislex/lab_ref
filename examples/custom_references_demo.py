#!/usr/bin/env python3
"""Демонстрация использования пользовательских папок с референсами.

Этот пример показывает различные способы использования собственных
референсов вместо встроенных в библиотеку.
"""

import os
import tempfile
import lab_ref


def demo_current_references_dir():
    """Демонстрация получения текущей папки с референсами."""
    print("=== ТЕКУЩАЯ ПАПКА С РЕФЕРЕНСАМИ ===\n")
    
    current_dir = lab_ref.get_current_references_dir()
    print(f"Текущая папка с референсами: {current_dir}")
    
    # Показываем доступные файлы
    if os.path.exists(current_dir):
        files = [f for f in os.listdir(current_dir) if f.endswith('.json')]
        print(f"Доступные файлы: {', '.join(files)}")
    
    print("\n" + "="*60 + "\n")


def demo_copy_references_template():
    """Демонстрация копирования шаблона референсов."""
    print("=== КОПИРОВАНИЕ ШАБЛОНА РЕФЕРЕНСОВ ===\n")
    
    # Создаем временную папку для демонстрации
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_refs_dir = os.path.join(temp_dir, "my_references")
        
        print(f"Копируем шаблон в: {custom_refs_dir}")
        copied_files = lab_ref.copy_references_template(custom_refs_dir)
        
        print(f"Скопированные файлы: {', '.join(copied_files)}")
        
        # Проверяем, что файлы действительно скопированы
        if os.path.exists(custom_refs_dir):
            actual_files = os.listdir(custom_refs_dir)
            print(f"Файлы в папке: {', '.join(actual_files)}")
        
        print(f"Всего скопировано файлов: {len(copied_files)}")
    
    print("\n" + "="*60 + "\n")


def demo_set_custom_references_dir():
    """Демонстрация установки пользовательской папки."""
    print("=== УСТАНОВКА ПОЛЬЗОВАТЕЛЬСКОЙ ПАПКИ ===\n")
    
    # Сохраняем текущую папку
    original_dir = lab_ref.get_current_references_dir()
    print(f"Исходная папка: {original_dir}")
    
    # Создаем временную папку с пользовательскими референсами
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_refs_dir = os.path.join(temp_dir, "custom_references")
        
        # Копируем шаблон
        copied_files = lab_ref.copy_references_template(custom_refs_dir)
        print(f"Создана пользовательская папка с {len(copied_files)} файлами")
        
        # Устанавливаем пользовательскую папку
        lab_ref.set_references_dir(custom_refs_dir)
        new_dir = lab_ref.get_current_references_dir()
        print(f"Новая папка: {new_dir}")
        
        # Проверяем, что функции используют новую папку
        try:
            biomaterials = lab_ref.list_biomaterials()
            print(f"Биоматериалы из пользовательской папки: {', '.join(biomaterials)}")
            
            # Проверяем работу с конкретным биоматериалом
            if "venous_blood" in biomaterials:
                ref = lab_ref.get_biomaterial_reference("venous_blood", "hemoglobin", "male", 30)
                print(f"Референс гемоглобина: {ref['min']}-{ref['max']} {ref['unit']}")
        except Exception as e:
            print(f"Ошибка при работе с пользовательской папкой: {e}")
        
        # Сбрасываем к исходной папке
        lab_ref.reset_references_dir()
        reset_dir = lab_ref.get_current_references_dir()
        print(f"После сброса: {reset_dir}")
    
    print("\n" + "="*60 + "\n")


def demo_modify_custom_references():
    """Демонстрация модификации пользовательских референсов."""
    print("=== МОДИФИКАЦИЯ ПОЛЬЗОВАТЕЛЬСКИХ РЕФЕРЕНСОВ ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_refs_dir = os.path.join(temp_dir, "modified_references")
        
        # Копируем шаблон
        lab_ref.copy_references_template(custom_refs_dir)
        
        # Модифицируем один из файлов
        venous_blood_file = os.path.join(custom_refs_dir, "venous_blood.json")
        
        if os.path.exists(venous_blood_file):
            import json
            
            # Читаем существующий файл
            with open(venous_blood_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Добавляем новый тест
            data["custom_test"] = {
                "name_ru": "Пользовательский тест",
                "test_code": "CUSTOM",
                "all": [
                    {"age_min": 0, "age_max": 150, "min": 10, "max": 20, "unit": "custom_unit"}
                ]
            }
            
            # Записываем обратно
            with open(venous_blood_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print("Добавлен пользовательский тест в venous_blood.json")
            
            # Устанавливаем пользовательскую папку
            lab_ref.set_references_dir(custom_refs_dir)
            
            # Проверяем, что новый тест доступен
            try:
                manager = lab_ref.BiomaterialManager("venous_blood")
                tests = manager.list_tests()
                
                if "custom_test" in tests:
                    print("✅ Пользовательский тест успешно добавлен!")
                    
                    # Создаем тест
                    test = manager.create_test("custom_test", 15, age=25)
                    print(f"Результат теста: {test}")
                    print(f"Статус: {test.status}")
                else:
                    print("❌ Пользовательский тест не найден")
                    
            except Exception as e:
                print(f"Ошибка при работе с модифицированными референсами: {e}")
            
            # Сбрасываем
            lab_ref.reset_references_dir()
    
    print("\n" + "="*60 + "\n")


def demo_environment_variable():
    """Демонстрация использования переменной окружения."""
    print("=== ИСПОЛЬЗОВАНИЕ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_refs_dir = os.path.join(temp_dir, "env_references")
        
        # Копируем шаблон
        lab_ref.copy_references_template(custom_refs_dir)
        
        # Устанавливаем переменную окружения напрямую
        old_env = os.environ.get("LAB_REF_DIR")
        os.environ["LAB_REF_DIR"] = custom_refs_dir
        
        print(f"Установлена переменная LAB_REF_DIR: {custom_refs_dir}")
        
        try:
            # Проверяем, что библиотека использует папку из переменной окружения
            current_dir = lab_ref.get_current_references_dir()
            print(f"Библиотека использует папку: {current_dir}")
            
            # Проверяем работу функций
            studies = lab_ref.list_lab_studies()
            print(f"Доступные исследования: {', '.join(studies)}")
            
        finally:
            # Восстанавливаем переменную окружения
            if old_env is not None:
                os.environ["LAB_REF_DIR"] = old_env
            elif "LAB_REF_DIR" in os.environ:
                del os.environ["LAB_REF_DIR"]
    
    print("\n" + "="*60 + "\n")


def demo_explicit_parameter():
    """Демонстрация явного указания папки в функциях."""
    print("=== ЯВНОЕ УКАЗАНИЕ ПАПКИ В ФУНКЦИЯХ ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_refs_dir = os.path.join(temp_dir, "explicit_references")
        
        # Копируем шаблон
        lab_ref.copy_references_template(custom_refs_dir)
        
        print(f"Используем папку явно: {custom_refs_dir}")
        
        try:
            # Используем функции с явным указанием папки
            biomaterials = lab_ref.list_biomaterials(references_dir=custom_refs_dir)
            print(f"Биоматериалы: {', '.join(biomaterials)}")
            
            studies = lab_ref.list_lab_studies(references_dir=custom_refs_dir)
            print(f"Исследования: {', '.join(studies)}")
            
            # Проверяем работу с конкретными функциями
            ref = lab_ref.get_biomaterial_reference(
                "venous_blood", "hemoglobin", "male", 30, 
                references_dir=custom_refs_dir
            )
            print(f"Референс: {ref['min']}-{ref['max']} {ref['unit']}")
            
            # ООП API тоже поддерживает явное указание папки
            manager = lab_ref.BiomaterialManager("venous_blood", references_dir=custom_refs_dir)
            print(f"Менеджер биоматериала: {manager.name}")
            
            study_manager = lab_ref.LabStudyManager(references_dir=custom_refs_dir)
            print(f"Менеджер исследований: {len(study_manager.list_studies())} исследований")
            
        except Exception as e:
            print(f"Ошибка при явном указании папки: {e}")
    
    print("\n" + "="*60 + "\n")


def demo_priority_order():
    """Демонстрация порядка приоритета папок."""
    print("=== ПОРЯДОК ПРИОРИТЕТА ПАПОК ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем несколько папок
        env_refs_dir = os.path.join(temp_dir, "env_references")
        explicit_refs_dir = os.path.join(temp_dir, "explicit_references")
        
        lab_ref.copy_references_template(env_refs_dir)
        lab_ref.copy_references_template(explicit_refs_dir)
        
        # Устанавливаем переменную окружения
        old_env = os.environ.get("LAB_REF_DIR")
        os.environ["LAB_REF_DIR"] = env_refs_dir
        
        try:
            print("Порядок приоритета:")
            print("1. Явный параметр references_dir")
            print("2. Переменная окружения LAB_REF_DIR")
            print("3. Стандартная папка библиотеки")
            print()
            
            # Без явного параметра - должна использоваться переменная окружения
            current_dir = lab_ref.get_current_references_dir()
            print(f"Без параметра (переменная окружения): {os.path.basename(current_dir)}")
            
            # С явным параметром - должна использоваться явная папка
            biomaterials_explicit = lab_ref.list_biomaterials(references_dir=explicit_refs_dir)
            print(f"С явным параметром: используется explicit_references")
            
            # Сбрасываем переменную окружения
            del os.environ["LAB_REF_DIR"]
            
            # Теперь должна использоваться стандартная папка
            current_dir = lab_ref.get_current_references_dir()
            print(f"После сброса переменной: {os.path.basename(current_dir)}")
            
        finally:
            # Восстанавливаем переменную окружения
            if old_env is not None:
                os.environ["LAB_REF_DIR"] = old_env
            elif "LAB_REF_DIR" in os.environ:
                del os.environ["LAB_REF_DIR"]
    
    print("\n" + "="*60 + "\n")


def main():
    """Главная функция демонстрации."""
    print("📁 ДЕМОНСТРАЦИЯ ПОЛЬЗОВАТЕЛЬСКИХ ПАПОК С РЕФЕРЕНСАМИ\n")
    print("Библиотека поддерживает несколько способов использования")
    print("пользовательских референсов вместо встроенных:\n")
    
    try:
        demo_current_references_dir()
        demo_copy_references_template()
        demo_set_custom_references_dir()
        demo_modify_custom_references()
        demo_environment_variable()
        demo_explicit_parameter()
        demo_priority_order()
        
        print("✅ ВСЕ ДЕМОНСТРАЦИИ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("\n🎯 СПОСОБЫ ИСПОЛЬЗОВАНИЯ ПОЛЬЗОВАТЕЛЬСКИХ РЕФЕРЕНСОВ:")
        print("• lab_ref.set_references_dir(path) - глобальная установка")
        print("• os.environ['LAB_REF_DIR'] = path - через переменную окружения")
        print("• func(..., references_dir=path) - явное указание в функциях")
        print("• lab_ref.copy_references_template(path) - копирование шаблона")
        print("\n💡 ПРИОРИТЕТ: явный параметр > переменная окружения > стандартная папка")
        
    except Exception as e:
        print(f"❌ Ошибка во время демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
