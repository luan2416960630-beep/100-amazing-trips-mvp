# 100种不可思议旅行

> 发现你从未想过可以这样旅行

[![Flask](https://img.shields.io/badge/Flask-3.1.0-000000?logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.45+-003B57?logo=sqlite)](https://www.sqlite.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v3-06B6D4?logo=tailwindcss)](https://tailwindcss.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![pytest](https://img.shields.io/badge/pytest-8.4.0-0A9EDC?logo=pytest)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

飞猪「100种不可思议旅行」是一个面向 95后-00后 Z 世代和视觉系内容消费者的**小众旅行发现平台**。平台专注于极致、不可思议的非主流旅行体验，以暗黑高对比度的沉浸式 UI 设计和三维审美筛选体系，重新定义了旅行内容的浏览方式。

---

## 项目背景

传统旅行平台内容同质化严重——首页千篇一律的热门景点和酒店推荐，筛选维度局限于价格、星级和目的地。Z 世代用户渴望发现独特、小众、能产出高质量视觉内容的旅行体验，但这些内容分散在各个社交平台，缺少统一的聚合入口。

「100种不可思议旅行」应运而生：**不是「卖出更多旅行产品」，而是「激发探索未知的渴望」**。

### 目标用户

- **Z 世代探索者（95后-00后）**：数字原住民，旅行决策受视觉内容驱动
- **反常规生活方式追求者**：厌倦热门景点打卡，渴望深度独特体验
- **视觉系内容消费者**：对图片质量有高要求，浏览本身就是审美享受

---

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 运行环境 |
| Flask | 3.1.0 | Web 框架，路由处理 |
| SQLite | 3.45+ (内置) | 数据库，JSONB 支持多值字段，FTS5 全文搜索 |
| flask-cors | 5.0.1 | 跨域资源共享 |
| pytest | 8.4.0 | 测试框架 |
| pytest-flask | 1.3.0 | Flask 测试工具 |

### 前端

| 技术 | 用途 |
|------|------|
| HTML5 | 页面结构 |
| Tailwind CSS v3 | 原子化 CSS 框架，CDN 引入 |
| 原生 JavaScript (ES6) | Fetch API 数据请求、DOM 操作、交互动画 |
| Inter 字体 | Google Fonts，屏幕阅读优化无衬线字体 |

### 设计与工具

| 工具 | 用途 |
|------|------|
| OpenAPI 3.0.3 | API 接口契约规范 |
| Claude Code | AI 辅助开发：PRD → 设计 → 编码 → 测试全流程 |

---

## 核心功能

- **旅行列表展示**：响应式瀑布流布局（手机 1 列 / 平板 2 列 / 桌面 3 列），暗黑高对比度 UI（`#0a0a0a` 背景 + `#ffffff` 文字 + `#00f0ff` 品牌色），图片 16:9 卡片 + 渐变遮罩文字叠加
- **三维审美筛选**：体验类型（9 项）、视觉风格（7 项）、小众程度（3 项），同维度多值取并集，跨维度取交集，筛选结果实时更新
- **关键词搜索**：300ms 防抖，匹配标题、副标题、目的地，支持中文分词
- **无限滚动分页**：滚动距底部 200px 自动加载下一页，骨架屏加载态 + "没有更多内容了"终止态
- **旅行详情页**：100vh 全屏英雄区 + 触摸/拖拽图片轮播（自动播放 + 圆点指示器）+ 实用信息优先布局 + 故事叙述 + 体验亮点 + 适合人群
- **统一错误处理**：网络错误、404、500 分类处理，暗黑风格错误提示 + 重试/返回按钮
- **暗黑沉浸式设计**：毛玻璃导航栏（`backdrop-filter: blur(20px)`）、图片懒加载 500ms 淡入、300ms ease-out-cubic 统一缓动、卡片悬停 `translateY(-8px)` + 荧光蓝光晕

---

## 本地运行指南

### 前置要求

- Python 3.10 或更高版本
- Git（可选，用于克隆仓库）

### 安装与启动

```bash
# 1. 进入项目目录
cd 100-amazing-trips-mvp

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动后端服务
python app.py

# 6. 访问前端页面
# 在浏览器中直接打开项目根目录下的 index.html 即可
# 后端 API 运行在 http://localhost:5000
```

### 常见问题

**端口 5000 被占用**
```bash
# 修改 app.py 最后一行中的端口号，如改为 5001：
app.run(host='0.0.0.0', port=5001, debug=True)
# 同时更新 index.html 和 detail.html 中的 API_BASE 变量
```

**依赖安装失败**
```bash
# 确保使用最新版本的 pip
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 项目结构

```
100-amazing-trips-mvp/
├── app.py                  # Flask 应用入口，3 个 API 路由实现
├── requirements.txt        # Python 依赖清单（固定版本）
├── .gitignore              # Git 忽略配置
├── README.md               # 本文件
├── db/
│   └── init.sql            # 数据库初始化脚本（trips 表 21 字段 + FTS5 + 6 触发器 + 3 索引）
├── tests/
│   ├── __init__.py          # 测试包标记
│   ├── conftest.py          # Pytest fixtures（app/client/db）
│   └── test_api.py          # 33 个 API 接口测试用例
├── docs/                    # 文档目录
├── static/                  # 静态资源
│   ├── css/
│   └── js/
└── templates/               # Flask 模板目录
```

### 项目根目录（顶层交付物）

```
100traveling MVP/
├── PRD-100种不可思议旅行-MVP.md     # MVP 产品需求文档（11 章）
├── design-system.md                  # UI 设计风格规范（11 章 + CSS Tokens）
├── database-schema.sql               # 数据库模型（含样例数据 + 查询示例）
├── api-spec.yaml                     # OpenAPI 3.0.3 接口规范
├── index.html                        # 首页（API 对接版）
└── detail.html                       # 详情页（API 对接版）
```

---

## API 文档

项目严格遵循 OpenAPI 3.0.3 规范，共 3 个接口：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/trips` | GET | 旅行列表（分页 + 三维筛选 + 关键词搜索 + 排序） |
| `/api/trips/{id}` | GET | 旅行详情（全部 21 字段 + JSON 解析） |
| `/api/filters` | GET | 筛选标签枚举（3 维度 × 完整枚举值） |

全部接口返回统一三层结构：`{"code": 200, "message": "success", "data": {...}}`

完整的 OpenAPI 文档见项目根目录下的 `api-spec.yaml`，可导入 Postman 或 Swagger UI 查看交互式文档。

---

## 测试

项目采用 **TDD（测试驱动开发）** 模式，所有接口先编写测试用例，再实现业务代码。

```bash
# 运行全部测试
pytest tests/ -v

# 仅运行 API 测试
pytest tests/test_api.py -v

# 查看测试覆盖率
pytest tests/test_api.py -v --tb=short
```

### 测试覆盖

| 接口 | 测试用例数 | 覆盖场景 |
|------|-----------|----------|
| `GET /api/trips` | 19 | 默认分页、分页边界、单维度筛选 ×3、三维组合交集、多值 OR 筛选 ×2、关键词搜索（命中 + 无结果）、排序 ×2、参数错误 ×3、空数据 |
| `GET /api/trips/{id}` | 7 | 正常获取、404 不存在、非数字 ID→400、ID=0→400、字段完整性、media_list 结构、gallery_images 结构、related_experiences 结构 |
| `GET /api/filters` | 6 | 正常返回、3 维度枚举值完整性、无重复值、content-type 验证 |
| **合计** | **33** | **100% 覆盖核心业务逻辑** |

---

## 开发流程

本项目采用 **SDD → DDD → TDD → E2E** 的 AI 辅助开发流程，全程使用 Claude Code 作为 AI 辅助开发工具，由 AI 生成代码并通过自动化测试验证。

```
┌─────────────────────────────────────────────────────────┐
│  SDD (Specification-Driven Development)                │
│  文档驱动开发                                           │
│  ├── PRD: 产品需求文档（11 章，严格 MVP 范围界定）        │
│  ├── 设计规范: 颜色/字体/间距/动画/组件/响应式（11 章）    │
│  └── 数据字典: 21 字段完整定义 + 枚举值                  │
├─────────────────────────────────────────────────────────┤
│  DDD (Data-Driven Development)                         │
│  数据驱动开发                                           │
│  ├── database-schema.sql: trips 表 + FTS5 + 3 索引      │
│  └── api-spec.yaml: OpenAPI 3.0.3, 3 接口 + 15 schemas  │
├─────────────────────────────────────────────────────────┤
│  TDD (Test-Driven Development)                        │
│  测试驱动开发                                           │
│  ├── test_api.py: 33 测试用例，全部 FAIL（红灯）         │
│  └── app.py: 实现路由 → 33 测试全部 PASS（绿灯）        │
├─────────────────────────────────────────────────────────┤
│  E2E (End-to-End)                                      │
│  端到端对接                                             │
│  ├── index.html: Fetch API 对接 /api/trips             │
│  └── detail.html: Fetch API 对接 /api/trips/{id}       │
└─────────────────────────────────────────────────────────┘
```

### 开发流程亮点

1. **AI 全流程参与**：从 PRD 撰写到代码实现，全程由 Claude Code 辅助完成，人工负责需求确认和代码审查
2. **契约先行**：API 接口规范（OpenAPI 3.0.3）在编码前定义完成，前后端可并行开发
3. **真 TDD**：先写 33 个失败测试 → 再实现业务逻辑 → 全部通过，保证代码质量
4. **设计规范驱动**：UI 设计规范定义了 5 级文字层级、8px 网格、统一缓动函数，前端实现零偏差

---

## 交付物清单

| 类别 | 文件 | 说明 |
|------|------|------|
| 产品文档 | `PRD-100种不可思议旅行-MVP.md` | 11 章 MVP 产品需求文档 |
| 设计规范 | `design-system.md` | UI 设计风格规范 + CSS Design Tokens |
| 数据模型 | `database-schema.sql` | trips 表（21 字段 + 约束 + 索引 + FTS5） |
| API 契约 | `api-spec.yaml` | OpenAPI 3.0.3 规范（3 接口 + 15 schemas） |
| 后端代码 | `app.py` | Flask 应用（3 路由 + 参数校验 + JSON 解析） |
| 数据库 | `db/init.sql` | 纯 DDL 初始化脚本（无 INSERT） |
| 前端首页 | `index.html` | Tailwind CSS + 原生 JS + API 对接 |
| 前端详情 | `detail.html` | 全屏英雄区 + 图片轮播 + 滚动入场动画 |
| 测试用例 | `tests/test_api.py` | 33 个测试用例（19+7+6+1） |
| 测试配置 | `tests/conftest.py` | Pytest fixtures（共享内存数据库） |
| 项目说明 | `README.md` | 本文件 |

---

## 设计特色

本项目采用**暗黑沉浸式图片剧场**设计理念，与传统旅行 App 形成鲜明差异：

| 维度 | 本设计 | 传统旅行 App |
|------|--------|-------------|
| 背景色 | 深黑 `#0a0a0a` | 白色/浅灰 |
| 品牌色 | 单一荧光蓝 `#00f0ff` | 多色系（红橙黄绿） |
| 筛选维度 | 体验类型 × 视觉风格 × 小众程度 | 目的地 × 价格 × 星级 |
| CTA 按钮 | 仅工具性按钮（重试、清除筛选） | 「立即预订」「限时抢购」 |
| 动画 | 统一 300ms ease-out-cubic | 各组件动画独立配置 |
| 空间感 | 大量留白 + 无阴影扁平化 | 卡片分割 + 多层阴影 |

---

## 许可证

MIT License — 详见 [LICENSE](LICENSE) 文件。

---

*由 Claude Code 辅助生成 · 2026年6月*
