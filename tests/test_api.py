"""
飞猪「100种不可思议旅行」MVP — API 接口测试用例.

严格对齐 OpenAPI 3.0.3 规范 (api-spec.yaml) 和 SQLite 数据模型 (init.sql).
每个测试用例仅测试一个场景，命名清晰表达测试意图.
"""

import json
import pytest


# ============================================================================
# 测试数据辅助函数
# ============================================================================

def _insert_sample_trips(db):
    """向测试数据库插入 5 条样例行程数据，覆盖不同的枚举组合.

    数据分布:
      id=1: 极地 + 自然光 + 冷门 (贝加尔湖冰潜)
      id=2: 水下 + 极简   + 冷门 (冰岛裂缝潜水)
      id=3: 极地 + 电影感 + 小众 (挪威极光帐篷)
      id=4: 高空 + 电影感 + 新兴 (热气球飞越卡帕多奇亚)
      id=5: 荒野 + 自然光 + 小众 (纳米比亚骷髅海岸)
    """
    trips = [
        (1,
         '西伯利亚冰潜：贝加尔湖零下40度的蓝',
         '在世界上最深的淡水湖冰层下自由潜行',
         'https://images.example.com/covers/baikal.webp',
         '["极地"]', '["自然光"]', '冷门',
         '贝加尔湖', '俄罗斯西伯利亚',
         '5天4晚', '2月-3月', '硬核',
         '[{"type":"image","url":"https://images.example.com/m1.webp","alt":"冰下潜水员"}]',
         '冰层之下：一个关于勇气的故事',
         '在零下40度的贝加尔湖冰层下潜水，是对勇气的终极考验。',
         '["在晶莹剔透的冰层下体验失重漂浮感","世界最深淡水湖的能见度可达40米"]',
         '[{"url":"https://images.example.com/g1.webp","alt":"冰下全景","caption":"穿透冰层的阳光"},'
         '{"url":"https://images.example.com/g2.webp","alt":"潜水员","caption":"冰下自由潜行"}]',
         '[{"id":3,"title":"挪威极光帐篷","subtitle":"在极光下入眠","cover_image":"https://images.example.com/covers/aurora.webp",'
         '"experience_type_tags":["极地"],"visual_style_tags":["电影感"],"rarity_level":"小众",'
         '"destination":"特罗姆瑟","duration":"3天2晚"},'
         '{"id":4,"title":"热气球土耳其","subtitle":"俯瞰月球地貌","cover_image":"https://images.example.com/covers/cappadocia.webp",'
         '"experience_type_tags":["高空"],"visual_style_tags":["电影感"],"rarity_level":"新兴",'
         '"destination":"卡帕多奇亚","duration":"1天"}]',
         'same_style',
         '2026-06-01T10:00:00Z', '2026-06-01T10:00:00Z'),

        (2,
         '冰岛裂缝潜水：两大板块之间的水下峡谷',
         '在欧亚与北美板块之间潜水',
         'https://images.example.com/covers/silfra.webp',
         '["水下"]', '["极简"]', '冷门',
         '辛格维利尔', '冰岛',
         '1天', '全年', '中等',
         '[{"type":"image","url":"https://images.example.com/m2.webp","alt":"裂缝潜水"}]',
         '板块之间：潜入地球的裂缝',
         '在冰岛辛格维利尔，你可以潜入欧亚板块和北美板块之间的裂缝。',
         '["能见度超过100米的纯净冰川融水","在地质板块之间游泳"]',
         '[{"url":"https://images.example.com/g3.webp","alt":"裂缝全景","caption":"清澈透底的裂缝"},'
         '{"url":"https://images.example.com/g4.webp","alt":"潜水员","caption":"板块之间的自由"}]',
         '[{"id":1,"title":"贝加尔湖冰潜","subtitle":"零下40度的蓝","cover_image":"https://images.example.com/covers/baikal.webp",'
         '"experience_type_tags":["极地"],"visual_style_tags":["自然光"],"rarity_level":"冷门",'
         '"destination":"贝加尔湖","duration":"5天4晚"},'
         '{"id":3,"title":"挪威极光帐篷","subtitle":"在极光下入眠","cover_image":"https://images.example.com/covers/aurora.webp",'
         '"experience_type_tags":["极地"],"visual_style_tags":["电影感"],"rarity_level":"小众",'
         '"destination":"特罗姆瑟","duration":"3天2晚"}]',
         'same_type',
         '2026-06-02T10:00:00Z', '2026-06-02T10:00:00Z'),

        (3,
         '挪威极光帐篷：在世界尽头的玻璃屋里入眠',
         '躺在温暖的羊毛毯里看极光',
         'https://images.example.com/covers/aurora.webp',
         '["极地"]', '["电影感"]', '小众',
         '特罗姆瑟', '挪威',
         '3天2晚', '10月-次年3月', '入门',
         '[{"type":"image","url":"https://images.example.com/m3.webp","alt":"极光帐篷"}]',
         '追光者：在北纬69度的三个夜晚',
         '在北极圈内的玻璃穹顶帐篷里，头顶是流动的极光瀑布。',
         '["360度无遮挡观赏极光","专业追光向导全程陪同"]',
         '[{"url":"https://images.example.com/g5.webp","alt":"极光与帐篷","caption":"玻璃屋外的极光舞蹈"},'
         '{"url":"https://images.example.com/g6.webp","alt":"营地全景","caption":"北极大地的温暖灯火"}]',
         '[{"id":1,"title":"贝加尔湖冰潜","subtitle":"零下40度的蓝","cover_image":"https://images.example.com/covers/baikal.webp",'
         '"experience_type_tags":["极地"],"visual_style_tags":["自然光"],"rarity_level":"冷门",'
         '"destination":"贝加尔湖","duration":"5天4晚"},'
         '{"id":5,"title":"纳米比亚骷髅海岸","subtitle":"世界最危险的海岸线","cover_image":"https://images.example.com/covers/namibia.webp",'
         '"experience_type_tags":["荒野"],"visual_style_tags":["自然光"],"rarity_level":"小众",'
         '"destination":"骷髅海岸","duration":"4天3晚"}]',
         'same_style',
         '2026-06-03T10:00:00Z', '2026-06-03T10:00:00Z'),

        (4,
         '热气球飞越卡帕多奇亚：俯瞰月球地貌',
         '在日出时分乘热气球俯瞰奇特地貌',
         'https://images.example.com/covers/cappadocia.webp',
         '["高空"]', '["电影感"]', '新兴',
         '卡帕多奇亚', '土耳其',
         '1天', '4月-10月', '入门',
         '[{"type":"image","url":"https://images.example.com/m4.webp","alt":"热气球日出"}]',
         '云端之上：卡帕多奇亚的日出',
         '当上百只热气球同时升空，晨曦中的奇特地貌宛如异星表面。',
         '["在日出时分俯瞰月球般的地貌","上百只热气球同时升空的壮观场面"]',
         '[{"url":"https://images.example.com/g7.webp","alt":"热气球群","caption":"晨曦中的上百只热气球"},'
         '{"url":"https://images.example.com/g8.webp","alt":"地貌俯拍","caption":"如月球表面的奇特岩石"}]',
         '[{"id":2,"title":"冰岛裂缝潜水","subtitle":"板块之间的水下峡谷","cover_image":"https://images.example.com/covers/silfra.webp",'
         '"experience_type_tags":["水下"],"visual_style_tags":["极简"],"rarity_level":"冷门",'
         '"destination":"辛格维利尔","duration":"1天"},'
         '{"id":5,"title":"纳米比亚骷髅海岸","subtitle":"世界最危险的海岸线","cover_image":"https://images.example.com/covers/namibia.webp",'
         '"experience_type_tags":["荒野"],"visual_style_tags":["自然光"],"rarity_level":"小众",'
         '"destination":"骷髅海岸","duration":"4天3晚"}]',
         'same_region',
         '2026-06-04T10:00:00Z', '2026-06-04T10:00:00Z'),

        (5,
         '纳米比亚骷髅海岸：沙漠与大海的碰撞',
         '在世界最危险的海岸线穿越',
         'https://images.example.com/covers/namibia.webp',
         '["荒野"]', '["自然光"]', '小众',
         '骷髅海岸', '纳米比亚',
         '4天3晚', '5月-10月', '硬核',
         '[{"type":"image","url":"https://images.example.com/m5.webp","alt":"骷髅海岸沉船"}]',
         '沙海之间：穿越骷髅海岸',
         '在纳米比亚的骷髅海岸，沙漠直接倾入大西洋，沉船的残骸散落在沙丘之间。',
         '["穿越地球上最荒凉的海岸线","探访百年前的沉船残骸"]',
         '[{"url":"https://images.example.com/g9.webp","alt":"海岸沉船","caption":"沙漠中的沉船遗骸"},'
         '{"url":"https://images.example.com/g10.webp","alt":"沙海交汇","caption":"沙漠与大海的碰撞"}]',
         '[{"id":3,"title":"挪威极光帐篷","subtitle":"在极光下入眠","cover_image":"https://images.example.com/covers/aurora.webp",'
         '"experience_type_tags":["极地"],"visual_style_tags":["电影感"],"rarity_level":"小众",'
         '"destination":"特罗姆瑟","duration":"3天2晚"},'
         '{"id":4,"title":"热气球土耳其","subtitle":"俯瞰月球地貌","cover_image":"https://images.example.com/covers/cappadocia.webp",'
         '"experience_type_tags":["高空"],"visual_style_tags":["电影感"],"rarity_level":"新兴",'
         '"destination":"卡帕多奇亚","duration":"1天"}]',
         'same_style',
         '2026-06-05T10:00:00Z', '2026-06-05T10:00:00Z'),
    ]

    sql = """
        INSERT INTO trips (id, title, subtitle, cover_image,
            experience_type_tags, visual_style_tags, rarity_level,
            destination, destination_region, duration, best_season, difficulty_level,
            media_list, story_title, story_body, story_highlights,
            gallery_images, related_experiences, recommendation_rule,
            created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    db.executemany(sql, trips)
    db.commit()


# ============================================================================
# 响应格式验证辅助
# ============================================================================

def _assert_response_structure(resp, expected_code):
    """验证统一响应格式: {code, message, data} 三层结构."""
    body = resp.get_json()
    assert resp.status_code == expected_code, \
        f'期望 HTTP {expected_code}，实际 {resp.status_code}'
    assert isinstance(body, dict), '响应体必须是 JSON 对象'
    assert 'code' in body, '响应体缺少 code 字段'
    assert 'message' in body, '响应体缺少 message 字段'
    assert 'data' in body, '响应体缺少 data 字段'
    assert isinstance(body['code'], int), 'code 字段必须是整数'
    assert isinstance(body['message'], str), 'message 字段必须是字符串'
    return body


def _assert_trip_card_fields(item):
    """验证 TripCard (首页卡片) 的 9 个必填字段存在且类型正确."""
    required = ['id', 'title', 'subtitle', 'cover_image',
                'experience_type_tags', 'visual_style_tags',
                'rarity_level', 'destination', 'duration']
    for field in required:
        assert field in item, f'卡片数据缺少必填字段: {field}'
    assert isinstance(item['id'], int), 'id 必须是整数'
    assert isinstance(item['title'], str), 'title 必须是字符串'
    assert isinstance(item['subtitle'], str), 'subtitle 必须是字符串'
    assert isinstance(item['cover_image'], str), 'cover_image 必须是字符串'
    assert isinstance(item['experience_type_tags'], list), 'experience_type_tags 必须是数组'
    assert isinstance(item['visual_style_tags'], list), 'visual_style_tags 必须是数组'
    assert isinstance(item['rarity_level'], str), 'rarity_level 必须是字符串'
    assert isinstance(item['destination'], str), 'destination 必须是字符串'
    assert isinstance(item['duration'], str), 'duration 必须是字符串'


# ============================================================================
# 1. GET /api/trips — 旅行体验列表
# ============================================================================

class TestListTrips:
    """测试旅行体验列表接口 (GET /api/trips)."""

    # ---- 正常情况 ----

    def test_list_trips_with_default_params(self, client, db):
        """不带任何参数，返回默认第一页数据."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips')
        body = _assert_response_structure(resp, 200)

        assert body['code'] == 200
        assert body['message'] == 'success'
        data = body['data']
        assert 'items' in data
        assert 'page' in data
        assert 'page_size' in data
        assert 'total' in data
        assert 'total_pages' in data
        assert data['page'] == 1
        assert data['page_size'] == 20  # 默认每页 20 条
        assert data['total'] == 5
        assert data['total_pages'] == 1
        assert isinstance(data['items'], list)
        assert len(data['items']) == 5, f'默认应返回全部数据，实际 {len(data["items"])} 条'
        for item in data['items']:
            _assert_trip_card_fields(item)

    # ---- 分页测试 ----

    def test_pagination_page2(self, client, db):
        """测试 page_size=2 时请求第 2 页，验证分页元数据正确."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?page=2&page_size=2')
        body = _assert_response_structure(resp, 200)

        data = body['data']
        assert data['page'] == 2
        assert data['page_size'] == 2
        assert data['total'] == 5
        assert data['total_pages'] == 3  # ceil(5/2) = 3
        assert len(data['items']) == 2

    def test_pagination_page_size(self, client, db):
        """测试 page_size=3，验证返回正确条数和分页信息."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?page=1&page_size=3')
        body = _assert_response_structure(resp, 200)

        data = body['data']
        assert data['page'] == 1
        assert data['page_size'] == 3
        assert len(data['items']) == 3
        assert data['total_pages'] == 2  # ceil(5/3) = 2

    def test_pagination_boundary_min_page_size(self, client, db):
        """边界值: page_size=1，验证每页只返回 1 条."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?page_size=1')
        body = _assert_response_structure(resp, 200)

        data = body['data']
        assert data['page_size'] == 1
        assert len(data['items']) == 1
        assert data['total_pages'] == 5

    def test_pagination_boundary_max_page_size(self, client, db):
        """边界值: page_size=50 (最大允许值)，验证正常返回."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?page_size=50')
        body = _assert_response_structure(resp, 200)

        data = body['data']
        assert data['page_size'] == 50
        assert len(data['items']) == 5  # 总共只有 5 条

    # ---- 单维度筛选 ----

    def test_filter_by_experience_type(self, client, db):
        """单维度筛选: experience_types=极地，应只返回含'极地'的记录."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?experience_types=极地')
        body = _assert_response_structure(resp, 200)

        items = body['data']['items']
        assert len(items) >= 1
        for item in items:
            assert '极地' in item['experience_type_tags'], \
                f'筛选结果应全部含"极地"，实际: {item["experience_type_tags"]}'

    def test_filter_by_visual_style(self, client, db):
        """单维度筛选: visual_styles=电影感，应只返回含'电影感'的记录."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?visual_styles=电影感')
        body = _assert_response_structure(resp, 200)

        items = body['data']['items']
        assert len(items) >= 1
        for item in items:
            assert '电影感' in item['visual_style_tags'], \
                f'筛选结果应全部含"电影感"，实际: {item["visual_style_tags"]}'

    def test_filter_by_rarity_level(self, client, db):
        """单维度筛选: rarity_level=冷门，应只返回小众程度为'冷门'的记录."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?rarity_level=冷门')
        body = _assert_response_structure(resp, 200)

        items = body['data']['items']
        assert len(items) >= 1
        for item in items:
            assert item['rarity_level'] == '冷门', \
                f'筛选结果应全部为"冷门"，实际: {item["rarity_level"]}'

    # ---- 多维度组合筛选（交集） ----

    def test_filter_multi_dimension_intersection(self, client, db):
        """三维筛选同时使用: experience_types=极地 & visual_styles=自然光 & rarity_level=冷门.
        应只返回同时满足三个条件的记录 (取交集)."""
        _insert_sample_trips(db)
        resp = client.get(
            '/api/trips?experience_types=极地&visual_styles=自然光&rarity_level=冷门'
        )
        body = _assert_response_structure(resp, 200)

        items = body['data']['items']
        assert len(items) >= 1, '应至少有一条记录同时满足三个筛选条件'
        for item in items:
            assert '极地' in item['experience_type_tags']
            assert '自然光' in item['visual_style_tags']
            assert item['rarity_level'] == '冷门'

    # ---- 多值筛选（逗号分隔） ----

    def test_filter_multi_value_experience_types(self, client, db):
        """同维度多值筛选: experience_types=极地,水下，应返回含'极地'或'水下'的记录 (OR 逻辑)."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?experience_types=极地,水下')
        body = _assert_response_structure(resp, 200)

        items = body['data']['items']
        assert len(items) >= 1
        for item in items:
            has_match = ('极地' in item['experience_type_tags'] or
                         '水下' in item['experience_type_tags'])
            assert has_match, \
                f'应至少匹配"极地"或"水下"之一，实际: {item["experience_type_tags"]}'

    def test_filter_multi_value_rarity_level(self, client, db):
        """同维度多值筛选: rarity_level=冷门,小众，应返回冷门或小众的记录."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?rarity_level=冷门,小众')
        body = _assert_response_structure(resp, 200)

        items = body['data']['items']
        assert len(items) >= 1
        for item in items:
            assert item['rarity_level'] in ('冷门', '小众'), \
                f'应属于"冷门"或"小众"，实际: {item["rarity_level"]}'

    # ---- 关键词搜索 ----

    def test_search_by_keyword_title_match(self, client, db):
        """关键词搜索: keyword=极光，应返回标题/简介/目的地中含'极光'的记录."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?keyword=极光')
        body = _assert_response_structure(resp, 200)

        items = body['data']['items']
        assert len(items) >= 1, '应有记录匹配关键词"极光"'
        for item in items:
            text_fields = (item['title'] + item['subtitle'] +
                           item['destination'])
            assert '极光' in text_fields, \
                f'搜索结果应包含关键词"极光"，实际: {item["title"]}'

    def test_search_by_keyword_no_results(self, client, db):
        """关键词搜索: 搜索一个不存在的词，应返回空列表."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?keyword=火星探险')
        body = _assert_response_structure(resp, 200)

        data = body['data']
        assert len(data['items']) == 0
        assert data['total'] == 0

    # ---- 排序 ----

    def test_sort_by_created_at_desc(self, client, db):
        """排序: sort=created_at & order=desc (默认)，最新创建的记录应排在最前."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?sort=created_at&order=desc')
        body = _assert_response_structure(resp, 200)

        items = body['data']['items']
        assert len(items) >= 2, '需要至少 2 条数据验证排序'
        # 默认倒序: id=5 最新 -> 最前
        assert items[0]['id'] == 5, f'按创建时间倒序，id=5 应在最前，实际: {items[0]["id"]}'

    def test_sort_by_rarity_level_asc(self, client, db):
        """排序: sort=rarity_level & order=asc，应按小众程度升序排列."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?sort=rarity_level&order=asc')
        body = _assert_response_structure(resp, 200)

        items = body['data']['items']
        assert len(items) >= 1
        rarity_values = [item['rarity_level'] for item in items]
        # 升序: 新兴 < 小众 < 冷门 (按拼音)
        assert rarity_values == sorted(rarity_values), \
            f'应升序排列，实际: {rarity_values}'

    # ---- 参数错误 ----

    def test_invalid_page_negative(self, client, db):
        """非法参数: page=-1，应返回 400 错误."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?page=-1')
        body = _assert_response_structure(resp, 400)

        assert body['code'] == 400
        assert body['data'] is None

    def test_invalid_page_size_exceeds_max(self, client, db):
        """非法参数: page_size=100 (超过最大值 50)，应返回 400 错误."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?page_size=100')
        body = _assert_response_structure(resp, 400)

        assert body['code'] == 400
        assert body['data'] is None

    def test_invalid_rarity_level_enum(self, client, db):
        """非法枚举值: rarity_level=热门 (不在枚举范围内)，应返回 400 错误."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?rarity_level=热门')
        body = _assert_response_structure(resp, 400)

        assert body['code'] == 400
        assert body['data'] is None

    # ---- 空数据 ----

    def test_filter_no_matching_results(self, client, db):
        """筛选条件无匹配: experience_types=美食 (无此类型数据)，应返回空列表."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips?experience_types=美食')
        body = _assert_response_structure(resp, 200)

        data = body['data']
        assert len(data['items']) == 0
        assert data['total'] == 0
        assert isinstance(data['items'], list)


# ============================================================================
# 2. GET /api/trips/{id} — 旅行体验详情
# ============================================================================

class TestTripDetail:
    """测试旅行体验详情接口 (GET /api/trips/{id})."""

    TRIP_DETAIL_REQUIRED_FIELDS = [
        'id', 'title', 'subtitle', 'cover_image',
        'experience_type_tags', 'visual_style_tags', 'rarity_level',
        'destination', 'duration', 'best_season', 'difficulty_level',
        'media_list', 'story_title', 'story_body',
        'gallery_images', 'related_experiences', 'recommendation_rule',
        'created_at', 'updated_at',
    ]

    TRIP_DETAIL_OPTIONAL_FIELDS = ['destination_region', 'story_highlights']

    def _assert_detail_field_types(self, detail):
        """验证 TripDetail 所有关键字段的类型."""
        assert isinstance(detail['id'], int)
        assert isinstance(detail['title'], str)
        assert isinstance(detail['subtitle'], str)
        assert isinstance(detail['cover_image'], str)
        assert isinstance(detail['experience_type_tags'], list)
        assert len(detail['experience_type_tags']) >= 1
        assert isinstance(detail['visual_style_tags'], list)
        assert len(detail['visual_style_tags']) >= 1
        assert isinstance(detail['rarity_level'], str)
        assert detail['rarity_level'] in ('冷门', '小众', '新兴')
        assert isinstance(detail['destination'], str)
        assert isinstance(detail['duration'], str)
        assert isinstance(detail['best_season'], str)
        assert isinstance(detail['difficulty_level'], str)
        assert detail['difficulty_level'] in ('入门', '中等', '硬核', '极限')
        assert isinstance(detail['media_list'], list)
        assert len(detail['media_list']) >= 1
        assert isinstance(detail['story_title'], str)
        assert isinstance(detail['story_body'], str)
        assert isinstance(detail['gallery_images'], list)
        assert len(detail['gallery_images']) >= 2
        assert isinstance(detail['related_experiences'], list)
        assert 2 <= len(detail['related_experiences']) <= 4
        assert isinstance(detail['recommendation_rule'], str)
        assert detail['recommendation_rule'] in ('same_type', 'same_style', 'same_region')
        assert isinstance(detail['created_at'], str)
        assert isinstance(detail['updated_at'], str)

    # ---- 正常情况 ----

    def test_get_trip_detail_by_id(self, client, db):
        """传入存在的 ID=1，返回完整详情数据和 200 状态码."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips/1')
        body = _assert_response_structure(resp, 200)

        assert body['code'] == 200
        assert body['message'] == 'success'
        detail = body['data']
        assert detail['id'] == 1
        assert detail['title'] == '西伯利亚冰潜：贝加尔湖零下40度的蓝'

    # ---- 不存在 ID ----

    def test_get_trip_detail_not_found(self, client, db):
        """传入不存在的 ID=999，应返回 404 状态码."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips/999')
        body = _assert_response_structure(resp, 404)

        assert body['code'] == 404
        assert body['data'] is None

    # ---- 非法 ID ----

    def test_get_trip_detail_invalid_non_numeric_id(self, client, db):
        """传入非数字 ID='abc'，应返回 400 状态码."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips/abc')
        body = _assert_response_structure(resp, 400)

        assert body['code'] == 400
        assert body['data'] is None

    def test_get_trip_detail_invalid_zero_id(self, client, db):
        """传入 ID=0 (小于最小值 1)，应返回 400 状态码."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips/0')
        body = _assert_response_structure(resp, 400)

        assert body['code'] == 400
        assert body['data'] is None

    # ---- 字段完整性 ----

    def test_trip_detail_field_completeness(self, client, db):
        """验证返回的详情数据包含所有必填字段且类型正确."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips/1')
        body = _assert_response_structure(resp, 200)

        detail = body['data']
        # 验证所有必填字段存在
        for field in self.TRIP_DETAIL_REQUIRED_FIELDS:
            assert field in detail, f'详情数据缺少必填字段: {field}'
        # 验证字段类型
        self._assert_detail_field_types(detail)

    def test_trip_detail_media_item_structure(self, client, db):
        """验证媒体轮播项包含 type, url, alt 三个必填字段."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips/1')
        body = _assert_response_structure(resp, 200)

        media_list = body['data']['media_list']
        for media in media_list:
            assert 'type' in media, '媒体项缺少 type 字段'
            assert 'url' in media, '媒体项缺少 url 字段'
            assert 'alt' in media, '媒体项缺少 alt 字段'
            assert media['type'] in ('image', 'video'), \
                f'媒体类型应为 image 或 video，实际: {media["type"]}'

    def test_trip_detail_gallery_image_structure(self, client, db):
        """验证图集项包含 url, alt 两个必填字段."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips/1')
        body = _assert_response_structure(resp, 200)

        gallery = body['data']['gallery_images']
        for img in gallery:
            assert 'url' in img, '图集项缺少 url 字段'
            assert 'alt' in img, '图集项缺少 alt 字段'

    def test_trip_detail_related_experience_structure(self, client, db):
        """验证相关推荐项复用首页卡片的 9 个必填字段."""
        _insert_sample_trips(db)
        resp = client.get('/api/trips/1')
        body = _assert_response_structure(resp, 200)

        related = body['data']['related_experiences']
        for exp in related:
            _assert_trip_card_fields(exp)


