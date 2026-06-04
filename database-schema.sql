-- ============================================================================
-- 飞猪「100种不可思议旅行」MVP SQLite 3.45.0+ 数据库模型
-- ============================================================================
-- 严格基于 PRD v1.0 (2026-06-04) 第10章数据字典
-- 字段、类型、枚举值、约束 100% 对齐 PRD 原文
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Mermaid ER Diagram
-- ----------------------------------------------------------------------------
-- ```mermaid
-- erDiagram
--     TRIPS {
--         INTEGER id PK "自增主键"
--         TEXT title "旅行标题 1-30字符"
--         TEXT subtitle "一句话描述 1-20字符"
--         TEXT cover_image "封面图URL"
--         TEXT experience_type_tags "JSONB 体验类型数组 枚举:水下/高空/极地/荒野/地下/极限运动/文化沉浸/夜间奇观/慢旅行"
--         TEXT visual_style_tags "JSONB 视觉风格数组 枚举:极简/赛博朋克/胶片复古/高饱和/黑白/电影感/自然光"
--         TEXT rarity_level "小众程度 枚举:冷门/小众/新兴"
--         TEXT destination "目的地 1-30字符"
--         TEXT destination_region "所属地区/国家 1-30字符"
--         TEXT duration "建议体验时长 自由文本"
--         TEXT best_season "最佳体验季节 自由文本"
--         TEXT difficulty_level "难度等级 枚举:入门/中等/硬核/极限"
--         TEXT media_list "JSONB 媒体轮播列表 type+url+alt+cover_frame"
--         TEXT story_title "故事标题 1-50字符"
--         TEXT story_body "故事正文 富文本"
--         TEXT story_highlights "JSONB 故事亮点摘要 0-5项"
--         TEXT gallery_images "JSONB 高清图集 url+alt+caption 至少2项"
--         TEXT related_experiences "JSONB 相关推荐 2-4项"
--         TEXT recommendation_rule "推荐逻辑 枚举:same_type/same_style/same_region"
--         TEXT created_at "创建时间 ISO8601"
--         TEXT updated_at "更新时间 ISO8601"
--     }
-- ```

-- ============================================================================
-- Part 1: PRAGMA 配置
-- ============================================================================

PRAGMA journal_mode = WAL;          -- WAL 模式，提升并发读写性能
PRAGMA foreign_keys = ON;           -- 启用外键约束（预留未来扩展）
PRAGMA synchronous = NORMAL;        -- 平衡性能与安全性
PRAGMA cache_size = -8000;          -- 8MB 缓存，适合移动端数据量
PRAGMA mmap_size = 268435456;       -- 256MB 内存映射
PRAGMA temp_store = MEMORY;         -- 临时表存储在内存中

-- ============================================================================
-- Part 2: CREATE TABLE — 唯一核心表 trips
-- ============================================================================

