"""Pytest 配置文件 — 提供测试客户端和内存数据库 fixtures."""

import os
import sqlite3
import pytest
from flask import Flask


@pytest.fixture
def app():
    """创建 Flask 测试应用实例.

    使用内存数据库，确保测试之间数据隔离.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',
    })

    # 基础错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {'code': 404, 'message': 'Not Found', 'data': None}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'code': 500, 'message': 'Internal Server Error', 'data': None}, 500

    yield app


@pytest.fixture
def client(app):
    """创建测试客户端."""
    return app.test_client()


@pytest.fixture
def db(app):
    """创建测试用内存数据库，自动执行初始化脚本.

    每次测试前重建表结构，确保测试隔离.
    """
    # 读取 init.sql 文件路径
    init_sql_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'db', 'init.sql'
    )

    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    # 执行初始化脚本
    if os.path.exists(init_sql_path):
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        conn.executescript(sql_script)
    conn.commit()

    yield conn
    conn.close()
