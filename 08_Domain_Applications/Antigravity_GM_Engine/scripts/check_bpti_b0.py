"""Only the three player-authorized B0 static boundary checks. No game access."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_core.bpti import (
    AGENCY, CHAIN, SYSTEM_IDS, VERSION, ResearchIndex, validate_bpti_knowledge,
)
from gm_core.knowledge import Knowledge
from gm_knowledge import parser, run


def index():
    return Knowledge(ROOT / "web_gm/knowledge").bpti()


def timed_claims():
    payload = deepcopy(index().payload)
    # Pure synthetic claim-time projections, never real GM decisions or sources.
    template = deepcopy(payload["claims"][0])
    template.update(source_ids=["R1-S23"], claim_status="SUPPORTED_INTERPRETATION",
                    fact_valid_from="2014-01-01", fact_valid_to="2014-06-30",
                    knowledge_available_from="2014-06-30", retrospective_only=True)
    source = next(s for s in payload["sources"] if s["source_id"] == "R1-S23")
    source["publication_date"] = "2023"
    template.update(claim_id="SYNTHETIC_PAST", statement="2014 historical mechanism only")
    payload["claims"].append(template)
    future = deepcopy(template)
    future.update(claim_id="SYNTHETIC_FUTURE", statement="FUTURE_FINALS_2022_RESULT",
                  fact_valid_from="2022-06-01", fact_valid_to="2022-06-30",
                  knowledge_available_from="2022-06-30")
    payload["claims"].append(future)
    return ResearchIndex(payload)


def contract_examples():
    base = dict(schema_version=VERSION, evidence_claim_ids=["R1-C-MOTION_READ_REACT"])
    return [
        dict(**base, object_type="SystemCard", system_id=SYSTEM_IDS[0],
             title="Contract illustration, not a B1 operational card",
             role_requirements=["CONNECTOR"],
             advantage_chain={k:"Basketball explanation: " + k for k in CHAIN},
             player_agency=sorted(AGENCY), defensive_counter_options=["SWITCH"],
             second_answers=["BACKDOOR"], known_failure_conditions=["READ_NOT_AVAILABLE"],
             roster_budget_tradeoffs=["Requires passing roles"], observable_signals=["MECHANISM"],
             native_binding_refs=[], status="REFERENCE_ONLY"),
        dict(**base, object_type="TeamIdentity", identity_id="CONTRACT_DEMO",
             team_abbr="GSW", historical_seed_as_of="2021-10-19",
             franchise_value_claim_ids=[], historical_coach_claim_ids=[], unknown_values=["SEED_NOT_ASSESSED"],
             system_candidates=[SYSTEM_IDS[0]], confidence="HISTORICAL_SEED_ONLY",
             operational_link="NOT_BOUND_TO_ANY_SAVE", status="HISTORICAL_SEED_ONLY"),
        dict(**base, object_type="NativeBinding", binding_id="CONTRACT_DEMO",
             system_id=SYSTEM_IDS[0], basketball_intent="Movement responsibility",
             field_candidates=["coach.ActiveSystem"], mapping_status="UNKNOWN_NATIVE_BEHAVIOR",
             behavior_effect="UNKNOWN", unknowns=["CRC_BEHAVIOR_UNVERIFIED"],
             fallback="HOLD_RESEARCH", status="REFERENCE_ONLY"),
        dict(**base, object_type="SystemBlueprint", blueprint_id="CONTRACT_DEMO",
             identity_ref="CONTRACT_DEMO", primary_system=SYSTEM_IDS[0], secondary_systems=[],
             source_binding={}, team_id=0, coach_ref="REQUIRES_EXISTING_M3_COACH_REF",
             player_role_refs=[], first_advantage="Movement", opponent_counter="Switch",
             second_answer="Backdoor", native_binding_refs=[],
             internal_alternatives=["HOLD", "INTERNAL", "MARKET"],
             unknowns=["NOT_BOUND_TO_A_GAME"], status="DRAFT_UNAPPROVED"),
    ]


class B0AuthorizedChecks(unittest.TestCase):
    def test_01_missing_or_unreviewed_source_cannot_be_verified(self):
        k = index()
        self.assertEqual(len([c for c in k.claims.values() if c.get("system_id")]), 10)
        self.assertEqual(len([c for c in k.claims.values() if c.get("team_abbr")]), 30)
        for sid in ("LAL-S2", "POR-S2"):
            self.assertEqual(k.sources[sid]["source_status"], "SOURCE_MISSING")
        for cid in ("R1-C-MOTION_READ_REACT", "R2-T-LAL-01"):
            changed = deepcopy(k.claims[cid])
            changed.update(claim_status="VERIFIED", verification_ref="synthetic caller assertion")
            with self.assertRaisesRegex(ValueError, "BPTI_(VERIFIED|MISSING_SOURCE)"):
                k.validate_claim(changed)
        source = run(parser().parse_args(["bpti-source", "--source-id", "LAL-S2", "--audience", "RESEARCH"]))
        self.assertIsNone(source["source"]["url"])
        self.assertNotIn("", json.dumps(k.payload, ensure_ascii=False))

    def test_02_future_nba_events_hidden_but_earlier_retrospective_facts_allowed(self):
        k = timed_claims()
        selected = k.claim("SYNTHETIC_PAST", as_of="2021-10-19")
        self.assertEqual(selected["availability"], "AVAILABLE_AS_OF_CUTOFF")
        for when in ("2021-10-19", "2026-10-20"):
            blocked = k.claim("SYNTHETIC_FUTURE", as_of=when)
            self.assertEqual(blocked["availability"], "FUTURE_OR_HIDDEN")
            self.assertIsNone(blocked["claim"])
            evidence = k.reference_evidence(["SYNTHETIC_FUTURE"], as_of=when)
            self.assertNotIn("FUTURE_FINALS_2022_RESULT", json.dumps(evidence))
        self.assertIsNotNone(k.claim("SYNTHETIC_FUTURE", audience="RESEARCH")["claim"])
        self.assertIsNone(k.source("R1-S23", as_of="2021-10-19")["source"])
        self.assertIsNone(run(parser().parse_args(
            ["bpti-claim", "--claim-id", "R2-T-BOS-01", "--as-of", "2021-10-19"]))["claim"])

    def test_03_four_contracts_cannot_carry_native_writes_or_approval(self):
        k = index()
        for example in contract_examples():
            self.assertEqual(validate_bpti_knowledge(example, k, audience="RESEARCH"), example)
            native = deepcopy(example)
            native["native_intent"] = {"address":"0x1234", "raw_bytes":[1]}
            with self.assertRaisesRegex(ValueError, "BPTI_NO_NATIVE_PAYLOAD"):
                validate_bpti_knowledge(native, k, audience="RESEARCH")
            approved = deepcopy(example)
            approved["approved"] = True
            with self.assertRaisesRegex(ValueError, "CALLER_CANNOT_DECLARE_AUTHORITY"):
                validate_bpti_knowledge(approved, k, audience="RESEARCH")
        binding = contract_examples()[2]
        binding["mapping_status"] = "SUPPORTED_FIELD_DIRECTION"
        with self.assertRaisesRegex(ValueError, "BPTI_NATIVE_SUPPORT_NEEDS_PROJECT_INTERFACE_EVIDENCE"):
            validate_bpti_knowledge(binding, k, audience="RESEARCH")


if __name__ == "__main__":
    unittest.main(verbosity=2)