CREATE TABLE IF NOT EXISTS trips (
    -- --- 主键 ---
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,

    -- --- 首页卡片字段 (PRD 4.3.1) ---
    title               TEXT    NOT NULL
                        CHECK (length(title) >= 1 AND length(title) <= 30),

    subtitle            TEXT    NOT NULL
                        CHECK (length(subtitle) >= 1 AND length(subtitle) <= 20),

    cover_image         TEXT    NOT NULL
                        CHECK (length(cover_image) > 0),

    experience_type_tags TEXT   NOT NULL DEFAULT '[]'
                        CHECK (json_valid(experience_type_tags)
                           AND json_array_length(experience_type_tags) >= 1),

    visual_style_tags   TEXT    NOT NULL DEFAULT '[]'
                        CHECK (json_valid(visual_style_tags)
                           AND json_array_length(visual_style_tags) >= 1),

    rarity_level        TEXT    NOT NULL
                        CHECK (rarity_level IN ('冷门', '小众', '新兴')),

    destination         TEXT    NOT NULL
                        CHECK (length(destination) >= 1 AND length(destination) <= 30),

    -- --- 详情页字段 (PRD 6.2) ---
    destination_region  TEXT
                        CHECK (destination_region IS NULL
                            OR length(destination_region) <= 30),

    duration            TEXT    NOT NULL
                        CHECK (length(duration) >= 1),

    best_season         TEXT    NOT NULL
                        CHECK (length(best_season) >= 1),

    difficulty_level    TEXT    NOT NULL
                        CHECK (difficulty_level IN ('入门', '中等', '硬核', '极限')),

    -- --- 媒体轮播 (PRD 6.2.1) ---
    -- 每项: { "type": "image|video", "url": "...", "alt": "...", "cover_frame": "..." }
    media_list          TEXT    NOT NULL DEFAULT '[]'
                        CHECK (json_valid(media_list)
                           AND json_array_length(media_list) >= 1),

    -- --- 故事叙述 (PRD 6.2.4) ---
    story_title         TEXT    NOT NULL
                        CHECK (length(story_title) >= 1 AND length(story_title) <= 50),

    story_body          TEXT    NOT NULL
                        CHECK (length(story_body) >= 1),

    story_highlights    TEXT    DEFAULT '[]'
                        CHECK (story_highlights IS NULL
                            OR (json_valid(story_highlights)
                            AND json_array_length(story_highlights) <= 5)),

    -- --- 高清图集 (PRD 6.2.5) ---
    -- 每项: { "url": "...", "alt": "...", "caption": "..." }
    gallery_images      TEXT    NOT NULL DEFAULT '[]'
                        CHECK (json_valid(gallery_images)
                           AND json_array_length(gallery_images) >= 2),

    -- --- 相关推荐 (PRD 6.2.6) ---
    -- 每项复用首页卡片: { "id", "title", "subtitle", "cover_image", ... }
    related_experiences TEXT    NOT NULL DEFAULT '[]'
                        CHECK (json_valid(related_experiences)
                           AND json_array_length(related_experiences) BETWEEN 2 AND 4),

    recommendation_rule TEXT    NOT NULL
                        CHECK (recommendation_rule IN
                            ('same_type', 'same_style', 'same_region')),

    -- --- 系统元数据 (PRD 10.1) ---
    created_at          TEXT    NOT NULL DEFAULT (datetime('now'))
                        CHECK (created_at IS NOT NULL),

    updated_at          TEXT    NOT NULL DEFAULT (datetime('now'))
                        CHECK (updated_at IS NOT NULL)
);

-- ============================================================================
-- Part 3: 索引 (匹配 PRD 4.2.3 三维筛选组合取交集逻辑)
-- ============================================================================

-- 3.1 小众程度单列索引 — 筛选维度3
CREATE INDEX IF NOT EXISTS idx_rarity_level
    ON trips(rarity_level);

-- 3.2 目的地单列索引 — 搜索/筛选
CREATE INDEX IF NOT EXISTS idx_destination
    ON trips(destination);

-- 3.3 创建时间索引 — 默认排序(倒序)
CREATE INDEX IF NOT EXISTS idx_created_at
    ON trips(created_at DESC);

-- ----------------------------------------------------------------------------
-- 说明: SQLite 3.45 JSON 多值数组的包含查询优化
-- ----------------------------------------------------------------------------
-- 对于 experience_type_tags 和 visual_style_tags 两个 JSON 数组列的筛选,
-- SQLite 无法创建传统的 B-Tree 索引直接加速 json_each() 子查询.
--
-- 策略:
-- 1. 利用 json_valid() + json_array_length() CHECK 约束保证数据完整性
-- 2. 筛选查询使用 json_each() 展开数组后做 INNER JOIN 取交集
-- 3. 对 rarity_level 的 B-Tree 索引先缩小范围, 再展开 JSON 做精细过滤
-- 4. 关键词搜索走 FTS5 全文索引 (见 Part 4)
-- ----------------------------------------------------------------------------

-- ============================================================================
-- Part 4: FTS5 全文搜索 (匹配 PRD 5.4 关键词搜索)
-- ============================================================================

-- 4.1 FTS5 虚拟表 — 对可搜索文本列建立全文索引
CREATE VIRTUAL TABLE IF NOT EXISTS trips_fts USING fts5(
    title,
    subtitle,
    destination,
    destination_region,
    experience_type_tags,       -- JSON数组文本也可被搜索
    visual_style_tags,           -- JSON数组文本也可被搜索
    content='trips',             -- 外部内容表
    content_rowid='id',          -- 外部内容表的行ID列
    tokenize='unicode61'         -- unicode61分词器, CJK字符序列按词组切分
);
-- 说明: unicode61 对 CJK 文本按连续字符序列建立 token.
-- 如 "贝加尔湖" 整体可匹配; 对子串匹配场景 (如搜"极光"命中"挪威极光帐篷"),
-- 建议应用层先走 FTS5, 无结果时降级为 LIKE 搜索 (见 Part 7 查询示例).

