"""Pytest 配置文件 — 提供测试客户端和内存数据库 fixtures."""

import os
import sqlite3
import pytest
from app import create_app

# 共享内存数据库 URI — app 路由和测试夹具共享同一份数据
MEMORY_DB_URI = 'file::memory:?cache=shared'


@pytest.fixture
def app():
    """创建 Flask 测试应用实例.

    使用共享内存数据库, create_app 内部会执行 schema 初始化.
    """
    app = create_app(db_path=MEMORY_DB_URI)
    app.config.update({
        'TESTING': True,
    })
    yield app


@pytest.fixture
def client(app):
    """创建测试客户端."""
    return app.test_client()


@pytest.fixture
def db(app):
    """创建测试用数据库连接, 并确保 schema 已初始化.

    由于 create_app 内部的 _init_database 会在连接关闭后丢失
    共享内存数据库, 此处重新执行 init.sql 并保持连接打开.
    """
    conn = sqlite3.connect(MEMORY_DB_URI, uri=True)
    conn.row_factory = sqlite3.Row

    # 执行 schema 初始化 (CREATE TABLE IF NOT EXISTS 可安全重复执行)
    init_sql_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'db', 'init.sql'
    )
    if os.path.exists(init_sql_path):
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        conn.executescript(sql_script)
    conn.commit()

    yield conn
    conn.close()
