# 100种不可思议旅行 — MVP 后端服务

飞猪「100种不可思议旅行」MVP 后端 API 服务。

## 技术栈

- **Python** 3.10+
- **Flask** 3.1.0
- **SQLite** 3.45.0+ (Python 内置)
- **Pytest** 8.4.0

## 环境搭建

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

## 启动服务

```bash
python app.py
```

服务启动后访问: `http://localhost:5000`

## 运行测试

```bash
pytest tests/ -v
```

## 项目结构

```
100-amazing-trips-mvp/
├── app.py              # 主应用入口
├── requirements.txt    # Python 依赖
├── .gitignore          # Git 忽略配置
├── README.md           # 项目说明
├── db/
│   └── init.sql        # 数据库初始化脚本
├── tests/              # 测试用例
│   ├── __init__.py
│   └── conftest.py     # Pytest 配置
├── docs/               # 文档
├── static/             # 静态文件
│   ├── css/
│   └── js/
└── templates/          # HTML 模板
```