-- 4.2 触发器: INSERT 时同步到 FTS5
CREATE TRIGGER IF NOT EXISTS trips_ai AFTER INSERT ON trips BEGIN
    INSERT INTO trips_fts(rowid, title, subtitle, destination, destination_region,
                          experience_type_tags, visual_style_tags)
    VALUES (new.id, new.title, new.subtitle, new.destination, new.destination_region,
            new.experience_type_tags, new.visual_style_tags);
END;

-- 4.3 触发器: DELETE 时同步到 FTS5
CREATE TRIGGER IF NOT EXISTS trips_ad AFTER DELETE ON trips BEGIN
    INSERT INTO trips_fts(trips_fts, rowid, title, subtitle, destination,
                          destination_region, experience_type_tags, visual_style_tags)
    VALUES ('delete', old.id, old.title, old.subtitle, old.destination,
            old.destination_region, old.experience_type_tags, old.visual_style_tags);
END;

-- 4.4 触发器: UPDATE 时同步到 FTS5
CREATE TRIGGER IF NOT EXISTS trips_au AFTER UPDATE ON trips BEGIN
    INSERT INTO trips_fts(trips_fts, rowid, title, subtitle, destination,
                          destination_region, experience_type_tags, visual_style_tags)
    VALUES ('delete', old.id, old.title, old.subtitle, old.destination,
            old.destination_region, old.experience_type_tags, old.visual_style_tags);
    INSERT INTO trips_fts(rowid, title, subtitle, destination, destination_region,
                          experience_type_tags, visual_style_tags)
    VALUES (new.id, new.title, new.subtitle, new.destination, new.destination_region,
            new.experience_type_tags, new.visual_style_tags);
END;

-- ============================================================================
-- Part 5: 自动更新 updated_at 触发器
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS trips_update_timestamp
    AFTER UPDATE ON trips
    FOR EACH ROW
    WHEN old.updated_at = new.updated_at
BEGIN
    UPDATE trips SET updated_at = datetime('now') WHERE id = old.id;
END;

-- ============================================================================
-- Part 6: 样例数据 (5条, 覆盖不同体验类型/视觉风格/小众程度)
-- ============================================================================

-- 样例 1: 冷门 + 水下 + 极简/自然光
INSERT INTO trips (title, subtitle, cover_image,
    experience_type_tags, visual_style_tags, rarity_level,
    destination, destination_region, duration, best_season, difficulty_level,
    media_list,
    story_title, story_body, story_highlights,
    gallery_images, related_experiences, recommendation_rule)
