# -*- coding: utf-8 -*-
"""
NBA 2K22 全联盟状态提取与持久化导出器 (League Dumper)
用法：
  python dumper.py
功能：
  1. 挂接 NBA2K22.exe 运行内存
  2. 提取 30 支核心现役球队的薪资、预算、化学反应
  3. 提取焦点球员状态
  4. 自动持久化写入 SQLite 数据库与 JSON 快照
"""
import os
import sys
import json
import sqlite3
from datetime import datetime

# 保证能引用同级模块
sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from scanner import LeagueScanner
import config

def init_db(db_path: str, schema_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()

def main():
    print("=" * 60)
    print("  NBA 2K22 Antigravity 外部 GM 引擎数据抓取工具")
    print("=" * 60)
    
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, "database", "league_state.sqlite")
    schema_path = os.path.join(project_dir, "database", "schema.sql")
    json_path = os.path.join(project_dir, "database", "league_snapshot.json")
    
    # 1. 初始化数据库
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    init_db(db_path, schema_path)
    print(f"[*] 本地数据库初始化成功: {db_path}")
    
    # 2. 挂接游戏内存
    print("[*] 正在探测并连接 NBA2K22.exe 游戏进程...")
    mem = GameMemory()
    print(f"[+] 成功挂接游戏进程! PID: {mem.pid}, 模块基址: 0x{mem.base_address:X}")
    
    scanner = LeagueScanner(mem)
    
    # 3. 扫描 30 支核心现役球队
    print("[*] 正在扫描全联盟 30 支现役球队状态...")
    teams = scanner.find_active_teams()
    print(f"[+] 成功捕获 {len(teams)} 支核心 NBA 球队数据！")
    
    # 4. 写入 SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for tid, t in teams.items():
        cursor.execute("""
            INSERT OR REPLACE INTO teams (
                team_id, abbreviation, city, name, memory_address, total_salary, payroll, budget, chemistry, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["team_id"],
            t["abbreviation"],
            t["city"],
            t["name"],
            hex(t["address"]),
            t["total_salary"],
            t["payroll"],
            t["budget"],
            t["chemistry"],
            datetime.now().isoformat()
        ))
    conn.commit()
    
    # 5. 读取焦点球员
    active_player = scanner.get_active_player()
    if active_player:
        print(f"\n[+] 捕获当前焦点球员: {active_player['first_name']} {active_player['last_name']}")
        print(f"    所属球队ID: {active_player['team_id']}")
        print(f"    本季薪水: ${active_player['salary_current_year']:,} | 剩余年限: {active_player['contract_years_left']} 年")
        print(f"    三分球能力: {active_player['three_point_rating']} | 传球准确度: {active_player['pass_accuracy_rating']}")
    
    # 6. 生成全局 JSON 快照
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "total_teams": len(teams),
        "teams": teams,
        "active_player": active_player
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"\n[+] 全局 JSON 快照已生成: {json_path}")
    
    conn.close()
    mem.close()
    print("\n[√] 存档数据标准化抓取全部完成！")

if __name__ == "__main__":
    main()
