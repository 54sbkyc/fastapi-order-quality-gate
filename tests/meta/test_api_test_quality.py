import ast
from pathlib import Path

API_TEST_DIR = Path("tests/api")


def _api_test_functions() -> list[ast.FunctionDef]:
    functions: list[ast.FunctionDef] = []
    for path in API_TEST_DIR.glob("test_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        functions.extend(
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        )
    return functions


def _decorator_name(decorator: ast.expr) -> str:
    if isinstance(decorator, ast.Call):
        return _decorator_name(decorator.func)
    if isinstance(decorator, ast.Attribute):
        parent = _decorator_name(decorator.value)
        return f"{parent}.{decorator.attr}" if parent else decorator.attr
    if isinstance(decorator, ast.Name):
        return decorator.id
    return ""


def test_every_api_test_has_allure_title():
    missing_titles = [
        function.name
        for function in _api_test_functions()
        if not any(
            _decorator_name(decorator) == "allure.title"
            for decorator in function.decorator_list
        )
    ]

    assert missing_titles == []


def test_api_suite_uses_parameterized_cases():
    parametrized_tests = [
        function.name
        for function in _api_test_functions()
        if any(
            _decorator_name(decorator) == "pytest.mark.parametrize"
            for decorator in function.decorator_list
        )
    ]

    assert len(parametrized_tests) >= 3
