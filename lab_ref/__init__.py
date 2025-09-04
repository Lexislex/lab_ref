"""lab_ref — утилиты и справочники лабораторных референсов.

Публичные функции доступны напрямую из пространства имён пакета:

    import lab_ref
    lab_ref.get_reference(...)
    lab_ref.print_test_types_report()

См. docstrings у функций для подробной справки.
"""

# Функциональный API (основной для простых случаев)
from .utils import (
    validate_references_structure,
    load_references,
    list_test_types,
    get_reference,
    check_value,
    print_reference_report,
    print_test_names_report,
    get_test_keys,
    print_test_types_report,
    # Новые функции для работы с биоматериалами
    list_biomaterials,
    get_biomaterial_reference,
    check_biomaterial_value,
    load_lab_studies,
    list_lab_studies,
    get_study_info,
    get_study_tests,
    get_study_biomaterials,
    get_preferred_biomaterial,
    check_study_values,
    print_biomaterials_report,
    print_lab_studies_report,
    # Функции для работы с пользовательскими папками референсов
    set_references_dir,
    get_current_references_dir,
    reset_references_dir,
    copy_references_template,
)

# ООП API (для сложных сценариев и удобства)
from .models import (
    AgeRange,
    Reference,
    Test,
    ReferenceManager,
    LabResult,
    # Новые классы для работы с биоматериалами
    BiomaterialManager,
    LabStudyManager,
    StudyResult,
)

__all__ = [
    # Функциональный API
    "validate_references_structure",
    "load_references",
    "list_test_types",
    "get_reference",
    "check_value",
    "print_reference_report",
    "print_test_names_report",
    "get_test_keys",
    "print_test_types_report",
    # Новые функции для работы с биоматериалами
    "list_biomaterials",
    "get_biomaterial_reference",
    "check_biomaterial_value",
    "load_lab_studies",
    "list_lab_studies",
    "get_study_info",
    "get_study_tests",
    "get_study_biomaterials",
    "get_preferred_biomaterial",
    "check_study_values",
    "print_biomaterials_report",
    "print_lab_studies_report",
    # Функции для работы с пользовательскими папками референсов
    "set_references_dir",
    "get_current_references_dir",
    "reset_references_dir",
    "copy_references_template",
    # ООП API
    "AgeRange",
    "Reference",
    "Test",
    "ReferenceManager",
    "LabResult",
    # Новые классы для работы с биоматериалами
    "BiomaterialManager",
    "LabStudyManager",
    "StudyResult",
]

# Помечаем ре-экспортированные функции как принадлежащие модулю `lab_ref`,
# чтобы IDE показывали их докстринги в подсказках на верхнем уровне
for _name in __all__:
    _obj = globals().get(_name)
    if hasattr(_obj, "__module__"):
        try:
            _obj.__module__ = __name__
        except Exception:
            pass


