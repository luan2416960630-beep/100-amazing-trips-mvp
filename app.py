"""
飞猪「100种不可思议旅行」MVP — Flask 应用入口.

包含 3 个 MVP API 接口:
  GET /api/trips        — 旅行体验列表 (分页+筛选+搜索+排序)
  GET /api/trips/<id>   — 单个旅行体验详情
  GET /api/filters       — 可用筛选标签枚举
"""

import json
import math
import os
import sqlite3

from flask import Flask, g, jsonify, request
from flask_cors import CORS


# ============================================================================
# 常量: 枚举值 & 校验集合
# ============================================================================

VALID_RARITY_LEVELS = {'冷门', '小众', '新兴'}
VALID_SORT_FIELDS = {'created_at', 'rarity_level'}
VALID_ORDERS = {'asc', 'desc'}

# /api/filters 返回的完整枚举 (100% 对齐 api-spec.yaml)
FILTER_EXPERIENCE_TYPES = [
    {'value': '水下', 'label': '水下'},
    {'value': '高空', 'label': '高空'},
    {'value': '极地', 'label': '极地'},
    {'value': '荒野', 'label': '荒野'},
    {'value': '地下', 'label': '地下'},
    {'value': '极限运动', 'label': '极限运动'},
    {'value': '文化沉浸', 'label': '文化沉浸'},
    {'value': '夜间奇观', 'label': '夜间奇观'},
    {'value': '慢旅行', 'label': '慢旅行'},
]

FILTER_VISUAL_STYLES = [
    {'value': '极简', 'label': '极简'},
    {'value': '赛博朋克', 'label': '赛博朋克'},
    {'value': '胶片复古', 'label': '胶片复古'},
    {'value': '高饱和', 'label': '高饱和'},
    {'value': '黑白', 'label': '黑白'},
    {'value': '电影感', 'label': '电影感'},
    {'value': '自然光', 'label': '自然光'},
]

FILTER_RARITY_LEVELS = [
    {'value': '冷门', 'label': '冷门（极少人知道）'},
    {'value': '小众', 'label': '小众（圈内知名）'},
    {'value': '新兴', 'label': '新兴（开始流行但未大众化）'},
]

# ============================================================================
# 辅助函数
# ============================================================================

def error_response(code, message):
    """构建统一错误响应."""
    return {'code': code, 'message': message, 'data': None}, code


def success_response(data):
    """构建统一成功响应."""
    return {'code': 200, 'message': 'success', 'data': data}


def cached_success_response(data):
    """构建带 60 秒缓存的成功响应."""
    resp = jsonify({'code': 200, 'message': 'success', 'data': data})
    resp.headers['Cache-Control'] = 'public, max-age=60'
    return resp


def get_db():
    """获取当前请求的数据库连接 (复用在 g 对象上).

    支持普通文件路径和 URI 模式 (如 file::memory:?cache=shared).
    """
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        if db_path.startswith('file:'):
            conn = sqlite3.connect(db_path, uri=True)
        else:
            conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def parse_json_field(value):
    """安全解析 TEXT 存储的 JSON 字段为 Python 对象."""
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def format_trip_card(row):
    """将数据库行格式化为 TripCard (首页卡片, 9 个必填字段)."""
    return {
        'id': row['id'],
        'title': row['title'],
        'subtitle': row['subtitle'],
        'cover_image': row['cover_image'],
        'experience_type_tags': parse_json_field(row['experience_type_tags']),
        'visual_style_tags': parse_json_field(row['visual_style_tags']),
        'rarity_level': row['rarity_level'],
        'destination': row['destination'],
        'duration': row['duration'],
    }


