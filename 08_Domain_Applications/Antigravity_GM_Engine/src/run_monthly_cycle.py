# -*- coding: utf-8 -*-
"""Player-triggered data-only workflow: backup -> capture -> audit -> stop."""
import argparse
import os
import sqlite3
from datetime import datetime, timezone

from auto_pipeline_ingest import run_automated_ingestion
from audit_sampling import run_ai_sampling_audit
from save_context import resolve_context


def _write_report(path: str, manifest: dict, audit: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        f"# NBA 2K22 数据采集报告：{manifest['snapshot_id']}",
        "",
        f"- 存档 ID：`{manifest['save_id']}`",
        f"- 入库时间 (UTC)：`{manifest['timestamp']}`",
        f"- 脚本质检：`{audit['verdict']}` | 校验项：{sum(audit['checks'].values())}/{len(audit['checks'])}",
        f"- 数据摘要：`{audit['database_digest_sha256']}`",
        f"- 球队：{manifest['ingested_counts']['teams']} 支；现役球员：{manifest['ingested_counts']['active_players']} 人；"
        f"制服组原始结构：{manifest['ingested_counts']['staff_pool_observations']} 条",
        ("- 制服组：完整目录槽位采集，在职员工归属使用双向角色指针。" if manifest.get('quality_metrics', {}).get('source_extension_profile') else
         "- 制服组归属：未验证。"),
        ("- 战绩/比赛统计：当前赛季累计数据来自统计表；场均数据由 Python 计算，月度/逐场明细未观测。" if manifest.get('quality_metrics', {}).get('source_extension_profile') else
         "- 战绩/比赛统计：未观测，保持 NULL。"),
        "",
        "## 阶段交付",
        "",
        "- 状态：`DATA_READY_AWAITING_PLAYER`。本次只完成数据采集与审计。",
        "- GM 决策：未启动；由玩家另行找到 GM 模型并明确触发。",
        "- 游戏执行：未启动；须由玩家批准具体方案并另行交给执行窗口。",
        "",
    ]
    lines.extend([
        "",
        "## 可复核产物",
        "",
        f"- 入库清单：`{os.path.basename(manifest['artifacts']['manifest_json'])}`",
        f"- 抽样审计：`{os.path.basename(audit['artifact_path'])}`",
        "",
    ])
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as target:
        target.write("\n".join(lines))
        target.flush()
        os.fsync(target.fileno())
    os.replace(temp_path, path)


def run_cycle(
    season_year: int = 2022,
    month_idx: int = 1,
    month_name: str = "NOV",
    notes: str = "",
    save_id: str = None,
):
    from gm_state_io.lifecycle import operation
    with operation(save_id or 'legacy-shared','capture'):
        return _run_cycle(season_year,month_idx,month_name,notes,save_id)


def _run_cycle(season_year,month_idx,month_name,notes,save_id):
    context = resolve_context(save_id)
    db_path = context["db_path"]
    os.makedirs(context["backups_dir"], exist_ok=True)
    if os.path.isfile(db_path):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(
            context["backups_dir"],
            f"league_state_{context['save_id']}_{season_year}_M{month_idx:02d}_{timestamp}.sqlite",
        )
        source = sqlite3.connect(db_path)
        backup = sqlite3.connect(backup_path)
        try:
            source.backup(backup)
        finally:
            backup.close()
            source.close()
        print(f"[+] 数据库备份已创建: {backup_path}")

    manifest = run_automated_ingestion(
        season_year=season_year,
        month_idx=month_idx,
        month_name=month_name,
        save_id=save_id,
        db_path=db_path,
        snapshots_dir=context["snapshots_dir"],
        player_pool_db_path=context["player_pool_db_path"],
        notes=notes,
    )
    snapshot_id = manifest["snapshot_id"]
    audit = run_ai_sampling_audit(
        snapshot_id=snapshot_id,
        save_id=save_id,
        db_path=db_path,
        snapshots_dir=context["snapshots_dir"],
        player_pool_db_path=context["player_pool_db_path"],
    )
    audit_file = os.path.join(context["snapshots_dir"], f"ai_sampling_audit_{snapshot_id}.json")
    audit["artifact_path"] = audit_file

    report_file = os.path.join(context["snapshots_dir"], f"DATA_REPORT_{snapshot_id}.md")
    _write_report(report_file, manifest, audit)
    print(f"[+] 数据采集与审计完成。审计凭证: {audit_file}")
    print("[+] DATA_READY_AWAITING_PLAYER：GM 决策和游戏执行均待玩家分别触发。")
    print(f"[+] 报告: {report_file}")
    return {
        "snapshot_id": snapshot_id,
        "manifest": manifest,
        "audit": audit,
        "stage_status": "DATA_READY_AWAITING_PLAYER",
        "gm_decision_started": False,
        "game_execution_started": False,
        "report_file": report_file,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="仅采集真实数据和完成脚本审计；不启动 GM 决策或游戏执行")
    parser.add_argument("--season", type=int, default=2022)
    parser.add_argument("--month", type=int, default=1)
    parser.add_argument("--name", type=str, default="NOV")
    parser.add_argument("--notes", type=str, default="")
    parser.add_argument("--save-id", type=str, default=None, help="游戏存档 ID；省略时沿用旧共享数据库")
    args = parser.parse_args()
    run_cycle(args.season, args.month, args.name, args.notes, args.save_id)
