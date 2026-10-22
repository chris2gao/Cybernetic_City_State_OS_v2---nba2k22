"""Import only archived R1/R2 reference rows; no web/game queries or certification."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_core.bpti import SYSTEM_IDS, VERSION

RESEARCH = "docs/development_research/"
R1 = RESEARCH + "BPTI_R1_BASKETBALL_SYSTEMS_DEEP_RESEARCH_V1.md"
R2 = RESEARCH + "BPTI_R2_30_FRANCHISE_IDENTITIES_AND_EVOLUTION_DEEP_RESEARCH_V2.md"
REPAIR = RESEARCH + "BPTI_R2_SOURCE_REPAIR_ADDENDUM_V1.md"
R1_REVIEW = "docs/development_reviews/BPTI_R1_DEEP_RESEARCH_REVIEW_V1.md"
FAMILY_SOURCES = (
    ("R1-S02", "R1-S03", "R1-S04"), ("R1-S06", "R1-S07", "R1-S08"),
    ("R1-S09", "R1-S26", "R1-S28"), ("R1-S10", "R1-S11"),
    ("R1-S12", "R1-S13", "R1-S14"), ("R1-S15", "R1-S16"),
    ("R1-S17", "R1-S18"), ("R1-S19", "R1-S20"),
    ("R1-S21", "R1-S22", "R1-S25", "R1-S31"),
    ("R1-S23", "R1-S24", "R1-S30", "R1-S32"),
)


def clean(text):
    return re.sub("\ue200.*?\ue201", "", text).replace("**", "").replace("\u0060", "").strip()


def rows(path):
    for number, line in enumerate((ROOT / path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.startswith("|"):
            yield number, [clean(s) for s in line.strip("|").split("|")]


def locator(path, start, end=None):
    return dict(document=path, line_start=start, line_end=end or start)


def url(text):
    match = re.search(r"https?://[^\s|<>]+", text)
    return match[0].rstrip("；，。") if match else None


def make_source(sid, title, period, published, link, origin):
    return dict(source_id=sid, title=title, historical_period=period,
                publication_date=published, url=link, origin=origin,
                source_status="REFERENCE_INDEXED" if link else "SOURCE_MISSING",
                verification_ref=None)


def claim(cid, domain, statement, ids, origin, **extra):
    # Source links do not certify a whole compound research conclusion or its
    # temporal projection. B1/B3 may extract earlier, finer claims with evidence.
    return dict(claim_id=cid, domain=domain, statement=statement, source_ids=list(ids),
                origin=origin, historical_period="RESEARCH_COMPOUND_SEE_SOURCES",
                fact_valid_from=None, fact_valid_to=None, knowledge_available_from=None,
                retrospective_only=True, claim_status="UNKNOWN",
                evidence_level="RESEARCH_CANDIDATE_NOT_B0_VERIFIED",
                counterevidence=["Compound claim needs claim-level historical time extraction."],
                design_relevance="Reference pointer only; not an operational system/team assessment.",
                verification_ref=None, **extra)


def build():
    sources, claims = {}, []
    for line, cells in rows(R1):
        if re.fullmatch(r"R1-S\d{2}", cells[0]):
            sid, period, title, link = cells
            sources[sid] = make_source(sid, title, period, None, url(link), locator(R1, line))
    # Dates explicitly established by the archived review, not inferred from URL.
    for sid, published in (("R1-S03", "2022-01"), ("R1-S09", "2021-07-08"),
                           ("R1-S10", "2022-02-17"), ("R1-S20", "2022-08")):
        sources[sid]["publication_date"] = published
        sources[sid]["date_evidence_document"] = R1_REVIEW
    starts = {}
    lines = (ROOT / R1).read_text(encoding="utf-8-sig").splitlines()
    for number, line in enumerate(lines, 1):
        match = re.search(r"SystemCard — ([A-Z_]+)", line)
        if match:
            starts[match[1]] = number
    for pos, family in enumerate(SYSTEM_IDS):
        end = (starts[SYSTEM_IDS[pos + 1]] - 1 if pos + 1 < len(SYSTEM_IDS)
               else next(n for n, line in enumerate(lines, 1)
                         if n > starts[family] and line.startswith("## ")) - 1)
        section = lines[starts[family] - 1:end]
        principle = next(clean(line.strip("|").split("|")[1]) for line in section
                         if line.startswith("|") and "核心原则" in line)
        claims.append(claim("R1-C-" + family, "BASKETBALL_PRINCIPLE",
                            principle, FAMILY_SOURCES[pos],
                            locator(R1, starts[family], end), system_id=family))
    for line, cells in rows(R2):
        if len(cells) == 6 and re.fullmatch(r"[A-Z]{3}-S\d+", cells[0]):
            sid, _, title, published, period, _ = cells
            sources[sid] = make_source(sid, title, period, published, url(title), locator(R2, line))
    for line, cells in rows(REPAIR):
        match = re.match(r"([A-Z]{3}-S\d+)", cells[0])
        if not match:
            continue
        sid = match[1]
        prior = sources.get(sid)
        missing = "MISSING_EXACT_SOURCE" in cells[-1]
        repaired = make_source(
            sid, cells[0], prior["historical_period"] if prior else "2021",
            None if missing else (re.search(r"\d{4}-\d{2}-\d{2}", cells[2])[0]
                                  if re.search(r"\d{4}-\d{2}-\d{2}", cells[2]) else "2021-07"),
            None if missing else url(cells[1]), locator(REPAIR, line))
        repaired["repair_status"] = cells[-1]
        repaired["support_scope"] = cells[2]
        repaired["original_origin"] = prior["origin"] if prior else None
        if "PARTIAL_SUPPORT" in cells[-1]:
            repaired["source_status"] = "PARTIAL_SUPPORT"
        sources[sid] = repaired
    for line, cells in rows(R2):
        if not re.fullmatch(r"R2-T-[A-Z]{3}-01", cells[0]):
            continue
        cid, team = cells[:2]
        ids = re.findall(r"[A-Z]{3}-S\d+", cells[-1])
        # R2 writes 'TEAM-S1/S2'; keep the source namespace explicit.
        ids += [team + "-S" + n for n in re.findall(r"/S(\d+)", cells[-1])]
        for sid in ids:
            if sid not in sources:
                sources[sid] = make_source(sid, "SOURCE_MISSING in archived index",
                                           "UNKNOWN", None, None, locator(R2, line))
        c = claim(cid, "FRANCHISE_HISTORICAL_REFERENCE", cells[3], ids,
                  locator(R2, line), team_abbr=team)
        if any(sources[s]["source_status"] == "SOURCE_MISSING" for s in ids):
            c["claim_status"] = "SOURCE_MISSING"
        if team == "ATL":
            c["counterevidence"].append("ATL-S2 supports staffing only, not enduring franchise culture.")
        claims.append(c)
    return dict(schema_version=VERSION, status="B0_REFERENCE_INDEX_NOT_B1_OR_B3_CARDS",
                historical_cutoff="2021-10-19", system_ids=list(SYSTEM_IDS),
                import_policy="ARCHIVED_REFERENCES_NO_NEW_WEB_OR_SOURCE_CERTIFICATION",
                sources=list(sources.values()), claims=claims)


if __name__ == "__main__":
    payload = build()
    destination = ROOT / "web_gm/knowledge/bpti/research_source_index.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(status=payload["status"], sources=len(payload["sources"]),
                          claims=len(payload["claims"]),
                          missing_sources=[s["source_id"] for s in payload["sources"]
                                           if s["source_status"] == "SOURCE_MISSING"])))
