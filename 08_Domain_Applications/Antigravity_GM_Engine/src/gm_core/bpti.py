"""BPTI B0 contracts. Pure reference DTOs; no DB, registry or game access."""
from copy import deepcopy
from datetime import date
import re
from typing import TypedDict, get_origin
from urllib.parse import urlsplit

from .workbench_common import reject_authority, same_source, text_required
from .bpti_package import PackageBQueries

VERSION = "BPTI_KNOWLEDGE_V1"
HISTORICAL_CUTOFF = date(2021, 10, 19)
SYSTEM_IDS = (
    "MOTION_READ_REACT", "TRIANGLE_INSIDE_OUT", "SPREAD_PICK_AND_ROLL",
    "ISOLATION_MIDRANGE_CREATION", "POST_HIGH_LOW", "POINT_CENTER_ELBOW_HUB",
    "TRANSITION_EARLY_OFFENSE", "DEFENSE_FIRST_RIM_PROTECTION",
    "SWITCHABLE_PRESSURE_DEFENSE", "ADAPTIVE_MULTIPLE_SYSTEMS",
)
AGENCY = {"SCRIPTED_ENTRY", "STRUCTURED_READ", "CREATIVE_OPTION", "BAILOUT_RIGHT", "RESET_RIGHT"}
DOMAINS = {
    "BASKETBALL_PRINCIPLE", "FRANCHISE_HISTORICAL_REFERENCE",
    "COACH_HISTORICAL_PHILOSOPHY", "GM_DESIGN_HYPOTHESIS",
    "PROJECT_NATIVE_INTERFACE", "GAME_RUN_OBSERVATION", "UNKNOWN",
}
CLAIM_STATES = {"UNKNOWN", "SOURCE_MISSING", "SUPPORTED_INTERPRETATION", "VERIFIED"}
CHAIN = ("entry_condition", "first_advantage", "defensive_response", "player_read",
         "second_advantage", "counter_response", "fallback")
MAPPING_STATES = {"SUPPORTED_FIELD_DIRECTION", "TYPE_MATCHED_ONLY",
                  "UNKNOWN_NATIVE_BEHAVIOR", "UNSUPPORTED_ACTION"}


class SystemCard(TypedDict):
    schema_version: str
    object_type: str
    system_id: str
    title: str
    evidence_claim_ids: list[str]
    role_requirements: list[str]
    advantage_chain: dict[str, str]
    player_agency: list[str]
    defensive_counter_options: list[str]
    second_answers: list[str]
    known_failure_conditions: list[str]
    roster_budget_tradeoffs: list[str]
    observable_signals: list[str]
    native_binding_refs: list[str]
    status: str


class TeamIdentity(TypedDict):
    schema_version: str
    object_type: str
    identity_id: str
    team_abbr: str
    historical_seed_as_of: str
    evidence_claim_ids: list[str]
    franchise_value_claim_ids: list[str]
    historical_coach_claim_ids: list[str]
    unknown_values: list[str]
    system_candidates: list[str]
    confidence: str
    operational_link: str
    status: str


class NativeBinding(TypedDict):
    schema_version: str
    object_type: str
    binding_id: str
    system_id: str
    evidence_claim_ids: list[str]
    basketball_intent: str
    field_candidates: list[str]
    mapping_status: str
    behavior_effect: str
    unknowns: list[str]
    fallback: str
    status: str


class SystemBlueprint(TypedDict):
    schema_version: str
    object_type: str
    blueprint_id: str
    evidence_claim_ids: list[str]
    identity_ref: str
    primary_system: str
    secondary_systems: list[str]
    source_binding: dict
    team_id: int
    coach_ref: str
    player_role_refs: list[dict]
    first_advantage: str
    opponent_counter: str
    second_answer: str
    native_binding_refs: list[str]
    internal_alternatives: list[str]
    unknowns: list[str]
    status: str


CONTRACTS = {t.__name__: t for t in (SystemCard, TeamIdentity, NativeBinding, SystemBlueprint)}


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("BPTI_EXACT_DATE_REQUIRED")
    return date.fromisoformat(value)


