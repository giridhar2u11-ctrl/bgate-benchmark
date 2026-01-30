from __future__ import annotations
import numpy as np
import pandas as pd

DOMAINS = [
    "nonprofit_donations",
    "supply_chain_provenance",
    "health_record_access",
    "academic_credentials",
    "interbank_settlement",
    "iot_device_integrity",
]

GOV_MODELS = ["single_operator", "consortium_bft", "permissionless_pos", "permissioned_raft"]

def _clip_int(x: float, lo: int, hi: int) -> int:
    return int(max(lo, min(hi, round(x))))

def generate_scenarios(n: int = 30, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    rows = []
    for i in range(1, n + 1):
        domain = rng.choice(DOMAINS)
        gov_model = rng.choice(GOV_MODELS)

        stakeholders = _clip_int(rng.normal(10, 4), 3, 30)
        trust_asymmetry = _clip_int(rng.normal(3, 1), 1, 5)
        data_sensitivity = _clip_int(rng.normal(3, 1.2), 1, 5)
        dispute_freq = max(0, rng.poisson(3))
        regulatory_pressure = _clip_int(rng.normal(3, 1.1), 1, 5)

        incident_response = int(rng.random() < 0.65)
        upgrade_policy = int(rng.random() < 0.60)
        dispute_process = int(rng.random() < 0.70)
        decision_rights_clarity = _clip_int(rng.normal(1.2, 0.6), 0, 2)

        key_mgmt_maturity = _clip_int(rng.normal(3, 1.1), 1, 5)
        observability_level = _clip_int(rng.normal(3, 1.0), 1, 5)
        data_gov_maturity = _clip_int(rng.normal(3, 1.0), 1, 5)
        change_readiness = _clip_int(rng.normal(3, 1.0), 1, 5)

        cost_baseline = float(_clip_int(rng.normal(120, 40), 40, 300))
        cost_blockchain = float(_clip_int(cost_baseline * rng.uniform(0.8, 1.4), 30, 450))

        time_baseline = float(_clip_int(rng.normal(100, 30), 30, 250))
        time_blockchain = float(_clip_int(time_baseline * rng.uniform(0.7, 1.2), 20, 350))

        adoption_stage = rng.choice(["idea", "pilot", "production"], p=[0.45, 0.40, 0.15])

        rows.append({
            "scenario_id": f"S{i:03d}",
            "domain": domain,
            "governance_model": gov_model,
            "stakeholders_count": stakeholders,
            "trust_asymmetry_level": trust_asymmetry,
            "data_sensitivity": data_sensitivity,
            "dispute_frequency_per_month": dispute_freq,
            "regulatory_pressure": regulatory_pressure,
            "incident_response_present": incident_response,
            "upgrade_policy_present": upgrade_policy,
            "dispute_process_present": dispute_process,
            "decision_rights_clarity": decision_rights_clarity,
            "key_management_maturity": key_mgmt_maturity,
            "observability_level": observability_level,
            "data_governance_maturity": data_gov_maturity,
            "change_readiness": change_readiness,
            "cost_baseline": cost_baseline,
            "cost_blockchain_est": cost_blockchain,
            "time_baseline": time_baseline,
            "time_blockchain_est": time_blockchain,
            "adoption_stage": adoption_stage,
        })

    return pd.DataFrame(rows)