def format_trip_detail(row):
    """将数据库行格式化为 TripDetail (详情页全部字段)."""
    return {
        'id': row['id'],
        'media_list': parse_json_field(row['media_list']),
        'cover_image': row['cover_image'],
        'destination': row['destination'],
        'destination_region': row['destination_region'],
        'duration': row['duration'],
        'best_season': row['best_season'],
        'difficulty_level': row['difficulty_level'],
        'title': row['title'],
        'subtitle': row['subtitle'],
        'experience_type_tags': parse_json_field(row['experience_type_tags']),
        'visual_style_tags': parse_json_field(row['visual_style_tags']),
        'rarity_level': row['rarity_level'],
        'story_title': row['story_title'],
        'story_highlights': parse_json_field(row['story_highlights']),
        'story_body': row['story_body'],
        'gallery_images': parse_json_field(row['gallery_images']),
        'related_experiences': _format_related_experiences(
            parse_json_field(row['related_experiences'])
        ),
        'recommendation_rule': row['recommendation_rule'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
    }


def _format_related_experiences(related):
    """格式化相关推荐: 确保 JSON 数组内的标签字段被正确解析."""
    if not related:
        return []
    result = []
    for item in related:
        item['experience_type_tags'] = parse_json_field(
            item.get('experience_type_tags')
        )
        item['visual_style_tags'] = parse_json_field(
            item.get('visual_style_tags')
        )
        result.append(item)
    return result


# ============================================================================
# 应用工厂
# ============================================================================

def create_app(db_path=None):
    """创建并配置 Flask 应用.

    Args:
        db_path: 数据库路径. None 时使用默认路径 db/trips.db.
                 测试时可传入 'file::memory:?cache=shared'.
    """
    app = Flask(__name__)

    # ---- CORS 配置 ----
    CORS(app, resources={r"/*": {"origins": "*"}})

    # ---- 数据库配置 ----
    basedir = os.path.abspath(os.path.dirname(__file__))
    if db_path is None:
        db_path = os.path.join(basedir, 'db', 'trips.db')
    app.config['DATABASE'] = db_path

    # ---- 数据库自动初始化 ----
    _init_database(app, basedir)

    # ---- 请求结束自动关闭数据库 ----
    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    # ---- 基础错误处理 ----
    @app.errorhandler(404)
    def not_found(error):
        return {'code': 404, 'message': 'Not Found', 'data': None}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'code': 500, 'message': 'Internal Server Error', 'data': None}, 500

    # ==================================================================
    # API 路由
    # ==================================================================

    # ===== 1. GET /api/trips — 旅行体验列表 =====
    @app.route('/api/trips')
    def list_trips():
        """获取旅行体验列表.

        支持: 分页, 三维筛选(取交集), 同维度多值(取并集),
              关键词搜索(LIKE 模糊匹配), 排序.
        """
        db = get_db()

        # -- 参数解析 & 校验 --
        page = request.args.get('page', '1')
        try:
            page = int(page)
        except (ValueError, TypeError):
            return error_response(400, '参数 page 必须为整数')
        if page < 1:
            return error_response(400, '参数 page 必须为大于等于 1 的整数')

        page_size = request.args.get('page_size', '20')
        try:
            page_size = int(page_size)
        except (ValueError, TypeError):
            return error_response(400, '参数 page_size 必须为整数')
        if page_size < 1:
            return error_response(400, '参数 page_size 必须为大于等于 1 的整数')
        if page_size > 50:
            return error_response(400, '参数 page_size 不能超过 50')

        exp_types = request.args.get('experience_types', '').strip()
        vis_styles = request.args.get('visual_styles', '').strip()
        rarity = request.args.get('rarity_level', '').strip()
        keyword = request.args.get('keyword', '').strip()
        sort = request.args.get('sort', 'created_at').strip()
        order = request.args.get('order', 'desc').strip()

        # -- 参数校验 --
        if sort not in VALID_SORT_FIELDS:
            return error_response(400, f'参数 sort 必须为 {" 或 ".join(VALID_SORT_FIELDS)}')
        if order not in VALID_ORDERS:
            return error_response(400, f'参数 order 必须为 {" 或 ".join(VALID_ORDERS)}')

        # rarity_level 枚举严格校验
        if rarity:
            rarity_values = [v.strip() for v in rarity.split(',') if v.strip()]
            for rv in rarity_values:
                if rv not in VALID_RARITY_LEVELS:
                    return error_response(400, f'参数 rarity_level 值无效: {rv}')

        # -- 构建动态 SQL --
        conditions = []
        params = []

        # 体验类型筛选: 使用 json_each 检查 JSON 数组包含
        if exp_types:
            exp_list = [v.strip() for v in exp_types.split(',') if v.strip()]
            exp_conditions = []
            for ev in exp_list:
                exp_conditions.append(
                    'EXISTS (SELECT 1 FROM json_each(experience_type_tags) WHERE value = ?)'
                )
                params.append(ev)
            conditions.append('(' + ' OR '.join(exp_conditions) + ')')

        # 视觉风格筛选: 同上
        if vis_styles:
            vs_list = [v.strip() for v in vis_styles.split(',') if v.strip()]
            vs_conditions = []
            for sv in vs_list:
                vs_conditions.append(
                    'EXISTS (SELECT 1 FROM json_each(visual_style_tags) WHERE value = ?)'
                )
                params.append(sv)
            conditions.append('(' + ' OR '.join(vs_conditions) + ')')

        # 小众程度筛选: 直接等于匹配, 逗号分隔多值
        if rarity:
            rarity_values = [v.strip() for v in rarity.split(',') if v.strip()]
            placeholders = ','.join(['?'] * len(rarity_values))
            conditions.append(f'rarity_level IN ({placeholders})')
            params.extend(rarity_values)

        # 关键词搜索: LIKE 模糊匹配 title, subtitle, destination
        if keyword:
            like_pattern = f'%{keyword}%'
            conditions.append(
                '(title LIKE ? OR subtitle LIKE ? OR destination LIKE ?)'
            )
            params.extend([like_pattern, like_pattern, like_pattern])

        where_sql = ''
        if conditions:
            where_sql = 'WHERE ' + ' AND '.join(conditions)

        # -- 排序 --
        order_direction = 'DESC' if order == 'desc' else 'ASC'
        order_by = f'ORDER BY {sort} {order_direction}'

        # -- 统计总数 --
        count_sql = f'SELECT COUNT(*) AS cnt FROM trips {where_sql}'
        total = db.execute(count_sql, params).fetchone()['cnt']

        # -- 分页查询 --
        total_pages = max(1, math.ceil(total / page_size))
        offset = (page - 1) * page_size
        query_sql = (
            f'SELECT id, title, subtitle, cover_image, '
            f'experience_type_tags, visual_style_tags, '
            f'rarity_level, destination, duration '
            f'FROM trips {where_sql} {order_by} LIMIT ? OFFSET ?'
        )
        rows = db.execute(query_sql, params + [page_size, offset]).fetchall()

        # -- 构建响应 --
        items = [format_trip_card(row) for row in rows]
        data = {
            'items': items,
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': total_pages,
        }
        return cached_success_response(data)

    # ===== 2. GET /api/trips/<trip_id> — 旅行体验详情 =====
    @app.route('/api/trips/<trip_id>')
    def get_trip_detail(trip_id):
        """获取单个旅行体验完整详情.

        trip_id: 必须是正整数.
        """
        # -- ID 校验 --
        try:
            trip_id = int(trip_id)
        except (ValueError, TypeError):
            return error_response(400, '无效的ID')
        if trip_id < 1:
            return error_response(400, '无效的ID')

        # -- 查询 --
        db = get_db()
        row = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()

        if row is None:
            return error_response(404, '旅行不存在')

        detail = format_trip_detail(row)
        return success_response(detail)

    # ===== 3. GET /api/filters — 获取筛选标签 =====
    @app.route('/api/filters')
    def get_filters():
        """返回三个筛选维度的完整枚举值.

        对齐 api-spec.yaml FilterTags schema.
        """
        data = {
            'experience_types': FILTER_EXPERIENCE_TYPES,
            'visual_styles': FILTER_VISUAL_STYLES,
            'rarity_levels': FILTER_RARITY_LEVELS,
        }
        resp = jsonify({'code': 200, 'message': 'success', 'data': data})
        resp.headers['Cache-Control'] = 'public, max-age=60'
        return resp

    return app


# ============================================================================
# 数据库初始化
# ============================================================================

def _init_database(app, basedir):
    """应用启动时自动初始化数据库.

    仅在数据库文件不存在时执行 init.sql 脚本.
    对于内存数据库 (如 :memory: 或 file: URI) 总是执行初始化.
    """
    db_path = app.config['DATABASE']
    is_memory = (db_path == ':memory:' or db_path.startswith('file:'))

    # 确保 db 目录存在 (内存数据库跳过)
    if not is_memory:
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)

    # 如果数据库文件已存在则跳过初始化 (内存数据库总是初始化)
    if not is_memory and os.path.exists(db_path):
        return

    init_sql_path = os.path.join(basedir, 'db', 'init.sql')
    if not os.path.exists(init_sql_path):
        raise FileNotFoundError(f'数据库初始化脚本未找到: {init_sql_path}')

    if is_memory:
        conn = sqlite3.connect(db_path, uri=True)
    else:
        conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    with open(init_sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    conn.executescript(sql_script)
    conn.commit()
    conn.close()


# ============================================================================
# 模块级别应用实例 (生产环境启动)
# ============================================================================

# 为 Flask 内部使用提供 current_app 引用
from flask import current_app  # noqa: E402 (必须在 create_app 之后 import)

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
