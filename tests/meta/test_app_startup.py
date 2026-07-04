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
    assert "订单系统接口自动化测试项目" in result.stdout


def test_openapi_documentation_is_chinese(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    openapi = response.json()
    assert openapi["info"]["title"] == "订单系统接口自动化测试项目"

    tags = {tag["name"]: tag["description"] for tag in openapi["tags"]}
    assert tags["认证接口"] == "用户注册、登录和 JWT 鉴权。"
    assert tags["商品接口"] == "商品列表和商品详情查询。"
    assert tags["订单接口"] == "订单创建、查询、支付模拟和取消。"

    assert openapi["paths"]["/api/auth/register"]["post"]["summary"] == "用户注册"
    assert openapi["paths"]["/api/orders"]["post"]["summary"] == "创建订单"


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
