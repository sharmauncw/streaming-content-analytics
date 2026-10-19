"""Content-based movie recommender.

Each movie is represented by a TF-IDF vector over its genres; the final
score blends genre cosine similarity (70%) with release-year proximity (20%)
and average-rating proximity (10%). Genre-only similarity ties constantly
(movies sharing an identical genre string all score 1.0), so the year/rating
blend is what makes the ranking actually discriminate. Popularity (number of
ratings) breaks any remaining ties. `recommend(title, n=5)` is the public
API; running this file demos it on a few titles and writes
outputs/recommendations.md.
"""
from __future__ import annotations

from difflib import get_close_matches
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import BASE_DIR, OUTPUTS_DIR, ensure_dirs, load_data

SAMPLE_TITLES = ["Toy Story (1995)", "Pulp Fiction (1994)", "The Matrix (1999)"]

_model: dict | None = None


def _fit() -> dict:
    """Fit (once, cached) the TF-IDF model over the genre strings."""
    global _model
    if _model is None:
        movies, ratings = load_data()
        vec = TfidfVectorizer(tokenizer=lambda s: s.split("|"), token_pattern=None, lowercase=False)
        genre_matrix = vec.fit_transform(movies["genres"])
        agg = ratings.groupby("movieId")["rating"].agg(
            n_ratings="count", avg_rating="mean")
        movies = movies.join(agg, on="movieId")
        movies["n_ratings"] = movies["n_ratings"].fillna(0).astype(int)
        movies["avg_rating"] = movies["avg_rating"].fillna(ratings["rating"].mean())
        _model = {"movies": movies, "matrix": genre_matrix}
    return _model


def recommend(title: str, n: int = 5) -> pd.DataFrame:
    """Return the n most similar movies to `title`.

    Score = 0.7 * genre TF-IDF cosine similarity
          + 0.2 * release-year proximity  (1 / (1 + |dy| / 10))
          + 0.1 * average-rating proximity (1 - |dr| / 4.5).
    Ties are broken by popularity (number of ratings).
    Fuzzy-matches the title if it's not exact.
    """
    model = _fit()
    movies, matrix = model["movies"], model["matrix"]
    titles = movies["title"].tolist()
    if title not in titles:
        guess = get_close_matches(title, titles, n=1, cutoff=0.5)
        if not guess:
            raise ValueError(f"No close match found for {title!r}")
        title = guess[0]
        print(f"(fuzzy match -> {title})")
    idx = titles.index(title)
    genre_sims = cosine_similarity(matrix[idx], matrix).ravel()
    years = movies["year"].astype(float).to_numpy()
    own_year = years[idx]
    years = np.where(np.isnan(years), own_year, years)  # missing year -> neutral
    avg_r = movies["avg_rating"].to_numpy()
    year_prox = 1.0 / (1.0 + np.abs(years - own_year) / 10.0)
    rating_prox = 1.0 - np.abs(avg_r - avg_r[idx]) / 4.5
    sims = 0.7 * genre_sims + 0.2 * year_prox + 0.1 * rating_prox
    # Sort by similarity desc, then popularity desc; exclude the movie itself.
    order = np.lexsort((-movies["n_ratings"].to_numpy(), -sims))
    order = order[order != idx][:n]
    recs = movies.iloc[order][["title", "genres", "n_ratings"]].copy()
    recs["similarity"] = np.round(sims[order], 3)
    return recs.reset_index(drop=True)


def main() -> None:
    ensure_dirs()
    lines = ["# Sample Recommendations", "",
             "Content-based recommender: genre TF-IDF cosine similarity blended "
             "with release-year and rating proximity (70/20/10); popularity breaks ties.",
             ""]
    for title in SAMPLE_TITLES:
        print(f"\nRecommendations for: {title}")
        recs = recommend(title, n=5)
        print(recs[["title", "genres", "similarity"]].to_string(index=False))
        lines.append(f"## {title}")
        lines.append("")
        for _, r in recs.iterrows():
            lines.append(f"- **{r['title']}** — _{r['genres']}_ (similarity {r['similarity']:.3f})")
        lines.append("")
    out = OUTPUTS_DIR / "recommendations.md"
    out.write_text("\n".join(lines))
    print(f"\nsaved {out.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
