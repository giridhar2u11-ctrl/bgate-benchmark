[![DOI](https://zenodo.org/badge/1146216833.svg)](https://doi.org/10.5281/zenodo.18435587)
# B-GATE Benchmark (v1)
**B-GATE** stands for **Blockchain Governance & Adoption Trustworthiness Evaluation**.  
This repository provides a **reproducible benchmark** that scores whether a blockchain deployment scenario is **adoptable** and **governable**.

> **Plain English:** Many blockchain projects fail not because the technology is missing, but because the **governance is missing** (no clear decision rights, no dispute process, no upgrade rules, no incident response).  
> B-GATE makes those governance gaps **measurable** in a consistent, repeatable way.

---

## Why this is important (Non-technical summary)
Organizations often adopt blockchain for transparency and trust, but “trust” depends on:
- Who can change rules?
- How disputes are resolved?
- How upgrades and emergency patches are handled?
- What happens when there is a security incident?
- Whether monitoring and auditability are in place

**B-GATE converts these questions into standardized scores** so that different governance designs can be compared objectively.

---

## What this project delivers
This repository includes:

1) **Benchmark Scenarios Dataset (Synthetic)**
- `data/scenarios.csv` contains realistic, standardized blockchain deployment scenarios across domains (nonprofit donations, supply chain, healthcare access, credentialing, etc.).
- The data is **synthetic** (research/benchmark purposes) so it can be shared publicly and reproduced.

2) **Scoring Rubric (The Benchmark Standard)**
- `rubric/bgate_rubric.yaml` defines how scores are computed (weights + penalty rules).
- Penalties are applied when essential governance controls are missing.

3) **Reproducible Scoring + Reports**
- A one-command run generates:
  - `outputs/scores/bgate_scores.csv` (all scenario scores)
  - `outputs/reports/` (plain-English report per scenario in Markdown and PDF)

---

## The core output: four numbers (easy to interpret)
For each scenario, B-GATE produces:

- **ARS** = Adoption Readiness Score (0–100)  
  “Is the organization and use-case ready to adopt blockchain?”

- **GQS** = Governance Quality Score (0–100)  
  “Are decision rights, disputes, security governance, upgrades, and accountability defined?”

- **TSS** = Trustworthiness & Sustainability Score (0–100)  
  “Will the solution remain reliable, legitimate, and stable after adoption?”

- **B-GATE Index** (0–100)  
  A combined score with explicit penalties for missing governance essentials.

**Interpretation bands:**
- **GREEN**: low governance/adoption risk  
- **YELLOW**: moderate risk  
- **RED**: high risk (governance gaps likely to cause failure)

---

## Why this is a novel contribution
Most existing work measures either:
- **adoption intention** (surveys), OR
- **technical metrics**, OR
- **governance checklists**

**B-GATE unifies adoption + governance + sustainability into one reproducible benchmark** with:
- a scenario dataset,
- a scoring rubric,
- penalty rules for missing governance essentials,
- and auto-generated plain-English reports.

This makes governance and adoption **auditable and comparable** across scenarios.

---

## How to run (Step-by-step, beginner friendly)

### 1) Open Command Prompt in the project folder
Windows:
- Open the `bgate-benchmark` folder
- Click the address bar (top)
- Type `cmd` and press Enter

### 2) Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
