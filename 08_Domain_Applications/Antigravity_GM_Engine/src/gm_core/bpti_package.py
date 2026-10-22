"""B2/B3 reference queries. No database, registry, native intent or executor access."""
from copy import deepcopy


LAYERS = ("FRANCHISE_IDENTITY", "COACH_PHILOSOPHY", "BASKETBALL_SYSTEM",
          "PLAYER_ROLE_AND_AGENCY", "MATCHUP_GAMEPLAN")


class PackageBQueries:
    def _install_package(self, package):
        from .bpti import VERSION, SYSTEM_IDS, validate_bpti_knowledge, _no_native_payload
        self.package = deepcopy(package or {})
        _no_native_payload(self.package)
        self.native_bindings = {}
        self.team_identities = {}
        self.mechanism_claims = {}
        if not package:
            return
        if package.get("schema_version") != VERSION or package.get("version") != "BPTI_PACKAGE_B_V1":
            raise ValueError("BPTI_PACKAGE_VERSION")
        self.native_bindings = self._unique(package["bindings"], "binding_id")
        self.team_identities = self._unique(package["identities"], "team_abbr")
        if len(self.team_identities) != 30 or len({v['identity_id'] for v in self.team_identities.values()}) != 30:
            raise ValueError("BPTI_THIRTY_UNIQUE_HISTORICAL_IDENTITIES_REQUIRED")
        allowed = set(package["supported_field_keys"])
        for binding in self.native_bindings.values():
            validate_bpti_knowledge(binding, self, audience="RESEARCH")
            if binding["mapping_status"] == "SUPPORTED_FIELD_DIRECTION" and set(binding["field_candidates"]) - allowed:
                raise ValueError("BPTI_UNSUPPORTED_FIELD_DIRECTION")
            if binding["mapping_status"] == "TYPE_MATCHED_ONLY" and not any(
                self.claims[c].get("evidence_level") in
                {"NATIVE_TYPE_MEMBERSHIP_VERIFIED", "PLAYER_REPORTED_TYPE_MEMBERSHIP"}
                for c in binding["evidence_claim_ids"]
            ):
                raise ValueError("BPTI_TYPE_MATCH_REQUIRES_MEMBERSHIP_EVIDENCE")
        for abbr, identity in self.team_identities.items():
            validate_bpti_knowledge(identity, self, audience="RESEARCH")
            layers = package["identity_layers"][abbr]
            if set(layers) != set(LAYERS):
                raise ValueError("BPTI_FIVE_IDENTITY_LAYERS_REQUIRED")
            for layer, refs in layers.items():
                if not refs or any(c not in self.claims or self.claims[c].get('identity_layer') != layer for c in refs):
                    raise ValueError("BPTI_IDENTITY_LAYER_EVIDENCE_REQUIRED")
        for system_id, refs in package["mechanism_claims"].items():
            if system_id not in SYSTEM_IDS or not refs or any(c not in self.claims for c in refs):
                raise ValueError("BPTI_MECHANISM_REFERENCE_REQUIRED")
        self.mechanism_claims = deepcopy(package["mechanism_claims"])

    @staticmethod
    def _page(rows, limit, offset):
        if type(limit) is not int or not 1 <= limit <= 5 or type(offset) is not int or offset < 0:
            raise ValueError("BPTI_PAGE_LIMIT_1_TO_5_NONNEGATIVE_OFFSET")
        end = offset + limit
        return dict(total_matches=len(rows), returned_count=len(rows[offset:end]),
                    truncated=end < len(rows), next_offset=end if end < len(rows) else None,
                    items=rows[offset:end], authority="REFERENCE_ONLY_NO_NATIVE_PLAN_OR_APPROVAL")

    def _mechanism_entries(self, system_id, *, as_of, audience):
        rows = []
        for cid in self.mechanism_claims.get(system_id, []):
            view = self.claim(cid, as_of=as_of, audience=audience)
            if view["claim"] is not None:
                rows.append(view)
        return rows

    def binding(self, binding_id, *, as_of=None, audience="GM"):
        from .bpti import validate_bpti_knowledge
        value = self.native_bindings[binding_id]
        if audience == "GM":
            family = self.system(value["system_id"], as_of=as_of)
            if family["card"] is None and not family.get("mechanism_entries"):
                return dict(binding_id=binding_id, availability="HOLD_SYSTEM_EVIDENCE", binding=None)
        dto = validate_bpti_knowledge(value, self, as_of=as_of, audience=audience)
        return dict(binding_id=binding_id, availability="REFERENCE_ONLY", binding=dto,
                    evidence=[self.claim(c, as_of=as_of, audience=audience) for c in dto["evidence_claim_ids"]],
                    next_step="M3_SAME_BATCH_GM_SANITIZED_REQUIRED_NO_ACTION_GENERATED")

    def search_bindings(self, *, system_id=None, field=None, mapping_status=None,
                        limit=5, offset=0, as_of=None, audience="GM"):
        from .bpti import SYSTEM_IDS, MAPPING_STATES, _enum, _date
        _enum(audience, {"GM", "RESEARCH"}, "AUDIENCE")
        if audience == "GM":
            _date(as_of)
        if system_id is not None:
            _enum(system_id, SYSTEM_IDS, "SYSTEM_ID")
        if mapping_status is not None:
            _enum(mapping_status, MAPPING_STATES, "MAPPING_STATUS")
        rows = []
        for bid, b in self.native_bindings.items():
            if system_id and b["system_id"] != system_id:
                continue
            if mapping_status and b["mapping_status"] != mapping_status:
                continue
            if field and not any(field.casefold() in f.casefold() for f in b["field_candidates"]):
                continue
            view = self.binding(bid, as_of=as_of, audience=audience)
            if view["binding"] is not None:
                rows.append(dict(binding_id=bid, system_id=b["system_id"],
                                 mapping_status=b["mapping_status"], basketball_intent=b["basketball_intent"],
                                 evidence_claim_ids=deepcopy(b["evidence_claim_ids"])))
        return self._page(rows, limit, offset)

    def team_identity(self, team, *, as_of=None, audience="GM"):
        from .bpti import _enum, _date, validate_bpti_knowledge
        _enum(audience, {"GM", "RESEARCH"}, "AUDIENCE")
        if audience == "GM":
            _date(as_of)
        abbr = team.upper()
        original = self.team_identities[abbr]
        dto = deepcopy(original)
        layers, blocked, available = {}, [], set()
        for layer, refs in self.package["identity_layers"][abbr].items():
            views = [self.claim(c, as_of=as_of, audience=audience) for c in refs]
            layers[layer] = [v for v in views if v["claim"] is not None]
            available.update(c for c, v in zip(refs, views) if v["claim"] is not None)
            blocked.extend(dict(claim_id=c, availability=v["availability"])
                           for c, v in zip(refs, views) if v["claim"] is None)
        if audience == "GM":
            for key in ("evidence_claim_ids", "franchise_value_claim_ids", "historical_coach_claim_ids"):
                dto[key] = [c for c in dto[key] if c in available]
            if not layers["BASKETBALL_SYSTEM"]:
                dto["system_candidates"] = []
            dto["unknown_values"] += [b['claim_id'] + ':' + b['availability'] for b in blocked]
        # The stored seed is always validated. An entirely hidden seed remains text-free.
        if dto["evidence_claim_ids"]:
            dto = validate_bpti_knowledge(dto, self, as_of=as_of, audience=audience)
        else:
            dto = None
        return dict(team_abbr=abbr, identity_id=original['identity_id'], identity=dto, layers=layers,
                    blocked_claims=blocked, status="HISTORICAL_SEED_ONLY",
                    operational_link="NOT_BOUND_TO_ANY_SAVE", actual_team_assessment="UNASSESSED",
                    strategy_reference_slot="TEAM_STRATEGY_STATE_V1.identity_reference",
                    source_requirement="FUTURE_M3_SAME_BATCH_GM_SANITIZED")

    def search_identities(self, *, team=None, system_id=None, limit=5, offset=0,
                          as_of=None, audience="GM"):
        from .bpti import SYSTEM_IDS, _enum, _date
        _enum(audience, {"GM", "RESEARCH"}, "AUDIENCE")
        if audience == "GM":
            _date(as_of)
        if system_id is not None:
            _enum(system_id, SYSTEM_IDS, "SYSTEM_ID")
        rows = []
        for abbr in self.team_identities:
            if team and abbr != team.upper():
                continue
            view = self.team_identity(abbr, as_of=as_of, audience=audience)
            dto = view["identity"]
            if system_id and (dto is None or system_id not in dto["system_candidates"]):
                continue
            rows.append(dict(team_abbr=abbr, identity_id=view["identity_id"], status=view["status"],
                             operational_link=view['operational_link'],
                             system_candidates=dto["system_candidates"] if dto else [],
                             availability="HISTORICAL_REFERENCE" if dto else "HOLD_EVIDENCE"))
        return self._page(rows, limit, offset)

    def context(self, system_id, *, team=None, limit=5, offset=0, as_of=None, audience="GM"):
        """Bounded B2+B3 join; later B4 may opt in without changing this reference layer."""
        return dict(system=self.system(system_id, as_of=as_of, audience=audience),
                    bindings=self.search_bindings(system_id=system_id, limit=limit, offset=offset,
                                                  as_of=as_of, audience=audience),
                    identity=self.team_identity(team, as_of=as_of, audience=audience) if team else None,
                    authority="REFERENCE_ONLY_NO_NATIVE_PLAN_OR_APPROVAL")
