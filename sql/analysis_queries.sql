-- ============================================================
-- Streaming Content Analytics — analytical SQL (runs on the CSVs via DuckDB)
-- Execute with: python sql/run_sql.py   (runs from the repo root)
-- ============================================================

-- QUERY: genre_rank_by_avg_rating
-- DESCRIPTION: Rank every genre by average rating (movies with 50+ ratings only)
WITH movie_stats AS (
    SELECT m.movieId, m.genres, AVG(r.rating) AS avg_r, COUNT(*) AS n
    FROM read_csv('data/movies.csv') AS m
    JOIN read_csv('data/ratings.csv') AS r USING (movieId)
    GROUP BY m.movieId, m.genres
),
popular AS (
    SELECT * FROM movie_stats WHERE n >= 50
),
genre_ratings AS (
    SELECT UNNEST(string_split(genres, '|')) AS genre, avg_r
    FROM popular
)
SELECT
    genre,
    ROUND(AVG(avg_r), 3) AS avg_rating,
    COUNT(*) AS movies,
    RANK() OVER (ORDER BY AVG(avg_r) DESC) AS genre_rank
FROM genre_ratings
GROUP BY genre
ORDER BY genre_rank;

-- QUERY: rolling_avg_rating_by_year
-- DESCRIPTION: Yearly average rating plus a 5-year rolling average
WITH yearly AS (
    SELECT
        regexp_extract(m.title, '\((\d{4})\)', 1)::INT AS yr,
        AVG(r.rating) AS avg_r,
        COUNT(*) AS n
    FROM read_csv('data/movies.csv') AS m
    JOIN read_csv('data/ratings.csv') AS r USING (movieId)
    WHERE regexp_extract(m.title, '\((\d{4})\)', 1) ~ '^\d{4}$'
    GROUP BY yr
)
SELECT
    yr AS release_year,
    ROUND(avg_r, 3) AS avg_rating,
    n AS ratings,
    ROUND(AVG(avg_r) OVER (ORDER BY yr ROWS BETWEEN 4 PRECEDING AND CURRENT ROW), 3) AS rolling_5yr_avg
FROM yearly
ORDER BY yr;

-- QUERY: top_movies_per_genre
-- DESCRIPTION: Top 3 movies per genre by average rating (30+ ratings), via ROW_NUMBER
WITH movie_stats AS (
    SELECT m.movieId, m.title, m.genres, AVG(r.rating) AS avg_r, COUNT(*) AS n
    FROM read_csv('data/movies.csv') AS m
    JOIN read_csv('data/ratings.csv') AS r USING (movieId)
    GROUP BY m.movieId, m.title, m.genres
),
exploded AS (
    SELECT s.title, s.avg_r, s.n, UNNEST(string_split(s.genres, '|')) AS genre
    FROM movie_stats AS s
    WHERE s.n >= 30
),
ranked AS (
    SELECT
        genre, title, ROUND(avg_r, 3) AS avg_rating, n,
        ROW_NUMBER() OVER (PARTITION BY genre ORDER BY avg_r DESC) AS rn
    FROM exploded
)
SELECT genre, title, avg_rating, n AS ratings
FROM ranked
WHERE rn <= 3
ORDER BY genre, rn;

-- QUERY: rating_deciles_per_genre
-- DESCRIPTION: NTILE deciles of movie quality within each genre (first 40 rows)
WITH movie_stats AS (
    SELECT m.movieId, m.title, m.genres, AVG(r.rating) AS avg_r
    FROM read_csv('data/movies.csv') AS m
    JOIN read_csv('data/ratings.csv') AS r USING (movieId)
    GROUP BY m.movieId, m.title, m.genres
),
exploded AS (
    SELECT s.title, s.avg_r, UNNEST(string_split(s.genres, '|')) AS genre
    FROM movie_stats AS s
)
SELECT
    genre,
    title,
    ROUND(avg_r, 2) AS avg_rating,
    NTILE(10) OVER (PARTITION BY genre ORDER BY avg_r DESC) AS decile
FROM exploded
ORDER BY genre, decile, avg_r DESC
LIMIT 40;

-- QUERY: year_over_year_title_counts
-- DESCRIPTION: Catalog title counts per release year with YoY growth via LAG
WITH yearly AS (
    SELECT
        regexp_extract(title, '\((\d{4})\)', 1)::INT AS yr,
        COUNT(*) AS titles
    FROM read_csv('data/movies.csv')
    WHERE regexp_extract(title, '\((\d{4})\)', 1) ~ '^\d{4}$'
    GROUP BY yr
)
SELECT
    yr AS release_year,
    titles,
    LAG(titles) OVER (ORDER BY yr) AS prev_year_titles,
    ROUND(
        100.0 * (titles - LAG(titles) OVER (ORDER BY yr))
        / NULLIF(LAG(titles) OVER (ORDER BY yr), 0), 1
    ) AS yoy_growth_pct
FROM yearly
ORDER BY yr;

-- QUERY: genre_share_by_decade
-- DESCRIPTION: How each decade's catalog splits across genres (CTE + windowed share)
WITH decade_genres AS (
    SELECT
        (regexp_extract(title, '\((\d{4})\)', 1)::INT / 10 * 10)::INT AS decade,
        UNNEST(string_split(genres, '|')) AS genre
    FROM read_csv('data/movies.csv')
    WHERE regexp_extract(title, '\((\d{4})\)', 1) ~ '^\d{4}$'
)
SELECT
    decade,
    genre,
    COUNT(*) AS titles,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY decade), 1) AS pct_of_decade
FROM decade_genres
GROUP BY decade, genre
ORDER BY decade, titles DESC;

-- QUERY: rater_activity_quartiles
-- DESCRIPTION: How rating generosity varies with user activity (NTILE over users)
WITH user_stats AS (
    SELECT userId, COUNT(*) AS n, AVG(rating) AS avg_given
    FROM read_csv('data/ratings.csv')
    GROUP BY userId
),
quartiled AS (
    SELECT n, avg_given, NTILE(4) OVER (ORDER BY n) AS activity_quartile
    FROM user_stats
)
SELECT
    activity_quartile,
    COUNT(*) AS users,
    ROUND(AVG(n), 0) AS avg_ratings_per_user,
    ROUND(AVG(avg_given), 3) AS mean_rating_given
FROM quartiled
GROUP BY activity_quartile
ORDER BY activity_quartile;