def _texts(value, label, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError("BPTI_TEXT_LIST_REQUIRED:" + label)
    for item in value:
        text_required(item, label)


def _enum(value, allowed, label):
    if value not in allowed:
        raise ValueError("BPTI_INVALID_" + label)


def _no_native_payload(value):
    reject_authority(value)
    if isinstance(value, dict):
        for key, item in value.items():
            if key.casefold() in {
                "raw", "raw_bytes", "address", "offset", "pointer", "preimage",
                "target_value", "object_key", "changes", "sql", "write_instructions",
                "native_intent", "desired", "applied",
            }:
                raise ValueError("BPTI_NO_NATIVE_PAYLOAD:" + key)
            _no_native_payload(item)
    elif isinstance(value, list):
        for item in value:
            _no_native_payload(item)


def _locator(value):
    if not isinstance(value, dict) or set(value) != {"document", "line_start", "line_end"}:
        raise ValueError("BPTI_RESEARCH_LOCATOR_REQUIRED")
    text_required(value["document"], "document")
    if (type(value["line_start"]) is not int or type(value["line_end"]) is not int
            or not 1 <= value["line_start"] <= value["line_end"]):
        raise ValueError("BPTI_RESEARCH_LINE_RANGE_REQUIRED")


def _url(value):
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.hostname)


def publication_upper_bound(value):
    """Keep source precision: '2021' does not mean January 1."""
    if not isinstance(value, str):
        return None
    if re.fullmatch(r"\d{4}", value):
        return date(int(value), 12, 31)
    if re.fullmatch(r"\d{4}-\d{2}", value):
        from calendar import monthrange
        year, month = map(int, value.split("-"))
        return date(year, month, monthrange(year, month)[1])
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return _date(value)
    return None


