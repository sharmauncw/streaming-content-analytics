"""Cluster movies by genre + year + average rating.

Features: multi-hot genre vector, release year (standardized), mean rating (standardized).
KMeans over k=3..10; elbow (inertia) and silhouette printed; best-silhouette k is used.
(k=2 is skipped — it always wins by splitting the catalog into two giant blobs,
which isn't a useful taste grouping.)
A PCA 2-D scatter colored by cluster is saved as PNG + HTML, plus cluster_profiles.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from utils import CHARTS_DIR, OUTPUTS_DIR, ensure_dirs, load_data, movie_stats, save_plotly


def build_features(movies: pd.DataFrame, ratings: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    stats = movie_stats(movies, ratings).dropna(subset=["year", "avg_rating"]).reset_index(drop=True)
    all_genres = sorted({g for genres in stats["genre_list"] for g in genres})
    genre_mat = np.zeros((len(stats), len(all_genres)), dtype=float)
    for i, genres in enumerate(stats["genre_list"]):
        for g in genres:
            genre_mat[i, all_genres.index(g)] = 1.0
    X = np.hstack([
        genre_mat,
        stats[["year", "avg_rating"]].to_numpy(dtype=float),
    ])
    X = StandardScaler().fit_transform(X)
    feature_names = [f"genre:{g}" for g in all_genres] + ["year", "avg_rating"]
    return stats, X, feature_names


def choose_k(X: np.ndarray, k_min: int = 3, k_max: int = 10) -> int:
    """Print inertia (elbow) and silhouette for each k; return best silhouette.

    k=2 is skipped: on this data it always wins by splitting the catalog into
    two giant blobs (drama/comedy vs adventure/action), which tells us nothing
    useful. k_min=3 keeps the comparison honest among granular taste groups.
    """
    print("k   inertia      silhouette")
    print("-" * 30)
    scores: dict[int, float] = {}
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels, sample_size=min(3000, len(X)), random_state=42)
        scores[k] = sil
        print(f"{k:<3d} {km.inertia_:>10,.1f}  {sil:>10.4f}")
    best_k = max(scores, key=scores.get)
    print(f"\nBest k by silhouette (k>={k_min}): {best_k}\n")
    return best_k


def cluster_profiles(stats: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    stats = stats.copy()
    stats["cluster"] = labels
    all_genres = sorted({g for genres in stats["genre_list"] for g in genres})
    rows = []
    for c in sorted(stats["cluster"].unique()):
        sub = stats[stats["cluster"] == c]
        genre_counts = pd.Series(
            [g for genres in sub["genre_list"] for g in genres]
        ).value_counts()
        top3 = ", ".join(f"{g} ({n/len(sub):.0%})" for g, n in genre_counts.head(3).items())
        rows.append({
            "cluster": int(c),
            "size": len(sub),
            "top_genres": top3,
            "avg_rating": round(sub["avg_rating"].mean(), 3),
            "avg_year": int(sub["year"].mean()),
            "avg_ratings_per_movie": round(sub["n_ratings"].mean(), 1),
        })
    return pd.DataFrame(rows).sort_values("cluster")


def scatter_plot(stats: pd.DataFrame, X: np.ndarray, labels: np.ndarray) -> None:
    coords = PCA(n_components=2, random_state=42).fit_transform(X)
    df = pd.DataFrame({
        "pc1": coords[:, 0], "pc2": coords[:, 1],
        "cluster": labels.astype(str),
        "title": stats["title"],
        "year": stats["year"],
        "avg_rating": stats["avg_rating"].round(2),
    })
    fig = px.scatter(
        df, x="pc1", y="pc2", color="cluster",
        hover_data=["title", "year", "avg_rating"],
        title="Movie Clusters (PCA of genre + year + rating features)",
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"pc1": "PC 1", "pc2": "PC 2", "cluster": "Cluster"},
    )
    fig.update_traces(marker=dict(size=5, opacity=0.75, line_width=0))
    fig.update_layout(plot_bgcolor="#F7F9FC", title_font_size=18)
    save_plotly(fig, "cluster_scatter.png", "cluster_scatter.html",
                width=1000, height=620)


def main() -> None:
    ensure_dirs()
    movies, ratings = load_data()
    stats, X, _ = build_features(movies, ratings)
    print(f"Clustering {len(stats):,} movies ...")
    k = choose_k(X)
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = km.fit_predict(X)
    profiles = cluster_profiles(stats, labels)
    print(profiles.to_string(index=False))
    profiles.to_csv(OUTPUTS_DIR / "cluster_profiles.csv", index=False)
    print(f"\nsaved outputs/cluster_profiles.csv")
    scatter_plot(stats, X, labels)
    print("\nClustering complete.")


if __name__ == "__main__":
    main()
