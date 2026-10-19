"""Execute sql/analysis_queries.sql against the CSVs with DuckDB.

Writes outputs/sql_results.md with row counts + the first 10 rows of each query.
Run from anywhere: python sql/run_sql.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import duckdb
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = REPO_ROOT / "sql" / "analysis_queries.sql"
OUT_FILE = REPO_ROOT / "outputs" / "sql_results.md"


def parse_queries(text: str) -> list[tuple[str, str, str]]:
    """Split the SQL file into (name, description, sql) blocks."""
    blocks = re.split(r"^-- QUERY:\s*", text, flags=re.M)[1:]
    out = []
    for b in blocks:
        name, rest = b.split("\n", 1)
        desc = ""
        m = re.match(r"-- DESCRIPTION:\s*(.*)\n", rest)
        if m:
            desc = m.group(1).strip()
            rest = rest[m.end():]
        out.append((name.strip(), desc, rest.strip()))
    return out


def main() -> None:
    os.chdir(REPO_ROOT)  # so relative 'data/...' paths resolve
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    queries = parse_queries(SQL_FILE.read_text())
    con = duckdb.connect()
    lines = ["# SQL Analysis Results", "",
             "Analytical queries over `movies.csv` + `ratings.csv` run with DuckDB.",
             ""]
    for name, desc, sql in queries:
        df: pd.DataFrame = con.execute(sql).df()
        print(f"{name}: {len(df)} rows")
        assert len(df) > 0, f"query {name} returned no rows!"
        lines.append(f"## {name.replace('_', ' ').title()}")
        lines.append("")
        if desc:
            lines.append(f"*{desc}*")
            lines.append("")
        lines.append(f"**{len(df)} rows returned.** Showing first 10:")
        lines.append("")
        lines.append(df.head(10).to_markdown(index=False))
        lines.append("")
    con.close()
    OUT_FILE.write_text("\n".join(lines))
    print(f"\nsaved {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
