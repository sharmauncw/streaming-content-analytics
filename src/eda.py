"""Exploratory data analysis: summary stats + charts (PNG via kaleido, one interactive HTML)."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import CHARTS_DIR, ensure_dirs, load_data, movie_stats, save_plotly

PALETTE = px.colors.qualitative.Set2
HEATMAP_SCALE = "Plasma"


def summary_stats(movies: pd.DataFrame, ratings: pd.DataFrame) -> None:
    stats = movie_stats(movies, ratings)
    all_genres = sorted({g for genres in movies["genre_list"] for g in genres})
    print("=" * 60)
    print("STREAMING CONTENT ANALYTICS — EDA SUMMARY")
    print("=" * 60)
    print(f"Movies:            {len(movies):>8,}")
    print(f"Ratings:           {len(ratings):>8,}")
    print(f"Unique users:      {ratings['userId'].nunique():>8,}")
    print(f"Unique genres:     {len(all_genres):>8,}")
    print(f"Year range:        {movies['year'].min():>8.0f} – {movies['year'].max():.0f}")
    print(f"Rating range:      {ratings['rating'].min():>8.1f} – {ratings['rating'].max():.1f}")
    print(f"Mean rating:       {ratings['rating'].mean():>8.3f}")
    print(f"Movies w/ >=50 ratings: {(stats['n_ratings'] >= 50).sum():>4,}")
    print()
    print("Top 10 most-rated movies:")
    top = stats.nlargest(10, "n_ratings")[["title", "n_ratings", "avg_rating"]]
    for _, r in top.iterrows():
        print(f"  {r['title'][:45]:45s} {r['n_ratings']:>5,} ratings  avg {r['avg_rating']:.2f}")
    print()


def chart_ratings_distribution(ratings: pd.DataFrame) -> None:
    fig = px.histogram(
        ratings, x="rating", nbins=10, color_discrete_sequence=["#636EFA"],
        title="Distribution of Ratings (0.5 – 5.0 stars)",
    )
    fig.update_layout(xaxis_title="Rating", yaxis_title="Count",
                     plot_bgcolor="#F7F9FC", bargap=0.15,
                     title_font_size=18)
    fig.update_traces(marker_line_color="white", marker_line_width=1.5)
    save_plotly(fig, "ratings_distribution.png", width=900, height=520)


def chart_top_genres(movies: pd.DataFrame, ratings: pd.DataFrame) -> None:
    # Genre-level average across well-rated movies only (each movie needs >= 50 ratings)
    stats = movie_stats(movies, ratings)
    popular = stats[stats["n_ratings"] >= 50].copy()
    exploded = popular.explode("genre_list").dropna(subset=["genre_list"])
    g = (
        exploded.groupby("genre_list")["avg_rating"]
        .agg(avg="mean", movies="count")
        .sort_values("avg", ascending=False)
    )
    fig = px.bar(
        g.reset_index(), x="genre_list", y="avg", color="avg",
        color_continuous_scale="Turbo",
        title="Average Rating by Genre (movies with 50+ ratings)",
        labels={"genre_list": "Genre", "avg": "Average rating"},
    )
    fig.update_layout(plot_bgcolor="#F7F9FC", xaxis_tickangle=-35,
                     title_font_size=18, coloraxis_colorbar_title="Avg rating")
    save_plotly(fig, "top_genres.png", width=1000, height=540)


def chart_ratings_over_years(movies: pd.DataFrame, ratings: pd.DataFrame) -> None:
    merged = ratings.merge(movies[["movieId", "year"]], on="movieId")
    by_year = (
        merged.dropna(subset=["year"]).groupby("year")
        .agg(titles=("movieId", "nunique"), avg_rating=("rating", "mean"))
        .reset_index()
    )
    fig = go.Figure()
    fig.add_bar(x=by_year["year"], y=by_year["titles"], name="Titles",
               marker_color="#19D3F3")
    fig.add_scatter(x=by_year["year"], y=by_year["avg_rating"], name="Avg rating",
                    yaxis="y2", mode="lines+markers",
                    marker_color="#EF553B", line=dict(width=3))
    fig.update_layout(
        title="Catalog Growth vs. Average Rating by Release Year",
        xaxis_title="Release year", yaxis_title="Number of titles",
        yaxis2=dict(title="Average rating", overlaying="y", side="right",
                    range=[2.5, 4.5]),
        plot_bgcolor="#F7F9FC", legend=dict(orientation="h", y=1.08),
        title_font_size=18,
    )
    path_png = "ratings_over_years.png"
    path_html = "ratings_over_years.html"
    save_plotly(fig, path_png, path_html, width=1100, height=520)


def chart_genre_heatmap(movies: pd.DataFrame, ratings: pd.DataFrame) -> None:
    # Mean rating by genre x decade
    stats = movie_stats(movies, ratings).dropna(subset=["year"])
    stats["decade"] = (stats["year"] // 10 * 10).astype(int).astype(str) + "s"
    exploded = stats.explode("genre_list").dropna(subset=["genre_list"])
    pivot = exploded.pivot_table(index="genre_list", columns="decade",
                                 values="avg_rating", aggfunc="mean")
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)
    fig = px.imshow(
        pivot, color_continuous_scale=HEATMAP_SCALE, aspect="auto",
        title="Average Movie Rating by Genre and Decade",
        labels=dict(x="Decade", y="Genre", color="Avg rating"),
    )
    fig.update_layout(title_font_size=18)
    fig.update_traces(texttemplate="%{z:.2f}", textfont_size=8)
    save_plotly(fig, "genre_heatmap.png", width=1100, height=620)


def main() -> None:
    ensure_dirs()
    movies, ratings = load_data()
    summary_stats(movies, ratings)
    chart_ratings_distribution(ratings)
    chart_top_genres(movies, ratings)
    chart_ratings_over_years(movies, ratings)
    chart_genre_heatmap(movies, ratings)
    print("\nEDA complete.")


if __name__ == "__main__":
    main()