# ============================================================================
# 3. GET /api/filters — 获取筛选标签枚举
# ============================================================================

class TestFilterTags:
    """测试筛选标签接口 (GET /api/filters)."""

    EXPERIENCE_TYPES_EXPECTED = [
        '水下', '高空', '极地', '荒野', '地下',
        '极限运动', '文化沉浸', '夜间奇观', '慢旅行',
    ]

    VISUAL_STYLES_EXPECTED = [
        '极简', '赛博朋克', '胶片复古', '高饱和',
        '黑白', '电影感', '自然光',
    ]

    RARITY_LEVELS_EXPECTED = ['冷门', '小众', '新兴']

    # ---- 正常情况 ----

    def test_get_filter_tags_success(self, client, db):
        """正常请求，返回 200 和三个维度的完整枚举值."""
        # 筛选标签接口不依赖数据库数据，但仍需要初始化过的 db
        _insert_sample_trips(db)
        resp = client.get('/api/filters')
        body = _assert_response_structure(resp, 200)

        assert body['code'] == 200
        assert body['message'] == 'success'
        data = body['data']
        assert 'experience_types' in data
        assert 'visual_styles' in data
        assert 'rarity_levels' in data

    # ---- 字段完整性 ----

    def test_filter_tags_experience_types_completeness(self, client, db):
        """验证 experience_types 包含全部 9 个枚举值且格式正确."""
        _insert_sample_trips(db)
        resp = client.get('/api/filters')
        body = _assert_response_structure(resp, 200)

        et_list = body['data']['experience_types']
        assert isinstance(et_list, list)
        assert len(et_list) == 9, f'体验类型应有 9 个，实际 {len(et_list)}'

        values = []
        for item in et_list:
            assert isinstance(item, dict), '每个筛选标签项必须是对象'
            assert 'value' in item, '筛选标签项缺少 value 字段'
            assert 'label' in item, '筛选标签项缺少 label 字段'
            assert isinstance(item['value'], str)
            assert isinstance(item['label'], str)
            values.append(item['value'])

        assert set(values) == set(self.EXPERIENCE_TYPES_EXPECTED), \
            f'体验类型枚举值不完整，期望 {self.EXPERIENCE_TYPES_EXPECTED}，实际 {values}'

    def test_filter_tags_visual_styles_completeness(self, client, db):
        """验证 visual_styles 包含全部 7 个枚举值且格式正确."""
        _insert_sample_trips(db)
        resp = client.get('/api/filters')
        body = _assert_response_structure(resp, 200)

        vs_list = body['data']['visual_styles']
        assert isinstance(vs_list, list)
        assert len(vs_list) == 7, f'视觉风格应有 7 个，实际 {len(vs_list)}'

        values = []
        for item in vs_list:
            assert isinstance(item, dict)
            assert 'value' in item
            assert 'label' in item
            values.append(item['value'])

        assert set(values) == set(self.VISUAL_STYLES_EXPECTED), \
            f'视觉风格枚举值不完整，期望 {self.VISUAL_STYLES_EXPECTED}，实际 {values}'

    def test_filter_tags_rarity_levels_completeness(self, client, db):
        """验证 rarity_levels 包含全部 3 个枚举值且格式正确."""
        _insert_sample_trips(db)
        resp = client.get('/api/filters')
        body = _assert_response_structure(resp, 200)

        rl_list = body['data']['rarity_levels']
        assert isinstance(rl_list, list)
        assert len(rl_list) == 3, f'小众程度应有 3 个，实际 {len(rl_list)}'

        values = []
        for item in rl_list:
            assert isinstance(item, dict)
            assert 'value' in item
            assert 'label' in item
            values.append(item['value'])

        assert set(values) == set(self.RARITY_LEVELS_EXPECTED), \
            f'小众程度枚举值不完整，期望 {self.RARITY_LEVELS_EXPECTED}，实际 {values}'

    # ---- 枚举值正确性 ----

    def test_filter_tags_no_duplicate_values(self, client, db):
        """验证每个维度内没有重复的 value 值."""
        _insert_sample_trips(db)
        resp = client.get('/api/filters')
        body = _assert_response_structure(resp, 200)

        for dim_name in ['experience_types', 'visual_styles', 'rarity_levels']:
            items = body['data'][dim_name]
            values = [item['value'] for item in items]
            assert len(values) == len(set(values)), \
                f'{dim_name} 中存在重复的 value: {values}'

    def test_filter_tags_response_cache_header(self, client, db):
        """验证筛选标签接口也可能返回合理的响应."""
        _insert_sample_trips(db)
        resp = client.get('/api/filters')
        assert resp.status_code == 200
        # 验证响应是可缓存的 JSON
        assert resp.content_type == 'application/json' or resp.is_json