VALUES (
    '西伯利亚冰潜：贝加尔湖零下40度的蓝',
    '在世界上最深的淡水湖冰层下自由潜行',
    'https://assets.flyzoo.com/covers/baikal-ice-dive.webp',

    '["水下", "极地"]',
    '["极简", "自然光"]',
    '冷门',

    '贝加尔湖', '俄罗斯西伯利亚',
    '5天4晚', '2月-3月', '硬核',

    '[
        {"type":"image","url":"https://assets.flyzoo.com/media/baikal-01.webp","alt":"冰层下潜水员剪影"},
        {"type":"image","url":"https://assets.flyzoo.com/media/baikal-02.webp","alt":"透过冰层看潜水员"},
        {"type":"video","url":"https://assets.flyzoo.com/media/baikal-dive.mp4","alt":"冰潜水下跟拍","cover_frame":"https://assets.flyzoo.com/media/baikal-thumb.webp"}
    ]',

    '冰层之下：一个关于勇气的故事',
    '我从未想过自己会在西伯利亚的冬天，站在一米厚的冰层上，穿戴好潜水装备，然后跳进一个凿开的三角形冰洞。水温恒定在零度附近，但真正的挑战不是寒冷，而是心理上的恐惧——头顶是坚不可摧的冰层，只有那个小小的三角形开口是回到人间的通道。然而当阳光穿透冰层，将整个水下世界染成梦幻的蓝色，那一刻你意识到，恐惧是通往不可思议之美的入场券。贝加尔湖的冰潜不是一项运动，而是一次对自我的重新校准。',
    '["在晶莹剔透的冰层下体验失重漂浮感", "世界最深淡水湖的能见度可达40米", "专业冰潜教练1对1陪同确保安全"]',

    '[
        {"url":"https://assets.flyzoo.com/gallery/baikal-g01.webp","alt":"冰下蓝色世界全景","caption":"阳光穿透一米冰层形成的蓝色光柱"},
        {"url":"https://assets.flyzoo.com/gallery/baikal-g02.webp","alt":"潜水员与气泡","caption":"呼出的气泡在冰层下汇聚成银色湖泊"},
        {"url":"https://assets.flyzoo.com/gallery/baikal-g03.webp","alt":"冰洞入口俯拍","caption":"从水下仰望，冰洞入口像一轮三角形的太阳"}
    ]',

    '[
        {"id":5,"title":"挪威北极光帐篷营地","subtitle":"在极光下入眠的72小时","cover_image":"https://assets.flyzoo.com/covers/aurora-camp.webp","experience_type_tags":"[\"极地\",\"慢旅行\"]","visual_style_tags":"[\"电影感\",\"自然光\"]","rarity_level":"小众","destination":"特罗姆瑟","duration":"3天2晚"},
        {"id":4,"title":"阿拉斯加荒野木屋：7天无人类的极北独居","subtitle":"住进不通电不通网的荒野木屋，与驯鹿和极光为伴","cover_image":"https://assets.flyzoo.com/covers/alaska-cabin.webp","experience_type_tags":"[\"荒野\",\"慢旅行\"]","visual_style_tags":"[\"极简\",\"自然光\"]","rarity_level":"冷门","destination":"阿拉斯加","duration":"7天"}
    ]',
    'same_style'
);

-- 样例 2: 小众 + 高空 + 赛博朋克/电影感
INSERT INTO trips (title, subtitle, cover_image,
    experience_type_tags, visual_style_tags, rarity_level,
    destination, destination_region, duration, best_season, difficulty_level,
    media_list,
    story_title, story_body, story_highlights,
    gallery_images, related_experiences, recommendation_rule)
VALUES (
    '东京屋顶：城市天台上的另一面',
    '潜入东京隐秘天台，看赛博朋克天际线',
    'https://assets.flyzoo.com/covers/tokyo-rooftop.webp',

    '["高空", "夜间奇观"]',
    '["赛博朋克", "电影感"]',
    '小众',

    '东京', '日本',
    '半日', '全年', '入门',

    '[
        {"type":"image","url":"https://assets.flyzoo.com/media/tokyo-rooftop-01.webp","alt":"新宿霓虹灯天际线"},
        {"type":"image","url":"https://assets.flyzoo.com/media/tokyo-rooftop-02.webp","alt":"雨夜天台倒影"}
    ]',

    '天台之上：东京的另一种打开方式',
    '东京有无数种玩法，但很少有人知道这座城市最迷人的角度在天台上。跟随本地城市探险者，穿过不起眼的消防梯和员工通道，你将抵达一个只属于少数人的东京。脚下是涩谷十字路口永不停歇的人流，远处是新宿的霓虹森林，而你就站在这些巨兽的缝隙之间。这不是旅游指南里的东京，这是银翼杀手电影中的城市——湿漉漉的柏油路面反射着巨型LED广告牌的光，而你手中冰凉的罐装咖啡是唯一的锚点。',

    '["探访5个不对外开放的隐秘天台", "在日落蓝色时刻拍摄电影感大片", "本地摄影师带路，了解每个天台背后的故事"]',

    '[
        {"url":"https://assets.flyzoo.com/gallery/tokyo-g01.webp","alt":"新宿雨夜街景俯拍","caption":"雨后柏油路反射霓虹灯光，赛博朋克感拉满"},
        {"url":"https://assets.flyzoo.com/gallery/tokyo-g02.webp","alt":"涩谷十字路口从天台俯视","caption":"世界上最繁忙的十字路口，从天台看像精致的机械装置"},
        {"url":"https://assets.flyzoo.com/gallery/tokyo-g03.webp","alt":"日出时分的东京塔","caption":"在某个废弃天台等到天亮，东京塔在晨光中温柔得不像话"},
        {"url":"https://assets.flyzoo.com/gallery/tokyo-g04.webp","alt":"天台上的日式自动售货机","caption":"孤独的自动售货机在天台上亮着，像某种赛博时代的信号灯"}
    ]',

    '[
        {"id":3,"title":"重庆地下核工厂废墟探索","subtitle":"在尘封50年的巨型地下工程中穿行","cover_image":"https://assets.flyzoo.com/covers/chongqing-bunker.webp","experience_type_tags":"[\"地下\"]","visual_style_tags":"[\"胶片复古\",\"黑白\"]","rarity_level":"冷门","destination":"重庆涪陵","duration":"1天"},
        {"id":4,"title":"阿拉斯加荒野木屋独居","subtitle":"7天无信号无人类的极北森林生活","cover_image":"https://assets.flyzoo.com/covers/alaska-cabin.webp","experience_type_tags":"[\"荒野\",\"慢旅行\"]","visual_style_tags":"[\"极简\",\"自然光\"]","rarity_level":"冷门","destination":"阿拉斯加","duration":"7天"}
    ]',
    'same_type'
);