class ResearchIndex(PackageBQueries):
    """M2 claim/source index. GM is the default, research an explicit mode."""

    def __init__(self, payload, system_cards=None, package=None):
        self.payload = deepcopy(payload)
        _no_native_payload(self.payload)
        if payload.get("schema_version") != VERSION:
            raise ValueError("BPTI_INDEX_VERSION")
        if tuple(payload.get("system_ids", ())) != SYSTEM_IDS:
            raise ValueError("BPTI_FAMILY_REGISTRY_MISMATCH")
        self.sources = self._unique(self.payload["sources"], "source_id")
        self.claims = self._unique(self.payload["claims"], "claim_id")
        for source in self.sources.values():
            _locator(source["origin"])
            _enum(source["source_status"], {"REFERENCE_INDEXED", "PARTIAL_SUPPORT", "SOURCE_MISSING", "VERIFIED"}, "SOURCE_STATUS")
            if source["source_status"] == "SOURCE_MISSING":
                if source["url"] is not None:
                    raise ValueError("BPTI_MISSING_SOURCE_MUST_NOT_SUBSTITUTE_URL")
            elif not _url(source["url"]):
                raise ValueError("BPTI_PERMANENT_SOURCE_URL_REQUIRED")
            if source["source_status"] == "VERIFIED" and not source.get("verification_ref"):
                raise ValueError("BPTI_SOURCE_VERIFICATION_REFERENCE_REQUIRED")
        for claim in self.claims.values():
            self.validate_claim(claim)
        self._install_package(package)
        self.system_cards = self._unique(system_cards or [], "system_id")
        if system_cards is not None and set(self.system_cards) != set(SYSTEM_IDS):
            raise ValueError("BPTI_SYSTEM_CARD_COVERAGE_REQUIRED")
        for card in self.system_cards.values():
            validate_bpti_knowledge(card, self, audience="RESEARCH")
            if card["object_type"] != "SystemCard" or set(card["native_binding_refs"]) - self.native_bindings.keys():
                raise ValueError("BPTI_UNREGISTERED_NATIVE_BINDING")

    @staticmethod
    def _unique(rows, key):
        result = {r[key]: r for r in rows}
        if len(result) != len(rows):
            raise ValueError("BPTI_DUPLICATE_ID:" + key)
        return result

    def validate_claim(self, claim):
        reject_authority(claim)
        text_required(claim["statement"], "statement")
        _locator(claim["origin"])
        _enum(claim["domain"], DOMAINS, "CLAIM_DOMAIN")
        _enum(claim["claim_status"], CLAIM_STATES, "CLAIM_STATUS")
        _texts(claim["source_ids"], "source_ids", True)
        if set(claim["source_ids"]) - self.sources.keys():
            raise ValueError("BPTI_SOURCE_ID_NOT_REGISTERED")
        if claim.get("system_id") is not None:
            _enum(claim["system_id"], SYSTEM_IDS, "SYSTEM_ID")
        for key in ("fact_valid_from", "fact_valid_to", "knowledge_available_from"):
            if claim[key] is not None:
                _date(claim[key])
        if claim["fact_valid_from"] and claim["fact_valid_to"]:
            if _date(claim["fact_valid_from"]) > _date(claim["fact_valid_to"]):
                raise ValueError("BPTI_FACT_PERIOD_REVERSED")
        if type(claim["retrospective_only"]) is not bool:
            raise ValueError("BPTI_RETROSPECTIVE_FLAG_REQUIRED")
        missing = any(self.sources[s]["source_status"] == "SOURCE_MISSING" for s in claim["source_ids"])
        if missing and claim["claim_status"] not in {"UNKNOWN", "SOURCE_MISSING"}:
            raise ValueError("BPTI_MISSING_SOURCE_CANNOT_SUPPORT_CLAIM")
        if claim["claim_status"] == "VERIFIED":
            if (not claim.get("verification_ref") or
                    any(self.sources[s]["source_status"] != "VERIFIED" for s in claim["source_ids"])):
                raise ValueError("BPTI_VERIFIED_REQUIRES_RELIABLE_REVIEWED_SOURCES")
        return deepcopy(claim)

    def availability(self, claim, *, as_of):
        cutoff = min(_date(as_of), HISTORICAL_CUTOFF)
        if claim["domain"] == "GAME_RUN_OBSERVATION":
            return "CURRENT_GAME_STATE_REQUIRES_M3_SOURCE"
        if claim["claim_status"] in {"UNKNOWN", "SOURCE_MISSING"}:
            return claim["claim_status"]
        if claim["domain"] == "PROJECT_NATIVE_INTERFACE":
            return "AVAILABLE_PROJECT_REFERENCE_NOT_BASKETBALL_EFFECT"
        times = [claim[k] for k in ("fact_valid_from", "fact_valid_to", "knowledge_available_from")]
        if any(t is None for t in times):
            return "UNKNOWN_TIME_BOUNDARY"
        if any(_date(t) > cutoff for t in times):
            return "FUTURE_OR_HIDDEN"
        # Later publication may support earlier events only after explicit
        # claim-level extraction. Its whole retrospective text is never passed.
        for sid in claim["source_ids"]:
            published = self.sources[sid]["publication_date"]
            if published is None:
                if not claim["retrospective_only"]:
                    return "UNKNOWN_PUBLICATION_DATE"
            else:
                latest = publication_upper_bound(published)
                if latest is None:
                    return "UNKNOWN_PUBLICATION_DATE"
                if latest > cutoff and not claim["retrospective_only"]:
                    return "RETROSPECTIVE_EXTRACTION_REQUIRED"
        return "AVAILABLE_AS_OF_CUTOFF"

    def claim(self, claim_id, *, as_of=None, audience="GM"):
        _enum(audience, {"GM", "RESEARCH"}, "AUDIENCE")
        claim = self.claims[claim_id]
        if audience == "RESEARCH":
            return dict(availability="RESEARCH_ONLY", claim=deepcopy(claim))
        availability = self.availability(claim, as_of=as_of)
        return dict(claim_id=claim_id, availability=availability,
                    claim=deepcopy(claim) if availability.startswith("AVAILABLE_") else None)

    def source(self, source_id, *, as_of=None, audience="GM"):
        _enum(audience, {"GM", "RESEARCH"}, "AUDIENCE")
        source = self.sources[source_id]
        if audience == "RESEARCH":
            return dict(availability="RESEARCH_ONLY", source=deepcopy(source))
        _date(as_of)
        # Source titles/URLs can disclose future outcomes. GM sees only the
        # approved temporal projection of a claim; source browsing is research.
        return dict(source_id=source_id, availability="RESEARCH_LOCATOR_ONLY_USE_FILTERED_CLAIM",
                    source=None)

    def reference_evidence(self, claim_ids, *, as_of):
        """Opt-in M3 reference_evidence projection, not a decision/native plan."""
        _date(as_of)
        result = {}
        for cid in claim_ids:
            selected = self.claim(cid, as_of=as_of)
            ref = "bpti-claim:" + cid
            result[ref] = dict(ref_id=ref, kind="KNOWLEDGE", version=VERSION,
                               availability=selected["availability"], value=selected["claim"])
        return result

    def system(self, system_id, *, as_of=None, audience="GM"):
        """One complete card, or a text-free HOLD if any supporting claim is hidden."""
        _enum(audience, {"GM", "RESEARCH"}, "AUDIENCE")
        _enum(system_id, SYSTEM_IDS, "SYSTEM_ID")
        card = self.system_cards[system_id]
        blocked = []
        if audience == "GM":
            _date(as_of)
            blocked = [dict(claim_id=cid, availability=self.availability(self.claims[cid], as_of=as_of))
                       for cid in card["evidence_claim_ids"]
                       if not self.availability(self.claims[cid], as_of=as_of).startswith("AVAILABLE_")]
        result = dict(system_id=system_id, audience=audience,
                      availability="NOT_READY" if blocked else "RESEARCH_ONLY" if audience == "RESEARCH" else "GM_ELIGIBLE_REFERENCE",
                      native_support="UNKNOWN_NOT_MAPPED_B1", card=None, evidence=[], blocked_claims=blocked)
        if self.package:
            result["native_support"] = "REFERENCE_BINDINGS_NOT_NATIVE_EFFECT_PROOF"
            result["native_binding_refs"] = [bid for bid, b in self.native_bindings.items() if b["system_id"] == system_id]
            result["mechanism_entries"] = self._mechanism_entries(system_id, as_of=as_of, audience=audience)
            if blocked and result["mechanism_entries"]:
                result["availability"] = "GM_ELIGIBLE_MECHANISM_ONLY"
        if blocked:
            return result
        # Validate the whole DTO before returning any narrative/list field.
        result["card"] = validate_bpti_knowledge(card, self, as_of=as_of, audience=audience)
        for cid in card["evidence_claim_ids"]:
            claim = self.claim(cid, as_of=as_of, audience=audience)["claim"]
            sources = []
            for sid in claim["source_ids"]:
                source = self.sources[sid]
                if audience == "RESEARCH":
                    sources.append(deepcopy(source))
                else:
                    # Follow B0: retrospective page titles/URLs are research
                    # metadata and may disclose future results. Keep locators.
                    sources.append(dict(source_id=sid, origin=deepcopy(source["origin"])))
            result["evidence"].append(dict(claim=claim, sources=sources))
        return result

    def system_coverage(self, *, as_of):
        _date(as_of)
        eligible = [sid for sid in self.system_cards
                    if self.system(sid, as_of=as_of)["card"] is not None
                    or self.system(sid, as_of=as_of).get("mechanism_entries")]
        return dict(created_count=len(self.system_cards), research_query_count=len(self.system_cards),
                    gm_eligible_count=len(eligible), gm_eligible_ids=eligible,
                    full_card_count=sum(self.system(sid, as_of=as_of)["card"] is not None for sid in self.system_cards),
                    coverage_scope="FULL_CARD_OR_NARROW_MECHANISM_ENTRY",
                    research_only_ids=[sid for sid in self.system_cards if sid not in eligible],
                    as_of=as_of, historical_cutoff=HISTORICAL_CUTOFF.isoformat(),
                    meaning="REFERENCE_ELIGIBILITY_NOT_TEAM_ASSESSMENT_OR_NATIVE_SUPPORT")

    def search_systems(self, *, system_id=None, role=None, counter=None,
                       limit=5, as_of=None, audience="GM"):
        """Bounded summaries only; filter the GM projection before text matching."""
        _enum(audience, {"GM", "RESEARCH"}, "AUDIENCE")
        if type(limit) is not int or not 1 <= limit <= 5:
            raise ValueError("BPTI_SYSTEM_LIMIT_1_TO_5")
        if system_id is not None:
            _enum(system_id, SYSTEM_IDS, "SYSTEM_ID")
        if audience == "GM":
            _date(as_of)
        rows = []
        for sid in self.system_cards:
            if system_id and sid != system_id:
                continue
            projected = self.system(sid, as_of=as_of, audience=audience)
            card = projected["card"]
            if card is None:
                if projected.get("mechanism_entries") and not role and not counter:
                    rows.append(dict(system_id=sid, availability=projected["availability"],
                                     evidence_claim_ids=[v["claim"]["claim_id"] for v in projected["mechanism_entries"]],
                                     native_support=projected["native_support"]))
                continue
            if role and not any(role.casefold() in text.casefold() for text in card["role_requirements"]):
                continue
            if counter and not any(counter.casefold() in text.casefold() for text in card["defensive_counter_options"]):
                continue
            rows.append(dict(system_id=sid, title=card["title"], availability=projected["availability"],
                             roles=[r.split(":", 1)[0] for r in card["role_requirements"]],
                             counters=[r.split(":", 1)[0] for r in card["defensive_counter_options"]],
                             evidence_claim_ids=deepcopy(card["evidence_claim_ids"]),
                             native_support="UNKNOWN_NOT_MAPPED_B1"))
        return dict(total_matches=len(rows), returned_count=min(limit, len(rows)),
                    truncated=len(rows) > limit, systems=rows[:limit],
                    coverage=self.system_coverage(as_of=as_of) if as_of else None)


