"""Render the collected Git evidence as a bounded Human decision table."""
import json
from pathlib import Path

SUMMARIES = '''上下文管理 Stage2 收尾审核派单与按 A v2 修订任务包
上下文管理迁入全局机制结构的派单
上下文管理结构迁移审查修正派单
上下文机制开发总结的审核派单
上下文机制开发总结修订派单
开发总结中稳定实现基线标签修正派单
确定性工具收益与风险评估派单
确定性工具 registry 证据指针修正派单
check-jsonschema 安装验证任务定义
check-jsonschema 按需集成验证；唯一补丁与 master 等价
check-jsonschema 网络与版本边界修正及连续执行授权
mutmut WSL 安装验证派单
mutmut 远端 master 证据语义修正派单
Cosmic Ray WSL 对比验证派单
Antigravity 接入说明及 promptfoo 离线验证派单
Antigravity 后端接入指南和 Cosmic Ray 续作派单
promptfoo CLI 离线验证、canonical 接入和交接简报
promptfoo CLI 离线验证候选及 Windows 超时、工作目录、版本探测修正
OpenFastTrace 候选、回执及完整性/Java 运行时门
cargo-ovft 安装候选、registry wrapper、版本探测与 smoke 修正
既有 Cosmic Ray 安装对账、wrapper、回执脱敏修正
cargo-ovft 候选的独立审核记录，不是新的安装实现
Python 集合覆盖检查器、CLI 错误和 wrapper 校验
集合覆盖机器验收、CLI 错误测试、路径泄露修正及接入记录
provenance 与 reference graph 契约盘点
实现方案建模阶段的需求模型、决策与完成记录
阶段协同推演激活准备、审核与完成指针
阶段协同推演 P1 canonical 实现及审核修正、完成指针
阶段协同推演需求建模及复核、provenance 修正
实现方案建模 Stage02 证据、远端验证和完成指针
阶段协同推演 Stage05 步骤拆分、复核及完成记录
阶段协同推演测试审核建模及 Stage06/P1 执行授权派单
阶段协同推演 Stage02 信息收集与审核完成记录
阶段协同推演 P3–P7 集成实现及最终审核、完成指针
阶段协同推演 P2 机器契约、完成指针及单模型串行治理记录
协同推演粒度修订及 Stage02 恢复执行记录
阶段协同推演 Stage04 方案建模及完成指针
阶段协同推演 Stage03 结果建模及完成指针
单模型串行工作流默认规则文档
全局通讯系统、Stage07 修正证据、复核及 master 集成候选派单
模型能力/可用性路由的资格测试、v2 测试套件及 Gemini 重测
模型路由 master 集成回执和 run 关闭记录
Stage04 根因替换 v2、receipt Git blob 绑定与字节规范化
correction-003 修正及 ownership-provenance 架构阻塞证据
Stage04 后继候选重冻结及三项阻塞问题修正记录
correction-003 独立审核 FIX_REQUIRED 结果
Stage04 根因替换 v2 的独立审核 PASS 记录
structural-provenance 上游修正；声明/事实通道及 B1/B2 问题关闭
跨区域 applicability correction-003 修正与冻结记录
T2 后继重冻结、SR-001/SR-002 修正；提交仍声明一个 residual
Stage04 根因替换 v1 候选及完成指针自指修正
Stage04 根因替换 v1 的 require-fixes 审核记录
角色/窗口/上下文路由集成、可选重试语义及 Human 决策记录
Stage04 reentry 审核、前台交接、manifest 与 Human 顺序授权
OS 初始化任务包与 run 证据；未据此宣称初始化全部完成
Cowork Opus5 注册审核、发布授权与 master 发布记录
ChatGPT 本地文件/终端能力任务初始化及派单导航
Human 阶段对齐推演；末轮 CHANGES_REQUIRED，原 W6 已明确冻结此前驱
Human 授权码最小长度规则简化候选
ChatGPT 插件能力目录任务初始化；未据此宣称目录实现完成
本地主机控制基线的集成后远端审核派单
Claude Code Opus5 路由注册及 authority blob 绑定修正
T2 续作控制、审核接收、最终修正派单与状态记录
T2 结构绑定 refinement 提议；等待 CM-v2 Human 确认的控制记录
T3 归档/大任务工作流控制、sender index 规范化及派单
Task0 关闭证据修复、最终审核与 Human 接受记录
任务纪律回执及测量工具修正：显式 ref、路径台账、读取失败与遍历停止点
文档/实际世界一致性测量 Phase1、完成指针及远端读回 SHA 补录'''.splitlines()

