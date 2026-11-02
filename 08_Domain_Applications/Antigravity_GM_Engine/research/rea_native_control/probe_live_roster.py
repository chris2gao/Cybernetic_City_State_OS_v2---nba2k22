"""Live Roster and Shot Tendency Probe Script.
Uses Checkpoint014 ReaCliTransport and native bindings to read live game values.
"""
import json
from pathlib import Path
import sys

_RESEARCH_DIR = Path(__file__).resolve().parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import contracts
import registry
import transport
from bulk_executor import canonical_encode

def run_probe(output_dir: Path, expected_pid: int = 10404):
    output_dir.mkdir(parents=True, exist_ok=True)
    reg = registry.NativeActionRegistry(_RESEARCH_DIR)

    # Load templates
    common_js = (_RESEARCH_DIR / 'runtime' / 'common.js').read_text(encoding='utf-8')
    gui_once_js = (_RESEARCH_DIR / 'runtime' / 'gui_once.js').read_text(encoding='utf-8')

    # Binding: player.get_stat_ui
    b_stat = reg.binding('player.get_stat_ui').to_dict()
    bindings = {'player.get_stat_ui': b_stat}

    req = {
        'action_id': 'PLAYER_PATCH_TENDENCIES',
        'request_id': 'probe_live_roster_001',
        'parameters': {
            'target_teams': [28, 1]
        }
    }
    limits = {
        'maximum_game_calls': 100,
        'read_bytes': 1048576,
        'is_live': True
    }

    action_handler_js = """
const u8 = (b, o = 0) => new DataView(b).getUint8(o);

function executeAction() {
  const targetTeams = [28, 1];
  const teamResults = {};

  for (const tid of targetTeams) {
    const t = team(tid);
    const b = read(t, 4696);
    const players = [];
    for (let i = 0; i < 15; i++) {
      const pp = ptrAt(b, i * 8);
      if (pp.isNull()) continue;
      const v = read(pp, 1264);
      const uid = u16(v, 0xf4);
      const firstName = text(v.slice(40, 80));
      const lastName = text(v.slice(0, 40));
      const fullName = (firstName + " " + lastName).trim();
      
      const tendencyVal = call('player.get_stat_ui', pp, 57);
      const rawByte = u8(read(pp.add(0x458), 1));

      players.push({
        slot: i,
        player_id: uid,
        name: fullName,
        shot_tendency_getter: tendencyVal,
        shot_tendency_raw: rawByte
      });
    }
    const teamAbbr = text(b.slice(0x30a, 0x314));
    teamResults[tid] = {
      team_id: tid,
      abbreviation: teamAbbr,
      player_count: players.length,
      players: players
    };
  }

  send({
    kind: 'chunk-execution-result',
    chunk_id: 'probe_001',
    chunk_digest: 'digest_probe_001',
    plan_digest: 'plan_probe_001',
    action_id: 'PLAYER_PATCH_TENDENCIES',
    batch_id: 'BATCH-PROBE-001',
    save_instance_id: 'MyLEAGUE0003',
    outcome: 'CHUNK_SUCCESS',
    details: teamResults,
    receipts: []
  });
}
"""

    script = (
        common_js + "\n" +
        action_handler_js + "\n" +
        gui_once_js
    )
    script = (
        script
        .replace('__REQUEST__', canonical_encode(req))
        .replace('__BINDINGS__', canonical_encode(bindings))
        .replace('__LIMITS__', canonical_encode(limits))
        .replace('__COACH_FIELDS__', '{}')
        .replace('__PLAYER_CONTRACT_FIELDS__', '{}')
    )

    live_ctx = transport.LiveExecutionContext(
        authorization_ref="Human conversation instruction 2026-11-01: 批准，许可授权，直接做批量的测试吧",
        allowed_action_ids=frozenset(["PLAYER_PATCH_TENDENCIES"]),
        maximum_game_calls=100,
        enabled=True,
        expected_pid=expected_pid
    )

    cli_transport = transport.ReaCliTransport(output_dir, live_ctx, duration_ms=10000)
    result = cli_transport.execute(
        script,
        action_id='PLAYER_PATCH_TENDENCIES',
        request_id='probe_req_001',
        maximum_game_calls=100
    )
    return result

if __name__ == '__main__':
    out_dir = Path("01_os/07_content/_runs/run-20261101-nba2k22-rea-controlled-live-bulk-pilot-001/07_测试执行/post_mutation_readback").resolve()
    res = run_probe(out_dir, expected_pid=10404)
    print(json.dumps(res, indent=2))