def validate_bpti_knowledge(obj, index, *, as_of=None, audience="GM", analysis=None):
    """Validate one exact DTO. Blueprint generation/D1-D6 insertion is B4."""
    _enum(audience, {"GM", "RESEARCH"}, "AUDIENCE")
    _no_native_payload(obj)
    if not isinstance(obj, dict):
        raise ValueError("BPTI_OBJECT_REQUIRED")
    kind = obj.get("object_type")
    if kind not in CONTRACTS or set(obj) != set(CONTRACTS[kind].__annotations__):
        raise ValueError("BPTI_EXACT_OBJECT_CONTRACT_REQUIRED")
    for key, annotation in CONTRACTS[kind].__annotations__.items():
        expected = get_origin(annotation) or annotation
        if not isinstance(obj[key], expected) or (expected is int and type(obj[key]) is not int):
            raise ValueError("BPTI_FIELD_TYPE_REQUIRED:" + key)
    if obj["schema_version"] != VERSION:
        raise ValueError("BPTI_OBJECT_VERSION")
    _texts(obj["evidence_claim_ids"], "evidence_claim_ids", True)
    refs = list(obj["evidence_claim_ids"])
    if kind == "TeamIdentity":
        for key in ("franchise_value_claim_ids", "historical_coach_claim_ids"):
            _texts(obj[key], key)
            refs.extend(obj[key])
    for cid in refs:
        if cid not in index.claims:
            raise ValueError("BPTI_CLAIM_ID_NOT_REGISTERED:" + cid)
        if audience == "GM" and not index.availability(index.claims[cid], as_of=as_of).startswith("AVAILABLE_"):
            raise ValueError("BPTI_CLAIM_NOT_AVAILABLE_TO_GM:" + cid)
    if audience == "GM":
        _date(as_of)
    for key in ("system_id", "primary_system"):
        if key in obj:
            _enum(obj[key], SYSTEM_IDS, "SYSTEM_ID")
    for key in ("system_candidates", "secondary_systems"):
        if key in obj:
            _texts(obj[key], key)
            for value in obj[key]:
                _enum(value, SYSTEM_IDS, "SYSTEM_ID")
    if "native_binding_refs" in obj:
        _texts(obj["native_binding_refs"], "native_binding_refs")
    if kind == "SystemCard":
        _enum(obj["status"], {"REFERENCE_ONLY"}, "STATUS")
        text_required(obj["title"], "title")
        for key in ("role_requirements", "player_agency", "defensive_counter_options",
                    "second_answers", "known_failure_conditions", "roster_budget_tradeoffs", "observable_signals"):
            _texts(obj[key], key, True)
        if set(obj["advantage_chain"]) != set(CHAIN):
            raise ValueError("BPTI_COMPLETE_ADVANTAGE_CHAIN_REQUIRED")
        for value in obj["advantage_chain"].values():
            text_required(value, "advantage_chain")
        for value in obj["player_agency"]:
            _enum(value, AGENCY, "AGENCY")
    elif kind == "TeamIdentity":
        _enum(obj["status"], {"HISTORICAL_SEED_ONLY"}, "STATUS")
        _enum(obj["confidence"], {"HISTORICAL_SEED_ONLY", "UNKNOWN"}, "CONFIDENCE")
        _enum(obj["operational_link"], {"NOT_BOUND_TO_ANY_SAVE"}, "OPERATIONAL_LINK")
        text_required(obj["identity_id"], "identity_id")
        if not re.fullmatch(r"[A-Z]{3}", obj["team_abbr"]):
            raise ValueError("BPTI_TEAM_ABBR_REQUIRED")
        if _date(obj["historical_seed_as_of"]) > HISTORICAL_CUTOFF:
            raise ValueError("BPTI_SEED_AFTER_HISTORICAL_CUTOFF")
        _texts(obj["unknown_values"], "unknown_values")
    elif kind == "NativeBinding":
        _enum(obj["status"], {"REFERENCE_ONLY"}, "STATUS")
        _enum(obj["mapping_status"], MAPPING_STATES, "MAPPING_STATUS")
        _enum(obj["behavior_effect"], {"UNKNOWN", "HYPOTHESIS_NOT_GUARANTEED"}, "EFFECT")
        _enum(obj["fallback"], {"HOLD_RESEARCH"}, "FALLBACK")
        text_required(obj["binding_id"], "binding_id")
        text_required(obj["basketball_intent"], "basketball_intent")
        _texts(obj["field_candidates"], "field_candidates")
        _texts(obj["unknowns"], "unknowns", True)
        if obj["mapping_status"] in {"SUPPORTED_FIELD_DIRECTION", "TYPE_MATCHED_ONLY"}:
            if not obj["field_candidates"] or not any(
                index.claims[c]["domain"] == "PROJECT_NATIVE_INTERFACE"
                and index.claims[c]["claim_status"] == "VERIFIED" for c in refs
            ):
                raise ValueError("BPTI_NATIVE_SUPPORT_NEEDS_PROJECT_INTERFACE_EVIDENCE")
    else:
        _enum(obj["status"], {"DRAFT_UNAPPROVED"}, "STATUS")
        for key in ("blueprint_id", "identity_ref", "coach_ref", "first_advantage", "opponent_counter", "second_answer"):
            text_required(obj[key], key)
        if obj["internal_alternatives"] != ["HOLD", "INTERNAL", "MARKET"]:
            raise ValueError("BPTI_PRESERVE_M3_INTERNAL_FIRST")
        _texts(obj["unknowns"], "unknowns")
        if not isinstance(obj["player_role_refs"], list):
            raise ValueError("BPTI_ROLE_LIST_REQUIRED")
        for role in obj["player_role_refs"]:
            if not isinstance(role, dict) or set(role) != {"player_ref", "roles", "agency"}:
                raise ValueError("BPTI_ROLE_REFERENCE_CONTRACT")
            text_required(role["player_ref"], "player_ref")
            _texts(role["roles"], "roles", True)
            _texts(role["agency"], "agency", True)
            for value in role["agency"]:
                _enum(value, AGENCY, "AGENCY")
        if audience == "GM":
            _validate_m3_binding(obj, analysis)
    return deepcopy(obj)


