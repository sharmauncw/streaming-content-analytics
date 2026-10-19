"""Shared helpers for the streaming-content-analytics pipeline."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load movies + ratings and enrich movies with release year and genre lists."""
    movies = pd.read_csv(DATA_DIR / "movies.csv")
    ratings = pd.read_csv(DATA_DIR / "ratings.csv")

    # Release year is embedded in the title, e.g. "Toy Story (1995)"
    movies["year"] = (
        movies["title"].str.extract(r"\((\d{4})\)")[0].astype("Int64")
    )
    movies["genre_list"] = movies["genres"].apply(
        lambda g: [] if g == "(no genres listed)" else g.split("|")
    )
    return movies, ratings


def movie_stats(movies: pd.DataFrame, ratings: pd.DataFrame) -> pd.DataFrame:
    """Per-movie stats: rating count, mean rating, genre list, year."""
    agg = (
        ratings.groupby("movieId")["rating"]
        .agg(n_ratings="count", avg_rating="mean")
        .reset_index()
    )
    stats = movies.merge(agg, on="movieId", how="left")
    stats["n_ratings"] = stats["n_ratings"].fillna(0).astype(int)
    return stats


def ensure_dirs() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def save_plotly(fig, png_name: str, html_name: str | None = None,
                width: int = 1000, height: int = 600, scale: int = 2) -> None:
    """Save a Plotly figure as PNG (+ optionally interactive HTML).

    PNG export needs Chrome (kaleido). If Chrome isn't available the PNG is
    skipped with a warning instead of crashing the pipeline — the HTML
    version (no Chrome needed) is always written.
    """
    if html_name:
        fig.write_html(CHARTS_DIR / html_name, include_plotlyjs="cdn")
    try:
        fig.write_image(CHARTS_DIR / png_name, width=width, height=height, scale=scale)
    except Exception as exc:  # kaleido raises RuntimeError without Chrome
        print(f"WARNING: skipped {png_name} — PNG export needs Google Chrome "
              f"installed ({exc}). The .html chart was still saved.")
        return
    print(f"saved charts/{png_name}" + (f" + {html_name}" if html_name else ""))