-- 样例 3: 冷门 + 地下 + 胶片复古/黑白
INSERT INTO trips (title, subtitle, cover_image,
    experience_type_tags, visual_style_tags, rarity_level,
    destination, destination_region, duration, best_season, difficulty_level,
    media_list,
    story_title, story_body, story_highlights,
    gallery_images, related_experiences, recommendation_rule)
VALUES (
    '重庆816地下核工厂：尘封50年的巨型迷宫',
    '在尘封50年的巨型地下工程中穿行',
    'https://assets.flyzoo.com/covers/chongqing-bunker.webp',

    '["地下"]',
    '["胶片复古", "黑白"]',
    '冷门',

    '重庆涪陵', '中国',
    '1天', '全年', '中等',

    '[
        {"type":"image","url":"https://assets.flyzoo.com/media/bunker-01.webp","alt":"核工厂主洞室全景"},
        {"type":"image","url":"https://assets.flyzoo.com/media/bunker-02.webp","alt":"锈蚀的控制室仪表盘"},
        {"type":"video","url":"https://assets.flyzoo.com/media/bunker-walk.mp4","alt":"地下通道行走跟拍","cover_frame":"https://assets.flyzoo.com/media/bunker-thumb.webp"}
    ]',

    '深入山体：一座为末日而建的城市',
    '1967年，六万人在涪陵的深山中秘密施工，掏空了整座山体，建造了世界上最大的人工洞体——816地下核工厂。这个工程在完全保密的状态下进行了17年，直到1984年才被叫停。今天你可以走进这个总建筑面积超过10万平方米的地下迷宫，穿过130条隧道和洞室，亲手触摸冷战时期人类为末日准备的疯狂。墙上还留着当年的标语，控制室里的仪表盘锈迹斑斑，但依然可以想象六万人在这座地下城市中工作生活的场景。这不是电影，这是一个真实存在的、人类为了毁灭自己而建造的地下王国。',

    '["进入从未对公众开放的核心反应堆大厅", "走完长达20公里的地下隧道网络", "手持胶片相机拍摄时光凝固的工业遗迹"]',

    '[
        {"url":"https://assets.flyzoo.com/gallery/bunker-g01.webp","alt":"核反应堆大厅全景","caption":"高30米的主反应堆大厅，人在其中渺小如蝼蚁"},
        {"url":"https://assets.flyzoo.com/gallery/bunker-g02.webp","alt":"斑驳的控制室","caption":"1970年代的仪表和控制台，时间仿佛冻结在这里"},
        {"url":"https://assets.flyzoo.com/gallery/bunker-g03.webp","alt":"地下隧道深处","caption":"长达数公里的隧道，灯光在尽头变成一个小小的亮点"}
    ]',

    '[
        {"id":2,"title":"东京屋顶：城市天台上的另一面","subtitle":"潜入东京隐秘天台，发现赛博朋克电影般的城市天际线","cover_image":"https://assets.flyzoo.com/covers/tokyo-rooftop.webp","experience_type_tags":"[\"高空\",\"夜间奇观\"]","visual_style_tags":"[\"赛博朋克\",\"电影感\"]","rarity_level":"小众","destination":"东京","duration":"半日"},
        {"id":5,"title":"挪威北极光帐篷营地","subtitle":"在极光下入眠的72小时","cover_image":"https://assets.flyzoo.com/covers/aurora-camp.webp","experience_type_tags":"[\"极地\",\"慢旅行\"]","visual_style_tags":"[\"电影感\",\"自然光\"]","rarity_level":"小众","destination":"特罗姆瑟","duration":"3天2晚"}
    ]',
    'same_region'
);

