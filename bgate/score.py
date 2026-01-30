from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, Any, Tuple

import pandas as pd
import yaml

@dataclass
class ScoreResult:
    scenario_id: str
    ARS: float
    GQS: float
    TSS: float
    bgate_index: float
    penalty_points: float
    rating: str
    penalty_reasons: str

def load_rubric(path: str = "rubric/bgate_rubric.yaml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _scale_1_5_to_0_100(x: float) -> float:
    return max(0.0, min(100.0, (x - 1.0) / 4.0 * 100.0))

def _binary_to_0_100(x: int) -> float:
    return 100.0 if int(x) == 1 else 0.0

def _clarity_to_0_100(x: int) -> float:
    # 0 unclear, 1 partial, 2 clear
    if x <= 0:
        return 0.0
    if x == 1:
        return 50.0
    return 100.0

def _economic_score(cost_baseline: float, cost_blockchain: float, time_baseline: float, time_blockchain: float) -> float:
    # Simple: reward reductions, penalize increases. Clamp.
    cost_ratio = cost_blockchain / max(1.0, cost_baseline)
    time_ratio = time_blockchain / max(1.0, time_baseline)

    # Ratios < 1 are good. Map around 1.
    cost_component = max(0.0, min(100.0, (1.3 - cost_ratio) / 0.8 * 100.0))
    time_component = max(0.0, min(100.0, (1.2 - time_ratio) / 0.7 * 100.0))
    return 0.6 * cost_component + 0.4 * time_component

def _use_case_fit(stakeholders: int, trust_asym: int, dispute_freq: int, data_sens: int) -> float:
    # High stakeholders + high trust asymmetry + disputes + high sensitivity -> stronger fit for shared ledger + governance.
    score = (
        min(30.0, stakeholders) / 30.0 * 30.0 +
        _scale_1_5_to_0_100(trust_asym) * 0.25 +
        min(10.0, dispute_freq) / 10.0 * 25.0 +
        _scale_1_5_to_0_100(data_sens) * 0.20
    )
    return max(0.0, min(100.0, score))

def score_one(row: pd.Series, rubric: Dict[str, Any]) -> ScoreResult:
    # --- ARS components ---
    use_case_fit = _use_case_fit(
        stakeholders=int(row["stakeholders_count"]),
        trust_asym=int(row["trust_asymmetry_level"]),
        dispute_freq=int(row["dispute_frequency_per_month"]),
        data_sens=int(row["data_sensitivity"]),
    )
    org_capability = (
        0.55 * _scale_1_5_to_0_100(float(row["data_governance_maturity"])) +
        0.45 * _scale_1_5_to_0_100(float(row["change_readiness"]))
    )
    economic_viability = _economic_score(
        float(row["cost_baseline"]), float(row["cost_blockchain_est"]),
        float(row["time_baseline"]), float(row["time_blockchain_est"])
    )
    stakeholder_alignment = (
        0.5 * (100.0 - _scale_1_5_to_0_100(float(row["trust_asymmetry_level"]))) +  # lower asymmetry is easier
        0.5 * (100.0 - min(10.0, float(row["dispute_frequency_per_month"])) / 10.0 * 100.0)
    )

    ars_w = rubric["scores"]["ARS"]["dimensions"]
    ARS = (
        ars_w["use_case_fit"]["weight"] * use_case_fit +
        ars_w["org_capability"]["weight"] * org_capability +
        ars_w["economic_viability"]["weight"] * economic_viability +
        ars_w["stakeholder_alignment"]["weight"] * stakeholder_alignment
    )

    # --- GQS components ---
    decision_rights = _clarity_to_0_100(int(row["decision_rights_clarity"]))
    dispute_resolution = _binary_to_0_100(int(row["dispute_process_present"]))
    security_compliance = (
        0.6 * _scale_1_5_to_0_100(float(row["key_management_maturity"])) +
        0.4 * _binary_to_0_100(int(row["incident_response_present"]))
    )
    data_governance = _scale_1_5_to_0_100(float(row["data_governance_maturity"]))
    upgrade_governance = _binary_to_0_100(int(row["upgrade_policy_present"]))
    observability = _scale_1_5_to_0_100(float(row["observability_level"]))

    gqs_w = rubric["scores"]["GQS"]["dimensions"]
    GQS = (
        gqs_w["decision_rights"]["weight"] * decision_rights +
        gqs_w["dispute_resolution"]["weight"] * dispute_resolution +
        gqs_w["security_compliance"]["weight"] * security_compliance +
        gqs_w["data_governance"]["weight"] * data_governance +
        gqs_w["upgrade_governance"]["weight"] * upgrade_governance +
        gqs_w["observability"]["weight"] * observability
    )

    # --- TSS components ---
    operational_resilience = (
        0.5 * observability +
        0.5 * security_compliance
    )
    incentive_sustainability = (
        0.5 * (100.0 - _scale_1_5_to_0_100(float(row["trust_asymmetry_level"]))) +
        0.5 * (100.0 - min(30.0, float(row["stakeholders_count"])) / 30.0 * 100.0 * 0.3)
    )
    ethics_legitimacy = (
        0.5 * (100.0 - min(10.0, float(row["dispute_frequency_per_month"])) / 10.0 * 100.0) +
        0.5 * (100.0 - _scale_1_5_to_0_100(float(row["regulatory_pressure"])))
    )
    ecosystem_dependence_risk = (
        0.5 * (100.0 - economic_viability) +
        0.5 * (100.0 - org_capability)
    )

    tss_w = rubric["scores"]["TSS"]["dimensions"]
    TSS = (
        tss_w["operational_resilience"]["weight"] * operational_resilience +
        tss_w["incentive_sustainability"]["weight"] * incentive_sustainability +
        tss_w["ethics_legitimacy"]["weight"] * ethics_legitimacy +
        tss_w["ecosystem_dependence_risk"]["weight"] * ecosystem_dependence_risk
    )

    # --- Overall index + penalties ---
    w_ars = rubric["scores"]["ARS"]["weight"]
    w_gqs = rubric["scores"]["GQS"]["weight"]
    w_tss = rubric["scores"]["TSS"]["weight"]

    base_index = w_ars * ARS + w_gqs * GQS + w_tss * TSS

    penalties = rubric["penalties"]
    penalty_points = 0.0
    reasons = []

    if int(row["incident_response_present"]) == 0:
        penalty_points += penalties["missing_incident_response"]["points"]
        reasons.append("Missing incident-response governance")
    if int(row["upgrade_policy_present"]) == 0:
        penalty_points += penalties["missing_upgrade_policy"]["points"]
        reasons.append("Missing upgrade/patch governance")
    if int(row["dispute_process_present"]) == 0:
        penalty_points += penalties["missing_dispute_process"]["points"]
        reasons.append("Missing dispute-resolution governance")
    if int(row["decision_rights_clarity"]) == 0:
        penalty_points += penalties["unclear_decision_rights"]["points"]
        reasons.append("Unclear decision rights")

    bgate_index = max(0.0, min(100.0, base_index - penalty_points))

    # rating bands for non-technical readers
    thr = rubric["thresholds"]
    if bgate_index >= thr["green"]:
        rating = "GREEN (Low governance/adoption risk)"
    elif bgate_index >= thr["yellow"]:
        rating = "YELLOW (Moderate governance/adoption risk)"
    else:
        rating = "RED (High governance/adoption risk)"

    return ScoreResult(
        scenario_id=str(row["scenario_id"]),
        ARS=round(ARS, 2),
        GQS=round(GQS, 2),
        TSS=round(TSS, 2),
        bgate_index=round(bgate_index, 2),
        penalty_points=round(penalty_points, 2),
        rating=rating,
        penalty_reasons="; ".join(reasons) if reasons else "None"
    )

def score_file(csv_path: str, rubric_path: str = "rubric/bgate_rubric.yaml") -> pd.DataFrame:
    rubric = load_rubric(rubric_path)
    df = pd.read_csv(csv_path)

    results = [score_one(df.iloc[i], rubric) for i in range(len(df))]
    out = pd.DataFrame([r.__dict__ for r in results])
    return out
