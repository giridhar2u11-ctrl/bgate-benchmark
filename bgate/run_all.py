from __future__ import annotations
import os
import pandas as pd

from bgate.generate_data import generate_scenarios
from bgate.score import score_file
from bgate.report import write_markdown_report, write_pdf_report

def run_all(n_scenarios: int = 40, seed: int = 7) -> None:
    os.makedirs("data", exist_ok=True)
    os.makedirs("outputs/scores", exist_ok=True)
    os.makedirs("outputs/reports", exist_ok=True)

    # 1) Generate synthetic benchmark dataset
    df = generate_scenarios(n=n_scenarios, seed=seed)
    df.to_csv("data/scenarios.csv", index=False)

    # 2) Score scenarios
    scores = score_file("data/scenarios.csv")
    scores_path = "outputs/scores/bgate_scores.csv"
    scores.to_csv(scores_path, index=False)

    # 3) Generate per-scenario reports
    scenarios = pd.read_csv("data/scenarios.csv")
    for _, srow in scenarios.iterrows():
        sid = srow["scenario_id"]
        score_row = scores[scores["scenario_id"] == sid].iloc[0]
        md_path = write_markdown_report("outputs/reports", srow, score_row)
        pdf_path = md_path.replace(".md", ".pdf")
        write_pdf_report(md_path, pdf_path)

    print("✅ Done!")
    print("Generated:")
    print("- data/scenarios.csv")
    print(f"- {scores_path}")
    print("- outputs/reports/*.md and *.pdf")

if __name__ == "__main__":
    run_all()
