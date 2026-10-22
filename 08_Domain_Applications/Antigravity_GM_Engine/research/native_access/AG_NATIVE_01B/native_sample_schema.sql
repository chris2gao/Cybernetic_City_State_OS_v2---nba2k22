-- =============================================================================
-- NBA2K22 原生数据深度挖掘独立 SQLite 样本库结构 (AG-NATIVE-01B)
-- 专用于原生内存记录到关系型数据模型的映射验证，不侵入现有生产数据库
-- =============================================================================

PRAGMA foreign_keys = ON;

-- 1. ROSTERDATA 数组描述符表 (67 个活跃数组 + 8 个空槽元数据)
CREATE TABLE IF NOT EXISTS roster_array_descriptors (
    slot_index INTEGER PRIMARY KEY,
    offset_from_manager INTEGER NOT NULL,
    offset_from_manager_hex TEXT NOT NULL,
    count INTEGER NOT NULL,
    array_pointer TEXT,
    inferred_stride INTEGER,
    size_in_heap INTEGER,
    object_name TEXT NOT NULL,
    family TEXT NOT NULL,
    getter_rva TEXT,
    status TEXT NOT NULL
);

-- 2. 球队基础映射表 (验证与死钱链表的关联)
CREATE TABLE IF NOT EXISTS teams (
    team_index INTEGER PRIMARY KEY,
    city TEXT,
    name TEXT,
    abbreviation TEXT,
    team_pointer TEXT NOT NULL,
    waived_salary_head_ptr TEXT
);

-- 3. 裁员死钱明细表 (WAIVED_SALARY, 原生 136 字节高精度解码)
CREATE TABLE IF NOT EXISTS waived_salaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_index INTEGER NOT NULL UNIQUE,
    team_index INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    season_1_amount INTEGER NOT NULL DEFAULT 0,
    season_2_amount INTEGER NOT NULL DEFAULT 0,
    season_3_amount INTEGER NOT NULL DEFAULT 0,
    season_4_amount INTEGER NOT NULL DEFAULT 0,
    season_5_amount INTEGER NOT NULL DEFAULT 0,
    season_6_amount INTEGER NOT NULL DEFAULT 0,
    total_dead_cap INTEGER NOT NULL,
    remaining_seasons INTEGER NOT NULL,
    is_stretched INTEGER NOT NULL DEFAULT 0,
    prev_record_ptr TEXT,
    team_ptr TEXT NOT NULL,
    provenance TEXT NOT NULL,
    FOREIGN KEY (team_index) REFERENCES teams(team_index)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_waived_salaries_team ON waived_salaries(team_index);
CREATE INDEX IF NOT EXISTS idx_waived_salaries_player ON waived_salaries(player_id);
CREATE INDEX IF NOT EXISTS idx_descriptors_family ON roster_array_descriptors(family);
