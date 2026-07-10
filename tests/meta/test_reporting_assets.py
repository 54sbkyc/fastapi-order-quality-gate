import ast
from pathlib import Path


def test_allure_metadata_generator_defines_interview_context():
    script = Path("scripts/write_allure_metadata.py").read_text(encoding="utf-8")

    for text in [
        "FastAPI Order Quality Gate",
        "Automation Testing Internship",
        "Authentication or Authorization Failure",
        "Business Rule Failure",
        "Coverage Gate",
    ]:
        assert text in script


def test_quality_gate_generates_allure_metadata():
    quality_gate = Path("scripts/quality-gate.ps1").read_text(encoding="utf-8-sig")

    assert "scripts/write_allure_metadata.py" in quality_gate


def test_test_depth_documents_are_linked_from_readme():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "docs/test-case-design.md" in readme
    assert "docs/bug-analysis.md" in readme


def test_allure_categories_json_shape():
    source = Path("scripts/write_allure_metadata.py").read_text(encoding="utf-8")
    start = source.index("CATEGORIES = ") + len("CATEGORIES = ")
    end = source.index("\n\n\ndef write_environment_file")
    categories = ast.literal_eval(source[start:end])

    category_names = {category["name"] for category in categories}
    assert "Authentication or Authorization Failure" in category_names
    assert "Business Rule Failure" in category_names
