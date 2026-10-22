# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 外部多智能体总经理决策大脑 (External GM Multi-Agent Brain)
【设计定位】：纯数据库驱动决策，大算力专注于高维博弈，零盲目读写内存。
核心规范：
1. 前置质检强断言：必须校验目标快照已获得确定性脚本审计凭证 (PASS_VERIFIED)，否则拒绝执行决策。
2. 纯数据库查询：100% 从 team_monthly_stats、player_monthly_stats 与市场池消费数据，严禁硬编码交易资产。
3. 超巨引力法则：活动焦点球员与静态保护名单从交易候选中排除。
4. 数据不足以确认 CBA 时输出待复核候选，不将粗略工资差额宣称为可用空间或合法交易。
5. 人类总指挥终审：建议需要人工批准；交易候选还必须完成 CBA 复核，禁止擅自热写内存。
"""
import os
import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
import config
from snapshot_integrity import file_sha256, snapshot_digest, write_json_atomic

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "database", "league_state.sqlite")
SNAPSHOTS_DIR = os.path.join(PROJECT_DIR, "database", "snapshots")

# ==============================================================================
# 1. 超巨引力法则 (神圣非卖品基石 - 拥有绝对不可交易豁免权)
# ==============================================================================
TIER_0_SUPERSTARS = {
    "Tyrese Haliburton": {
        "archetype": "POINT_GOD_PLAYMAKER",
        "gravitational_system": "PACE_&_SPACE",
        "is_untouchable": True,
        "reason": "玩家自建绝对基石 / 纯净核心大脑，严禁任何交易挂牌！"
    },
    "Stephen Curry": {
        "archetype": "OFF_BALL_GRAVITY_SNIPER",
        "gravitational_system": "PACE_&_SPACE",
        "is_untouchable": True,
        "reason": "勇士队魂与王朝图腾，严禁交易！"
    },
    "LeBron James": {
        "archetype": "ALL_AROUND_POINT_FORWARD",
        "gravitational_system": "PERIMETER_CENTRIC",
        "is_untouchable": True,
        "reason": "历史级超巨门面，严禁交易！"
    },
    "Giannis Antetokounmpo": {
        "archetype": "TRANSITION_POWER_FORCE",
        "gravitational_system": "DEFENSE",
        "is_untouchable": True,
        "reason": "雄鹿冠军绝对基石，严禁交易！"
    },
    "Nikola Jokic": {
        "archetype": "HIGH_POST_HUB",
        "gravitational_system": "BALANCED",
        "is_untouchable": True,
        "reason": "掘金战术枢纽大核，严禁交易！"
    },
    "Luka Doncic": {
        "archetype": "HELIO_CENTRIC_MAESTRO",
        "gravitational_system": "PERIMETER_CENTRIC",
        "is_untouchable": True,
        "reason": "独行侠基石大核，严禁交易！"
    }
}

class GMEngine:
    def __init__(
        self,
        db_path: str = DB_PATH,
        snapshots_dir: str = SNAPSHOTS_DIR,
        player_pool_db_path: Optional[str] = None,
    ):
        self.db_path = db_path
        self.snapshots_dir = snapshots_dir
        self.player_pool_db_path = player_pool_db_path or os.path.join(
            os.path.dirname(os.path.abspath(db_path)), "player_pool.sqlite"
        )

    def _connect_read_only(self) -> sqlite3.Connection:
        """Open the league snapshot database in SQLite read-only mode."""
        db_uri = Path(self.db_path).resolve().as_uri() + "?mode=ro"
        return sqlite3.connect(db_uri, uri=True)

    def verify_snapshot_gate(self, snapshot_id: str) -> Dict:
        """
        前置质检闸门：校验快照是否具备独立的 PASS_VERIFIED 质检合格盖章
        """
        audit_file = os.path.join(self.snapshots_dir, f"ai_sampling_audit_{snapshot_id}.json")
        manifest_file = os.path.join(self.snapshots_dir, f"ingest_manifest_{snapshot_id}.json")
        if not os.path.exists(audit_file):
            raise RuntimeError(f"【GM 决策闸门拦截】快照 {snapshot_id} 未进行 AI 抽样质检，缺少审计凭据: {audit_file}")
        if not os.path.exists(manifest_file):
            raise RuntimeError(f"【GM 决策闸门拦截】快照 {snapshot_id} 缺少入库清单。")
        
        with open(audit_file, "r", encoding="utf-8") as f:
            audit_data = json.load(f)
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        if audit_data.get("snapshot_id") != snapshot_id or manifest.get("snapshot_id") != snapshot_id:
            raise RuntimeError("【GM 决策闸门拦截】审计或入库清单的 snapshot_id 与请求不一致。")
        if manifest.get("status") != "INGEST_SUCCESS" or audit_data.get("save_id") != manifest.get("save_id"):
            raise RuntimeError("【GM 决策闸门拦截】入库状态失败，或凭证来自不同游戏存档。")
        if audit_data.get("verifier") != "deterministic_script" or audit_data.get("verdict") != "PASS_VERIFIED":
            raise RuntimeError(f"【GM 决策闸门拦截】快照 {snapshot_id} 脚本质检评定为 [{audit_data.get('verdict')}]，未达到 PASS_VERIFIED，拒绝执行决策！")
        checks = audit_data.get("checks", {})
        if not checks or not all(checks.values()):
            raise RuntimeError("【GM 决策闸门拦截】审计凭证包含失败或缺失的校验项。")

        current_manifest_hash = file_sha256(manifest_file)
        audit_binding = audit_data.get("manifest_binding", {})
        if audit_binding.get("manifest_sha256") != current_manifest_hash:
            raise RuntimeError("【GM 决策闸门拦截】入库清单在审计后发生变化，需重新审计。")
        if not os.path.isfile(self.player_pool_db_path):
            raise RuntimeError("【GM 决策闸门拦截】本存档球员池数据库不存在。")
        current_player_pool_hash = file_sha256(self.player_pool_db_path)
        expected_pool_hash = manifest.get("batch_binding", {}).get("player_pool_sha256")
        if (
            not expected_pool_hash
            or current_player_pool_hash != expected_pool_hash
            or current_player_pool_hash != audit_data.get("player_pool_sha256")
            or audit_data.get("player_pool_records") != manifest.get("batch_binding", {}).get("player_pool_records")
        ):
            raise RuntimeError("【GM 决策闸门拦截】球员池文件在审计后变化或凭证摘要不匹配。")
        with self._connect_read_only() as conn:
            current_digest = snapshot_digest(conn, snapshot_id)
            team_ids = {
                row[0] for row in conn.execute(
                    "SELECT team_id FROM team_monthly_stats WHERE snapshot_id=?", (snapshot_id,)
                )
            }
            team_count = conn.execute(
                "SELECT count(*) FROM team_monthly_stats WHERE snapshot_id=?", (snapshot_id,)
            ).fetchone()[0]
        expected_digest = manifest.get("batch_binding", {}).get("snapshot_digest_sha256")
        if not expected_digest or current_digest != expected_digest or current_digest != audit_data.get("database_digest_sha256"):
            raise RuntimeError("【GM 决策闸门拦截】数据库快照内容已变化或凭证摘要不匹配，需重新抓取并审计。")
        if team_ids != config.CORE_TEAM_IDS or team_count != 30:
            raise RuntimeError("【GM 决策闸门拦截】通过审计的快照当前不再包含完整的 30 队数据。")

        print(f"[+] 快照 {snapshot_id} 的脚本审计凭证与数据库摘要绑定通过 (PASS_VERIFIED，时间: {audit_data.get('audit_timestamp')})")
        return audit_data

    def get_verified_teams_stats(self, snapshot_id: str) -> List[Dict]:
        """纯数据库查询：从 team_monthly_stats 读取通过质检的 30 队数据"""
        conn = self._connect_read_only()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT team_id, team_abbr, total_salary, payroll, budget, cash, chemistry,
                   fan_interest, ticket_courtside, poe_off_pace, poe_on_ball, current_lifecycle_state
            FROM team_monthly_stats
            WHERE snapshot_id = ?
            ORDER BY team_id ASC
        """, (snapshot_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        if len(rows) != 30:
            raise RuntimeError(f"【数据源异常】快照 {snapshot_id} 中球队行数异常 (预期 30，实际 {len(rows)})")
        return rows

    def get_verified_season_rules(self, snapshot_id: str) -> Dict:
        """Read the season thresholds bound to this snapshot from the database."""
        with self._connect_read_only() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """SELECT s.season_year, s.season_code, s.salary_cap,
                          s.luxury_tax_threshold, s.first_apron, s.second_apron,
                          s.historical_draft_class_year
                   FROM monthly_snapshots AS m
                   JOIN seasons AS s ON s.season_year=m.season_year
                   WHERE m.snapshot_id=?""",
                (snapshot_id,),
            ).fetchone()
        if row is None or row["salary_cap"] is None or row["luxury_tax_threshold"] is None:
            raise RuntimeError(f"【数据源异常】快照 {snapshot_id} 缺少已登记的赛季工资规则。")
        if int(row["salary_cap"]) <= 0 or int(row["luxury_tax_threshold"]) <= 0:
            raise RuntimeError(f"【数据源异常】快照 {snapshot_id} 的工资帽或奢侈税线无效。")
        return dict(row)

    def get_verified_player_stats(
        self,
        snapshot_id: str,
        player_name: Optional[str] = None,
        face_id: Optional[int] = None,
    ) -> Optional[Dict]:
        """纯数据库查询：读取焦点自建球员实测攻传防能力与合同"""
        conn = self._connect_read_only()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if face_id is not None:
            cursor.execute("""
            SELECT player_name, position, three_point_rating, pass_accuracy_rating,
                   speed_rating, perimeter_defense_rating, salary_current_year, contract_years_left, face_id
            FROM player_monthly_stats
            WHERE snapshot_id = ? AND face_id = ? AND (? IS NULL OR player_name = ?)
            ORDER BY team_id
            LIMIT 2
            """, (snapshot_id, face_id, player_name, player_name))
        elif player_name:
            cursor.execute("""
            SELECT player_name, position, three_point_rating, pass_accuracy_rating,
                   speed_rating, perimeter_defense_rating, salary_current_year, contract_years_left, face_id
            FROM player_monthly_stats
            WHERE snapshot_id = ? AND player_name = ?
            ORDER BY team_id
            LIMIT 2
            """, (snapshot_id, player_name))
        else:
            conn.close()
            return None
        rows = cursor.fetchall()
        conn.close()
        if len(rows) > 1:
            raise RuntimeError(
                f"【数据源异常】快照 {snapshot_id} 中焦点球员身份不唯一 "
                f"(name={player_name!r}, face_id={face_id!r})"
            )
        return dict(rows[0]) if rows else None

    def get_team_roster(self, snapshot_id: str, team_id: int) -> List[Dict]:
        """纯数据库查询：获取指定球队在当前快照中的完整阵容与合同"""
        conn = self._connect_read_only()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT player_name, position, three_point_rating, pass_accuracy_rating,
                   speed_rating, perimeter_defense_rating, salary_current_year, contract_years_left, face_id
            FROM player_monthly_stats
            WHERE snapshot_id = ? AND team_id = ?
            ORDER BY salary_current_year DESC
        """, (snapshot_id, team_id))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def check_cba_salary_match(self, out_sal_a: int, out_sal_b: int) -> Tuple[bool, str]:
        """CBA 125% + 10万美元 薪资配平校验"""
        max_allowed_b = int(out_sal_a * 1.25) + 100_000
        max_allowed_a = int(out_sal_b * 1.25) + 100_000
        
        if out_sal_b <= max_allowed_b and out_sal_a <= max_allowed_a:
            return True, f"符合 CBA 125% 配平规则 (A送出 ${out_sal_a:,} / B送出 ${out_sal_b:,})"
        else:
            return False, f"薪资超出 CBA 配平允许浮动范围 (差额: ${abs(out_sal_a - out_sal_b):,})"

    def generate_gm_proposals(self, snapshot_id: str = "2021-2022_M01_NOV") -> Dict:
        """
        基于纯数据库实测源，驱动 30 支球队多智能体博弈决策：
        1. 严格校验前置 PASS_VERIFIED
        2. 全联盟财务超税与薪金空间阶梯构建 (严谨区分 $112.4M 工资帽与 $136.6M 奢侈税线)
        3. 纯数据库读取真实阵容资产；薪资配平数据不完整时只输出待复核候选
        4. 焦点球员与超巨绝对保护核验
        """
        # 1. 闸门核验
        audit_info = self.verify_snapshot_gate(snapshot_id)
        teams = self.get_verified_teams_stats(snapshot_id)
        season_rules = self.get_verified_season_rules(snapshot_id)
        active_player = audit_info.get("active_player", {})
        active_player_name = active_player.get("player_name")
        active_player_face_id = active_player.get("face_id")
        player = self.get_verified_player_stats(
            snapshot_id, active_player_name, active_player_face_id
        ) if active_player_name and active_player_face_id is not None else None

        print(f"[*] 正在执行 GM 智能体多维博弈推演 (基于纯数据库快照: {snapshot_id})...")

        salary_cap = int(season_rules["salary_cap"])
        luxury_tax_line = int(season_rules["luxury_tax_threshold"])
        tax_overwhelmed = []  # 实测工资高于该快照绑定的奢侈税线
        cap_rich_rebuilders = []  # 实测总薪资低于工资帽的球队，仅为 gross-room 代理值
        treadmill_teams = []  # 工资帽与奢侈税线之间的球队

        for t in teams:
            sal = t["total_salary"]
            if sal > luxury_tax_line:
                tax_overwhelmed.append({**t, "tax_over": sal - luxury_tax_line})
            elif sal < salary_cap:
                cap_rich_rebuilders.append({**t, "gross_room_proxy": salary_cap - sal})
            else:
                treadmill_teams.append(t)

        tax_overwhelmed.sort(key=lambda x: x["tax_over"], reverse=True)
        cap_rich_rebuilders.sort(key=lambda x: x["gross_room_proxy"], reverse=True)

        # 3. 动态寻找买家与卖家，从纯数据库提取真实球员资产撮合
        trade_proposals = []
        if tax_overwhelmed and cap_rich_rebuilders:
            seller = tax_overwhelmed[0]  # 如 GSW ($175M, 超税 $38.7M)
            buyer = cap_rich_rebuilders[0]  # 如 OKC ($50M, 空间 $61.9M)

            seller_roster = self.get_team_roster(snapshot_id, seller["team_id"])
            protected_names = set(TIER_0_SUPERSTARS)
            if active_player_name:
                protected_names.add(active_player_name)

            # 严格筛选非基石的真实球员资产 (年薪 > $5M，且不在 TIER_0_SUPERSTARS 中)
            tradeable_seller_players = [
                p for p in seller_roster
                if p["player_name"] not in protected_names and p["salary_current_year"] >= 5_000_000
            ]

            if tradeable_seller_players:
                # 选取一位真实球员 (如 Wiggins 或 Wiseman)
                target_player = tradeable_seller_players[0]
                p_name = target_player["player_name"]
                p_sal = target_player["salary_current_year"]
                p_pos = target_player["position"]
                p_yrs = target_player["contract_years_left"]

                gross_room_proxy = buyer["gross_room_proxy"]
                # Captured data does not include cap holds, roster charges,
                # exceptions, or the complete incoming/outgoing salary ledger.
                cba_legal = None
                cba_rule = "REQUIRES_FULL_CBA_REVIEW"

                trade_item = {
                    "proposal_id": f"TRADE_PROP_{snapshot_id}_01",
                    "status": "PROPOSED_REQUIRES_CBA_REVIEW",
                    "team_a": {
                        "abbr": seller["team_abbr"],
                        "role": "SELLER_TAX_RELIEF",
                        "total_salary_before": seller["total_salary"],
                        "tax_over_before": seller["tax_over"],
                        "assets_offered": [
                            {
                                "asset_type": "REAL_ROSTER_PLAYER",
                                "player_name": p_name,
                                "position": p_pos,
                                "salary": p_sal,
                                "contract_years_left": p_yrs,
                                "desc": f"真实在册球员 {p_name} ({p_pos}, 年薪 ${p_sal:,}, 剩余 {p_yrs} 年)"
                            },
                        ]
                    },
                    "team_b": {
                        "abbr": buyer["team_abbr"],
                        "role": "BUYER_CAP_ABSORBER",
                        "total_salary_before": buyer["total_salary"],
                        "gross_room_proxy_below_cap": gross_room_proxy,
                        "assets_offered": [
                            {
                                "asset_type": "UNVERIFIED_CAP_ROOM_PROXY",
                                "salary_absorbed": p_sal,
                                "desc": f"工资总额低于静态工资帽约 ${gross_room_proxy:,}；未扣除 cap holds 或 roster charges"
                            }
                        ]
                    },
                    "cba_validation": {
                        "is_legal": cba_legal,
                        "rule": cba_rule,
                        "detail": "当前快照不足以证明薪资配平或例外适用；必须按完整 CBA 工资账本复核。"
                    },
                    "superstar_protection_audit": {
                        "active_player_involved": p_name == active_player_name,
                        "tier_0_superstars_involved": p_name in TIER_0_SUPERSTARS,
                        "protected_names": sorted(protected_names),
                        "verdict": (
                            "PASS (活动焦点球员与静态保护名单已从候选资产中排除)"
                            if p_name not in protected_names
                            else "FAIL (候选资产命中了保护名单)"
                        )
                    },
                    "strategic_reasoning": (
                        f"【候选卖方 {seller['team_abbr']}】：当前实测总薪资为 ${seller['total_salary']:,}，高于静态奢侈税线。"
                        f"候选资产 {p_name} 的本季薪资为 ${p_sal:,}。\n"
                        f"【候选买方 {buyer['team_abbr']}】：实测工资总额与静态工资帽相差约 ${gross_room_proxy:,}。"
                        "该差额不等于 CBA 可用薪资空间；球队动机、选秀权所有权与交易合法性需补充真实数据后复核。"
                    )
                }
                trade_proposals.append(trade_item)

        # Legacy heuristic tactics are retired. Observed on-ball 7 conflicts
        # with the old documented 0..4 enum; do not invent increases up to 12.
        # Player-triggered web GM uses gm_core.tactics and an explicit enum.
        tactical_proposals = []

        result = {
            "snapshot_id": snapshot_id,
            "generated_at": datetime.now().isoformat(),
            "audit_prerequisite": {
                "status": "VERIFIED_VALID",
                "verifier": audit_info.get("verifier"),
                "verdict": audit_info.get("verdict")
            },
            "financial_landscape": {
                "season_year": season_rules["season_year"],
                "season_code": season_rules["season_code"],
                "salary_cap_from_database": salary_cap,
                "luxury_tax_threshold_from_database": luxury_tax_line,
                "luxury_tax_teams_count": len(tax_overwhelmed),
                "below_cap_proxy_teams_count": len(cap_rich_rebuilders),
                "top_tax_team": tax_overwhelmed[0]["team_abbr"] if tax_overwhelmed else "None",
                "top_below_cap_proxy_team": cap_rich_rebuilders[0]["team_abbr"] if cap_rich_rebuilders else "None"
            },
            "active_player_status": {
                "name": player["player_name"] if player else "N/A",
                "position": player["position"] if player else "N/A",
                "three_point": player["three_point_rating"] if player else "N/A",
                "contract_salary": player["salary_current_year"] if player else "N/A",
                "protection_status": (
                    "SACRED_UNTOUCHABLE (100% 玩家自主权)"
                    if player else "UNVERIFIED_ACTIVE_PLAYER_IDENTITY"
                )
            },
            "proposed_trades": trade_proposals,
            "proposed_tactics": tactical_proposals[:5],  # 截取前 5 队代表
            "execution_policy": "HUMAN_APPROVAL_REQUIRED (严格禁止未经批准写入游戏内存)"
        }

        # 落盘决策建议白皮书
        out_file = os.path.join(self.snapshots_dir, f"gm_decision_manifest_{snapshot_id}.json")
        write_json_atomic(out_file, result)

        print(f"[+] GM 决策多维博弈推演完成！")
        print(f"    - 超税队伍: {len(tax_overwhelmed)} 支 (最高: {result['financial_landscape']['top_tax_team']})")
        print(f"    - 工资帽以下代理队伍: {len(cap_rich_rebuilders)} 支 (差额最大: {result['financial_landscape']['top_below_cap_proxy_team']})")
        print(f"    - 交易候选: {len(trade_proposals)} 项 (待 CBA 复核，不可直接执行)")
        print(f"    - 决策建议清单已落盘: {out_file}\n")
        return result

if __name__ == "__main__":
    import argparse
    from save_context import resolve_context

    parser = argparse.ArgumentParser(description="基于通过校验的 SQLite 快照生成 GM 建议")
    parser.add_argument("--snapshot", default="2021-2022_M01_NOV")
    parser.add_argument("--save-id", default=None)
    args = parser.parse_args()
    context = resolve_context(args.save_id)
    engine = GMEngine(context["db_path"], context["snapshots_dir"], context["player_pool_db_path"])
    engine.generate_gm_proposals(args.snapshot)
