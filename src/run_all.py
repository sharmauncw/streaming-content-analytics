"""Run the full streaming-content-analytics pipeline end to end."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import clustering
import eda
import recommender


def main() -> None:
    print("\n" + "=" * 60)
    print("STEP 1/3 — Exploratory data analysis")
    print("=" * 60)
    eda.main()

    print("\n" + "=" * 60)
    print("STEP 2/3 — Movie clustering")
    print("=" * 60)
    clustering.main()

    print("\n" + "=" * 60)
    print("STEP 3/3 — Content-based recommender demo")
    print("=" * 60)
    recommender.main()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE — see outputs/ for charts and tables")
    print("=" * 60)


if __name__ == "__main__":
    main()
