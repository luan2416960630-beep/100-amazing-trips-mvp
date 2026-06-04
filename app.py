"""
飞猪「100种不可思议旅行」MVP — Flask 应用入口.

仅包含应用基础框架和配置，不含任何业务路由.
"""

import os
import sqlite3
from flask import Flask
from flask_cors import CORS


def create_app():
    """创建并配置 Flask 应用."""
    app = Flask(__name__)

    # ---- CORS 配置 ----
    CORS(app, resources={r"/*": {"origins": "*"}})

    # ---- 数据库配置 ----
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'db', 'trips.db')
    app.config['DATABASE'] = db_path

    # ---- 数据库自动初始化 ----
    _init_database(app, basedir)

    # ---- 基础错误处理 ----
    @app.errorhandler(404)
    def not_found(error):
        return {'code': 404, 'message': 'Not Found', 'data': None}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'code': 500, 'message': 'Internal Server Error', 'data': None}, 500

    return app


def _init_database(app, basedir):
    """应用启动时自动初始化数据库.

    仅在数据库文件不存在时执行 init.sql 脚本.
    """
    db_path = app.config['DATABASE']

    # 确保 db 目录存在
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)

    # 如果数据库文件已存在则跳过初始化
    if os.path.exists(db_path):
        return

    init_sql_path = os.path.join(basedir, 'db', 'init.sql')
    if not os.path.exists(init_sql_path):
        raise FileNotFoundError(f'数据库初始化脚本未找到: {init_sql_path}')

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    with open(init_sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    conn.executescript(sql_script)
    conn.commit()
    conn.close()


# 模块级别创建应用实例
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