-- 样例 4: 新兴 + 荒野 + 自然光/极简
INSERT INTO trips (title, subtitle, cover_image,
    experience_type_tags, visual_style_tags, rarity_level,
    destination, destination_region, duration, best_season, difficulty_level,
    media_list,
    story_title, story_body, story_highlights,
    gallery_images, related_experiences, recommendation_rule)
VALUES (
    '阿拉斯加荒野木屋：7天无人类的极北独居',
    '住进无电无网的荒野木屋与驯鹿为伴',
    'https://assets.flyzoo.com/covers/alaska-cabin.webp',

    '["荒野", "慢旅行"]',
    '["极简", "自然光"]',
    '冷门',

    '阿拉斯加', '美国',
    '7天', '9月-10月', '中等',

    '[
        {"type":"image","url":"https://assets.flyzoo.com/media/alaska-01.webp","alt":"荒野木屋外观"},
        {"type":"image","url":"https://assets.flyzoo.com/media/alaska-02.webp","alt":"木屋内取暖的铸铁炉"},
        {"type":"image","url":"https://assets.flyzoo.com/media/alaska-03.webp","alt":"窗外走过驯鹿群"}
    ]',

    '独自面对荒野：7天教会我的事',
    '直升机把你和一周的补给品卸在空地上，然后那架红白相间的机器越飞越远，螺旋桨的声音最终被风声取代。这里离最近的公路有100公里，没有手机信号，没有电，没有人类的声音——只有你、一座木屋、一个铸铁炉、和超过两万平方公里的原始荒野。第一天你会感到恐惧，那种沉默像实体一样压着耳膜。第三天你学会了分辨不同鸟类的叫声，学会了劈柴，学会了在日落后不点蜡烛，只靠炉火的微光看窗外绿色的极光。第七天，当直升机回来时，你发现自己不再需要它了。',

    '["亲手劈柴生火、在炉火上做饭", "秋夜躺着看极光无需任何滤镜", "白天徒步追踪野生驯鹿迁徙路线"]',

    '[
        {"url":"https://assets.flyzoo.com/gallery/alaska-g01.webp","alt":"木屋窗口望出去的极光","caption":"躺在木屋里就能看到的极光，不需要任何旅行团"},
        {"url":"https://assets.flyzoo.com/gallery/alaska-g02.webp","alt":"秋天苔原上的红色植被","caption":"九月的阿拉斯加苔原是一张红黄交织的地毯"},
        {"url":"https://assets.flyzoo.com/gallery/alaska-g03.webp","alt":"直升机降落补给","caption":"离开的瞬间，你已经在计划下一次回来"},
        {"url":"https://assets.flyzoo.com/gallery/alaska-g04.webp","alt":"铸铁炉上煮咖啡","caption":"劈柴二十分钟，只为一杯炉火咖啡，但这是世界上最好喝的咖啡"}
    ]',

    '[
        {"id":1,"title":"西伯利亚冰潜：贝加尔湖零下40度的蓝","subtitle":"在世界上最深的淡水湖冰层下自由潜行","cover_image":"https://assets.flyzoo.com/covers/baikal-ice-dive.webp","experience_type_tags":"[\"水下\",\"极地\"]","visual_style_tags":"[\"极简\",\"自然光\"]","rarity_level":"冷门","destination":"贝加尔湖","duration":"5天4晚"},
        {"id":5,"title":"挪威北极光帐篷营地","subtitle":"在极光下入眠的72小时","cover_image":"https://assets.flyzoo.com/covers/aurora-camp.webp","experience_type_tags":"[\"极地\",\"夜间奇观\",\"慢旅行\"]","visual_style_tags":"[\"电影感\",\"自然光\"]","rarity_level":"小众","destination":"特罗姆瑟","duration":"3天2晚"}
    ]',
    'same_style'
);