def compact(target: Path) -> None:
    source = target / '未合并分支快照_v1.json'
    data = json.loads(source.read_text(encoding='utf-8'))
    if 'commit_ledger' in data:
        return
    rows = data['branches']
    if len(rows) != len(SUMMARIES):
        raise RuntimeError('The hand-described snapshot changed; do not misassign work summaries')
    ledger = {}
    for index, row in enumerate(rows, 1):
        row['id'] = index
        row['work_summary'] = SUMMARIES[index - 1]
        for commit in row['commits']:
            ledger[commit['sha']] = commit
        row['commits'] = [c['sha'] for c in row['commits']]
        row.pop('changed_paths')
    data['commit_ledger'] = ledger
    data['snapshot_limits'] = 'Work summaries describe submitted artifacts, not fresh correctness acceptance. Full repeated path lists are intentionally omitted; top path groups and counts are retained. All commit identities and subjects are normalized in commit_ledger.'
    source.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    intro = ['# 未合并分支：Human 决策总表', '',
             f'比较基准：master `{data["baseline_master"]}`。', '',
             f'已核对 {data["live_remote_ref_count"]} 个实时远端分支、{data["local_ref_count"]} 个本地分支；'
             f'未合并引用 {data["unmerged_ref_count"]} 个，相同 HEAD 合为 {len(rows)} 组。', '',
             '编号按最早未合入提交的 committer 时间排序；共享祖先会有相同起始时间。这不是任务完成时间，也不是批准或自动合并次序。',
             '全部名称、精确 SHA、起止时间、patch 等价数及末端提交见详细清单；完整提交元数据见 JSON。',
             '“工作”指提交记录所载产物，不声称本轮重新验收通过；派单、审核、冻结分支均明确标注。', '',
             '| 编号 | 分支（远端名称；本地同 HEAD 别名见详细清单） | 提交记录所载工作 |',
             '| --- | --- | --- |']
    detail = ['# 未合并分支详细证据', '', f'比较基准：master `{data["baseline_master"]}`。', '',
              '分支引用来自当前本地 heads 和实时 ls-remote，不把陈旧 remote-tracking-only 引用计入。',
              '完整提交台账存于同目录 JSON 的 commit_ledger，各分支 commits 列表引用它；本文件只展示末端八条提交，避免重复铺开共同祖先。', '']
    for row in rows:
        primary = next((r['name'] for r in row['refs'] if r['source'] == 'remote'), row['refs'][0]['name'])
        intro.append(f'| {row["id"]:02d} | `{primary}` | {row["work_summary"]} |')
        detail += [f'## {row["id"]:02d}. {primary}', '', row['work_summary'], '',
                   '- 引用：' + '; '.join(r['source'] + ':' + r['name'] for r in row['refs']),
                   f'- 精确 HEAD：`{row["head"]}`',
                   f'- 未合入提交时间：{row["first_unique_commit_time"]} 至 {row["latest_unique_commit_time"]}',
                   f'- 未合入提交 {row["unmerged_commit_count"]}；净变更路径 {row["net_changed_path_count"]}；'
                   f'新补丁 {row["patch_new"]}；master 等价补丁 {row["patch_equivalent_in_master"]}。']
        if row['contained_by']:
            detail += ['- 已包含于其他清单 tip：' + ', '.join('`' + s[:12] + '`' for s in row['contained_by'])]
        detail += ['- 涉及区域：' + '; '.join(f'{p} ({n})' for p, n in row['top_path_groups']), '', '末端提交（最多八条）：', '']
        detail += ['- `' + sha[:12] + '` ' + ledger[sha]['subject'] for sha in row['commits'][-8:]]
        detail += ['', 'Human 决定：待定。', '']
    intro += ['', '特别说明：10 号只有一个未合入提交，但其补丁与 master 等价；不能把“历史未合并”当成“功能缺失”。',
              '58 号是 W6 已冻结的前驱且留下 CHANGES_REQUIRED，不得将其描述为已通过候选。',
              '本轮未合并或删除上述任一分支；待 Human 批准后再按时间与实际 Git 依赖实施。', '']
    (target / '未合并分支总表_v1.md').write_text('\n'.join(intro), encoding='utf-8')
    (target / '未合并分支清单_v1.md').write_text('\n'.join(detail), encoding='utf-8')
    print(f'Human table: {len(rows)} groups; unique commit ledger: {len(ledger)}')

if __name__ == '__main__':
    compact(Path(__file__).resolve().parents[1] / '02_信息收集')
