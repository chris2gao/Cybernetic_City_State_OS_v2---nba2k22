"""Only DEV25 B1-T1/T2/T3. Static files and synthetic projections; no game."""
from copy import deepcopy
import json
from itertools import islice
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_core.bpti import AGENCY, CHAIN, SYSTEM_IDS, ResearchIndex, validate_bpti_knowledge
from gm_core.knowledge import Knowledge
from gm_knowledge import parser, run

AS_OF = "2021-10-19"


def knowledge():
    return Knowledge(ROOT / "web_gm/knowledge").bpti()


def excerpt(location):
    with (ROOT / location["document"]).open(encoding="utf-8-sig") as stream:
        return "".join(islice(stream, location["line_start"] - 1, location["line_end"]))


class B1AuthorizedChecks(unittest.TestCase):
    def test_01_ten_cards_and_causal_content(self):
        index = knowledge()
        self.assertEqual(set(index.system_cards), set(SYSTEM_IDS))
        self.assertEqual(len(index.system_cards), 10)
        for card in index.system_cards.values():
            self.assertEqual(validate_bpti_knowledge(card, index, audience="RESEARCH"), card)
            self.assertEqual(set(card["advantage_chain"]), set(CHAIN))
            self.assertTrue(all(card["advantage_chain"].values()))
            self.assertEqual(set(card["player_agency"]), AGENCY)
            for field in ("role_requirements", "defensive_counter_options", "second_answers",
                          "known_failure_conditions", "roster_budget_tradeoffs", "observable_signals"):
                self.assertTrue(card[field], field)
            self.assertTrue(all(":" in role for role in card["role_requirements"]))
            for prefix in ("OUTCOME:", "MECHANISM:", "CONTEXT:", "NOT_FROM_BOX_SCORE:"):
                self.assertTrue(any(v.startswith(prefix) for v in card["observable_signals"]))
            self.assertEqual(card["native_binding_refs"], [])

    def test_02_bounded_cli_retrieval_and_traceability(self):
        index = knowledge()
        one = run(parser().parse_args(["bpti-system", "--system-id", "MOTION_READ_REACT", "--as-of", AS_OF]))
        self.assertEqual(one["card"]["system_id"], "MOTION_READ_REACT")
        by_id = index.search_systems(system_id="MOTION_READ_REACT", limit=1, as_of=AS_OF)
        self.assertEqual(by_id["returned_count"], 1)
        roles = run(parser().parse_args(["bpti-systems", "--role", "CONNECTOR", "--limit", "2", "--as-of", AS_OF]))
        self.assertEqual(roles["returned_count"], 2)
        self.assertTrue(roles["truncated"])
        counters = run(parser().parse_args(["bpti-systems", "--counter", "SWITCH", "--limit", "1", "--as-of", AS_OF]))
        self.assertEqual(counters["returned_count"], 1)
        self.assertTrue(counters["truncated"])
        self.assertTrue(all("advantage_chain" not in row for row in roles["systems"]))
        with self.assertRaisesRegex(ValueError, "LIMIT_1_TO_5"):
            index.search_systems(limit=10, audience="RESEARCH")
        for sid in SYSTEM_IDS:
            selected = index.system(sid, audience="RESEARCH")
            self.assertIsNotNone(selected["card"])
            for item in selected["evidence"]:
                self.assertTrue((ROOT / item["claim"]["origin"]["document"]).is_file())
                self.assertGreaterEqual(item["claim"]["origin"]["line_start"], 1)
                self.assertIn(sid, excerpt(item["claim"]["origin"]))
                for source in item["sources"]:
                    self.assertTrue(source["url"].startswith("https://"))
                    self.assertTrue((ROOT / source["origin"]["document"]).is_file())
                    self.assertGreaterEqual(source["origin"]["line_start"], 1)
                    self.assertIn(source["source_id"], excerpt(source["origin"]))
        coverage = index.system_coverage(as_of=AS_OF)
        self.assertEqual(coverage["research_query_count"], 10)
        self.assertEqual(coverage["gm_eligible_count"], 6)
        print("B1_COVERAGE " + json.dumps(coverage, ensure_ascii=False))

    def test_03_gm_temporal_source_and_non_execution_boundary(self):
        index = knowledge()
        payload = deepcopy(index.payload)
        future = deepcopy(index.claims["R1-P-MOTION_PRE2021"])
        future.update(claim_id="SYNTHETIC_FUTURE_2022", statement="FUTURE_NBA_FINALS_RESULT_SENTINEL",
                      fact_valid_from="2022-06-01", fact_valid_to="2022-06-30",
                      knowledge_available_from="2022-06-30")
        payload["claims"].append(future)
        for cid in ("SYNTHETIC_FUTURE_2022", "R1-C-MOTION_READ_REACT"):
            cards = deepcopy(list(index.system_cards.values()))
            poisoned = next(c for c in cards if c["system_id"] == "MOTION_READ_REACT")
            poisoned["evidence_claim_ids"].append(cid)
            poisoned["advantage_chain"]["first_advantage"] += " FUTURE_NBA_FINALS_RESULT_SENTINEL"
            changed = ResearchIndex(payload, cards)
            selected = changed.system("MOTION_READ_REACT", as_of=AS_OF)
            self.assertIsNone(selected["card"])
            self.assertNotIn("FUTURE_NBA_FINALS_RESULT_SENTINEL", json.dumps(selected))
            self.assertNotIn("FUTURE_NBA_FINALS_RESULT_SENTINEL", json.dumps(changed.search_systems(as_of=AS_OF)))
            self.assertIn("FUTURE_NBA_FINALS_RESULT_SENTINEL", json.dumps(changed.system("MOTION_READ_REACT", audience="RESEARCH")))
        missing = deepcopy(index.claims["R1-P-MOTION_PRE2021"])
        missing.update(source_ids=["LAL-S2"], claim_status="VERIFIED", verification_ref="synthetic assertion")
        with self.assertRaisesRegex(ValueError, "MISSING_SOURCE"):
            index.validate_claim(missing)
        for injection in ({"approved":True}, {"native_intent":{"address":"0x1234","raw_bytes":[1]}}):
            card = deepcopy(index.system_cards["MOTION_READ_REACT"])
            card.update(injection)
            with self.assertRaises(ValueError):
                validate_bpti_knowledge(card, index, audience="RESEARCH")
        not_ready = index.system("ISOLATION_MIDRANGE_CREATION", as_of=AS_OF)
        self.assertIsNone(not_ready["card"])
        self.assertEqual(not_ready["availability"], "NOT_READY")
        self.assertEqual(not_ready["native_support"], "UNKNOWN_NOT_MAPPED_B1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
