-- ============================================================================
-- 飞猪「100种不可思议旅行」MVP SQLite 数据库初始化脚本
-- ============================================================================
-- 严格基于 PRD v1.0 (2026-06-04) 第10章数据字典
-- 字段、类型、枚举值、约束 100% 对齐 PRD 原文
--
-- 说明: 本脚本仅包含 DDL (表结构/索引/触发器)，
--        不包含任何 INSERT 样例数据.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Part 1: PRAGMA 配置
-- ----------------------------------------------------------------------------

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -8000;
PRAGMA mmap_size = 268435456;
PRAGMA temp_store = MEMORY;

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
    gallery_images      TEXT    NOT NULL DEFAULT '[]'
                        CHECK (json_valid(gallery_images)
                           AND json_array_length(gallery_images) >= 2),

    -- --- 相关推荐 (PRD 6.2.6) ---
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
-- Part 3: 索引
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_rarity_level
    ON trips(rarity_level);

CREATE INDEX IF NOT EXISTS idx_destination
    ON trips(destination);

CREATE INDEX IF NOT EXISTS idx_created_at
    ON trips(created_at DESC);

-- ============================================================================
-- Part 4: FTS5 全文搜索
-- ============================================================================

CREATE VIRTUAL TABLE IF NOT EXISTS trips_fts USING fts5(
    title,
    subtitle,
    destination,
    destination_region,
    experience_type_tags,
    visual_style_tags,
    content='trips',
    content_rowid='id',
    tokenize='unicode61'
);

-- INSERT 同步触发器
CREATE TRIGGER IF NOT EXISTS trips_ai AFTER INSERT ON trips BEGIN
    INSERT INTO trips_fts(rowid, title, subtitle, destination, destination_region,
                          experience_type_tags, visual_style_tags)
    VALUES (new.id, new.title, new.subtitle, new.destination, new.destination_region,
            new.experience_type_tags, new.visual_style_tags);
END;

-- DELETE 同步触发器
CREATE TRIGGER IF NOT EXISTS trips_ad AFTER DELETE ON trips BEGIN
    INSERT INTO trips_fts(trips_fts, rowid, title, subtitle, destination,
                          destination_region, experience_type_tags, visual_style_tags)
    VALUES ('delete', old.id, old.title, old.subtitle, old.destination,
            old.destination_region, old.experience_type_tags, old.visual_style_tags);
END;

-- UPDATE 同步触发器
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
-- Part 5: updated_at 自动更新触发器
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS trips_update_timestamp
    AFTER UPDATE ON trips
    FOR EACH ROW
    WHEN old.updated_at = new.updated_at
BEGIN
    UPDATE trips SET updated_at = datetime('now') WHERE id = old.id;
END;
