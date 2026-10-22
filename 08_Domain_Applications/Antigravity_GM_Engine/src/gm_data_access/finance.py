"""Observed encodings are not certified financial purchasing power."""

FINANCE = {
    "total_salary": ("0xCBC", "uint32", "USD_AS_CAPTURED", "CURRENT_TEAM_TOTAL_LABEL; aggregation not independently reconciled"),
    "payroll": ("0xFF4", "uint32", "UNKNOWN", "PAYROLL_LABEL_ONLY; payment period and aggregation UNKNOWN"),
    "budget": ("0x1014", "uint32", "USD_AS_CAPTURED", "OPERATING_BUDGET_LABEL; replenishment period UNKNOWN"),
    "staff_budget": ("0x1018", "uint32", "USD_AS_CAPTURED", "STAFF_BUDGET_LABEL; replenishment period UNKNOWN"),
    "cash": ("0x1010", "uint32", "UNKNOWN", "SIGNEDNESS_AND_UI_MEANING_UNVERIFIED; preserve raw uint32"),
    "monthly_gate_revenue": ("0xFD8", "uint32", "USD_AS_CAPTURED", "TIME_WINDOW_UNKNOWN; column name does not prove monthly revenue"),
    "merch_revenue": ("0xFDC", "uint32", "USD_AS_CAPTURED", "TIME_WINDOW_UNKNOWN"),
    "media_revenue": ("0xFE4", "uint32", "USD_AS_CAPTURED", "TIME_WINDOW_UNKNOWN"),
    "salary_current_year": ("player profile contract_year_1", "31-bit masked unsigned", "USD", "CURRENT_CONTRACT_SLOT; offseason transition not certified"),
    "contract_year_1..6": ("config/memory_field_profile.json", "31-bit masked unsigned", "USD", "SIX_OBSERVED_SALARY_SLOTS; not certified future cap commitments"),
    "staff_salary": ("staff profile vitals.salary", "native field profile", "USD_AS_CAPTURED", "STAFF_SALARY_LABEL; payment period UNKNOWN"),
}


def semantics():
    return [dict(field=k, offset=v[0], encoding=v[1], unit=v[2], time_scope=v[3],
                 evidence="OBSERVED_RAW_SEMANTICS_PARTIAL", financial_eligibility="UNKNOWN",
                 usable_as_signing_capacity=False,
                 evidence_file="src/auto_pipeline_ingest.py; config/memory_field_profile.json")
            for k, v in FINANCE.items()]
