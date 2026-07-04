import os
import subprocess
import sys


def test_app_imports_in_clean_python_process():
    result = subprocess.run(
        [sys.executable, "-c", "import app.main; print(app.main.app.title)"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "FastAPI Order Quality Gate" in result.stdout


def test_app_startup_seeds_default_products(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    script = (
        "import app.main\n"
        "from sqlalchemy import select\n"
        "from app.db.session import SessionLocal\n"
        "from app.models.product import Product\n"
        "with SessionLocal() as db:\n"
        "    print(len(db.scalars(select(Product)).all()))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert int(result.stdout.strip()) >= 3