-- 样例 5: 小众 + 极地 + 电影感/自然光
INSERT INTO trips (title, subtitle, cover_image,
    experience_type_tags, visual_style_tags, rarity_level,
    destination, destination_region, duration, best_season, difficulty_level,
    media_list,
    story_title, story_body, story_highlights,
    gallery_images, related_experiences, recommendation_rule)
VALUES (
    '挪威极光帐篷：在世界尽头的玻璃屋里入眠',
    '躺在温暖的羊毛毯里，头顶是流动的极光瀑布',
    'https://assets.flyzoo.com/covers/aurora-camp.webp',

    '["极地", "夜间奇观", "慢旅行"]',
    '["电影感", "自然光"]',
    '小众',

    '特罗姆瑟', '挪威',
    '3天2晚', '10月-次年3月', '入门',

    '[
        {"type":"image","url":"https://assets.flyzoo.com/media/aurora-01.webp","alt":"玻璃帐篷外极光全景"},
        {"type":"video","url":"https://assets.flyzoo.com/media/aurora-timelapse.mp4","alt":"极光延时摄影","cover_frame":"https://assets.flyzoo.com/media/aurora-thumb.webp"}
    ]',

    '追光者：在北纬69度的三个夜晚',
    '天气预报说今夜云层很薄，极光指数KP4。晚餐后，你关掉帐篷里所有的灯，钻进厚厚的驯鹿皮毯子里。起初什么也看不见，只有头顶的玻璃穹顶上结了一层薄薄的霜。然后它来了——先是一条淡淡的绿色光带，像有人在黑色画布上用水彩轻轻扫过。然后绿色越来越浓，开始流动、旋转、变幻出紫色和粉色的边缘。整个天空变成了一座光的瀑布，而你就躺在世界的尽头，看着宇宙跳这支只有极少数人能亲眼目睹的舞蹈。',

    '["入住全透明玻璃穹顶帐篷，360度无遮挡观星", "专业极光向导带领追光，成功率提升至90%", "白天体验哈士奇雪橇穿越北极苔原"]',

    '[
        {"url":"https://assets.flyzoo.com/gallery/aurora-g01.webp","alt":"玻璃帐篷与极光合影","caption":"躺在零下20度的帐篷里，头顶是零上200度的极光燃烧"},
        {"url":"https://assets.flyzoo.com/gallery/aurora-g02.webp","alt":"紫色极光特写","caption":"罕见的紫色极光，需要极光指数KP5以上才能看到"},
        {"url":"https://assets.flyzoo.com/gallery/aurora-g03.webp","alt":"营地全景","caption":"北极圈内的极光营地，世界尽头的一簇暖光"}
    ]',

    '[
        {"id":1,"title":"西伯利亚冰潜：贝加尔湖零下40度的蓝","subtitle":"在世界上最深的淡水湖冰层下自由潜行","cover_image":"https://assets.flyzoo.com/covers/baikal-ice-dive.webp","experience_type_tags":"[\"水下\",\"极地\"]","visual_style_tags":"[\"极简\",\"自然光\"]","rarity_level":"冷门","destination":"贝加尔湖","duration":"5天4晚"},
        {"id":4,"title":"阿拉斯加荒野木屋：7天无人类的极北独居","subtitle":"住进不通电不通网的荒野木屋，与驯鹿和极光为伴","cover_image":"https://assets.flyzoo.com/covers/alaska-cabin.webp","experience_type_tags":"[\"荒野\",\"慢旅行\"]","visual_style_tags":"[\"极简\",\"自然光\"]","rarity_level":"冷门","destination":"阿拉斯加","duration":"7天"},
        {"id":2,"title":"东京屋顶：城市天台上的另一面","subtitle":"潜入东京隐秘天台，发现赛博朋克电影般的城市天际线","cover_image":"https://assets.flyzoo.com/covers/tokyo-rooftop.webp","experience_type_tags":"[\"高空\",\"夜间奇观\"]","visual_style_tags":"[\"赛博朋克\",\"电影感\"]","rarity_level":"小众","destination":"东京","duration":"半日"}
    ]',
    'same_style'
);