def _validate_m3_binding(obj, analysis):
    from .analysis_packet import require_gm_packet, team, evidence
    if analysis is None:
        raise ValueError("BPTI_BLUEPRINT_NEEDS_EXISTING_M3_PACKET")
    require_gm_packet(analysis)
    if not same_source(obj["source_binding"], analysis["source_binding"]) or any(
        obj["source_binding"].get(k) != analysis["source_binding"].get(k)
        for k in ("save_id", "save_instance_id", "generation_id")
    ):
        raise ValueError("BPTI_M3_SOURCE_MISMATCH")
    if type(obj["team_id"]) is not int:
        raise ValueError("BPTI_TEAM_ID_REQUIRED")
    selected_team = team(analysis, obj["team_id"])
    supplied = {"player:" + p for p in selected_team["player_supply"]["source_identity_set"]}
    for role in obj["player_role_refs"]:
        if role["player_ref"] not in supplied:
            raise ValueError("BPTI_ROLE_NOT_IN_SAME_TEAM_PACKET")
    coach_key = selected_team.get("tactical_context", {}).get("coach_object_key")
    if not coach_key or obj["coach_ref"] != "native-object:" + coach_key:
        raise ValueError("BPTI_COACH_NOT_IN_SAME_TEAM_PACKET")
    evidence(analysis, obj["coach_ref"])
