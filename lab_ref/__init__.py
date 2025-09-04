"""lab_ref — утилиты и справочники лабораторных референсов.

Публичные функции доступны напрямую из пространства имён пакета:

    import lab_ref
    lab_ref.get_reference(...)
    lab_ref.print_test_types_report()

См. docstrings у функций для подробной справки.
"""

__version__ = "0.1.0a1"

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
)

__all__ = [
    "validate_references_structure",
    "load_references",
    "list_test_types",
    "get_reference",
    "check_value",
    "print_reference_report",
    "print_test_names_report",
    "get_test_keys",
    "print_test_types_report",
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

