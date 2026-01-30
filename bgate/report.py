from __future__ import annotations
import os
from dataclasses import asdict
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def write_markdown_report(out_dir: str, scenario_row: pd.Series, score_row: pd.Series) -> str:
    os.makedirs(out_dir, exist_ok=True)
    sid = score_row["scenario_id"]
    path = os.path.join(out_dir, f"{sid}.md")

    md = f"""# B-GATE Report — {sid}

## Plain-English Summary
This report evaluates the **adoption readiness** and **governance quality** of a blockchain deployment scenario using the B-GATE benchmark.
The output is a standardized score that helps compare different governance designs and identify risk areas.

## Key Result
- **B-GATE Index:** {score_row["bgate_index"]}/100  
- **Rating:** {score_row["rating"]}
- **Penalty points:** {score_row["penalty_points"]}  
- **Penalty reasons:** {score_row["penalty_reasons"]}

## Score Breakdown
- **ARS (Adoption Readiness):** {score_row["ARS"]}/100  
- **GQS (Governance Quality):** {score_row["GQS"]}/100  
- **TSS (Trustworthiness & Sustainability):** {score_row["TSS"]}/100  

## Scenario Description (Benchmark Input)
- Domain: {scenario_row["domain"]}
- Governance model: {scenario_row["governance_model"]}
- Stakeholders: {scenario_row["stakeholders_count"]}
- Trust asymmetry: {scenario_row["trust_asymmetry_level"]} / 5
- Data sensitivity: {scenario_row["data_sensitivity"]} / 5
- Dispute frequency: {scenario_row["dispute_frequency_per_month"]} per month
- Regulatory pressure: {scenario_row["regulatory_pressure"]} / 5
- Adoption stage: {scenario_row["adoption_stage"]}

## Governance Evidence Flags (Binary)
- Incident response present: {scenario_row["incident_response_present"]}
- Upgrade policy present: {scenario_row["upgrade_policy_present"]}
- Dispute process present: {scenario_row["dispute_process_present"]}
- Decision rights clarity: {scenario_row["decision_rights_clarity"]} (0 unclear, 2 clear)

## Notes for Non-Technical Readers
- A high score means the scenario has **clear rules**, **accountability**, and **operational readiness**.
- Penalties occur when essential governance policies are missing (incident response, upgrades, dispute resolution, decision rights).

"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    return path

def write_pdf_report(md_path: str, pdf_path: str) -> None:
    # Simple “printable officer-friendly” PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y = height - 50

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    c.setFont("Times-Roman", 11)
    for line in lines:
        if y < 60:
            c.showPage()
            c.setFont("Times-Roman", 11)
            y = height - 50
        c.drawString(50, y, line[:110])
        y -= 14

    c.save()