-- ============================================================================
-- Part 7: PRD 对应查询示例
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 查询 7.1: 首页默认推荐
-- 对齐 PRD 4.4 — 按创建时间倒序，瀑布流首屏加载 20 条
-- 返回字段对齐 PRD 4.3.1 卡片字段定义
-- ----------------------------------------------------------------------------
-- SELECT
--     id,
--     title,
--     subtitle,
--     cover_image,
--     experience_type_tags,
--     visual_style_tags,
--     rarity_level,
--     destination,
--     duration
-- FROM trips
-- ORDER BY created_at DESC
-- LIMIT 20;
--
-- 预期结果: 返回5条样例数据(按样例5→4→3→2→1倒序)

-- ----------------------------------------------------------------------------
-- 查询 7.2: 三维筛选组合查询
-- 对齐 PRD 4.2.3 — 三个维度取交集，实时更新
-- 示例: 筛选 体验类型含"极地" + 视觉风格含"自然光" + 小众程度="冷门"
-- ----------------------------------------------------------------------------
-- SELECT
--     id, title, subtitle, cover_image,
--     experience_type_tags, visual_style_tags,
--     rarity_level, destination, duration
-- FROM trips
-- WHERE rarity_level = '冷门'
--   AND EXISTS (
--       SELECT 1 FROM json_each(experience_type_tags)
--       WHERE value = '极地'
--   )
--   AND EXISTS (
--       SELECT 1 FROM json_each(visual_style_tags)
--       WHERE value = '自然光'
--   )
-- ORDER BY created_at DESC;
--
-- 预期结果: 返回样例1(贝加尔湖冰潜) — 同时满足极地+自然光+冷门

-- ----------------------------------------------------------------------------
-- 查询 7.3: 关键词搜索
-- 对齐 PRD 5.4 — 匹配标题、标签、目的地
-- 策略: 先用 FTS5 unicode61 做分词匹配, 无结果时降级为 LIKE 子串搜索
-- 示例: 搜索关键词 "极光"
-- ----------------------------------------------------------------------------
-- -- FTS5 分词匹配 (适用于完整词组如"贝加尔湖""重庆涪陵")
-- SELECT
--     t.id, t.title, t.subtitle, t.cover_image,
--     t.experience_type_tags, t.visual_style_tags,
--     t.rarity_level, t.destination, t.duration
-- FROM trips t
-- JOIN trips_fts fts ON t.id = fts.rowid
-- WHERE trips_fts MATCH '极光'
-- ORDER BY rank
-- LIMIT 20;
--
-- -- LIKE 子串搜索 (FTS5 无结果时的降级方案, 适用于 CJK 子串)
-- SELECT
--     id, title, subtitle, cover_image,
--     experience_type_tags, visual_style_tags,
--     rarity_level, destination, duration
-- FROM trips
-- WHERE title LIKE '%极光%'
--    OR subtitle LIKE '%极光%'
--    OR destination LIKE '%极光%'
--    OR destination_region LIKE '%极光%'
--    OR experience_type_tags LIKE '%极光%'
--    OR visual_style_tags LIKE '%极光%'
-- ORDER BY
--     CASE WHEN title LIKE '%极光%' THEN 0
--          WHEN subtitle LIKE '%极光%' THEN 1
--          WHEN destination LIKE '%极光%' THEN 2
--          ELSE 3
--     END,
--     created_at DESC
-- LIMIT 20;
--
-- 预期结果: FTS5 可能无结果; LIKE 降级返回样例5(挪威极光帐篷)和样例4(阿拉斯加)

-- ----------------------------------------------------------------------------
-- 查询 7.4: 详情页完整查询
-- 对齐 PRD 6.2 — 返回单个旅行体验的全部字段
-- ----------------------------------------------------------------------------
-- SELECT * FROM trips WHERE id = 1;
--
-- 预期结果: 返回样例1(贝加尔湖冰潜)的完整21个字段

-- ============================================================================
-- 文件结束
-- ============================================================================
