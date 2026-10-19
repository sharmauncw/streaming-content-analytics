# SQL Analysis Results

Analytical queries over `movies.csv` + `ratings.csv` run with DuckDB.

## Genre Rank By Avg Rating

*Rank every genre by average rating (movies with 50+ ratings only)*

**19 rows returned.** Showing first 10:

| genre     |   avg_rating |   movies |   genre_rank |
|:----------|-------------:|---------:|-------------:|
| Film-Noir |        3.994 |        4 |            1 |
| War       |        3.892 |       19 |            2 |
| Mystery   |        3.827 |       38 |            3 |
| Crime     |        3.812 |       87 |            4 |
| Drama     |        3.802 |      166 |            5 |
| IMAX      |        3.759 |       28 |            6 |
| Animation |        3.723 |       32 |            7 |
| Thriller  |        3.652 |      121 |            8 |
| Musical   |        3.648 |       21 |            9 |
| Fantasy   |        3.644 |       66 |           10 |

## Rolling Avg Rating By Year

*Yearly average rating plus a 5-year rolling average*

**106 rows returned.** Showing first 10:

|   release_year |   avg_rating |   ratings |   rolling_5yr_avg |
|---------------:|-------------:|----------:|------------------:|
|           1902 |        3.5   |         5 |             3.5   |
|           1903 |        2.5   |         2 |             3     |
|           1908 |        4     |         1 |             3.333 |
|           1915 |        2     |         1 |             3     |
|           1916 |        3.6   |         5 |             3.12  |
|           1917 |        4.5   |         1 |             3.32  |
|           1919 |        2     |         1 |             3.22  |
|           1920 |        3.813 |         8 |             3.183 |
|           1921 |        4.1   |         5 |             3.603 |
|           1922 |        3.531 |        16 |             3.589 |

## Top Movies Per Genre

*Top 3 movies per genre by average rating (30+ ratings), via ROW_NUMBER*

**57 rows returned.** Showing first 10:

| genre     | title                                                |   avg_rating |   ratings |
|:----------|:-----------------------------------------------------|-------------:|----------:|
| Action    | Fight Club (1999)                                    |        4.273 |       218 |
| Action    | Dark Knight, The (2008)                              |        4.238 |       149 |
| Action    | Princess Bride, The (1987)                           |        4.232 |       142 |
| Adventure | Lawrence of Arabia (1962)                            |        4.3   |        45 |
| Adventure | Princess Bride, The (1987)                           |        4.232 |       142 |
| Adventure | Star Wars: Episode IV - A New Hope (1977)            |        4.231 |       251 |
| Animation | Spirited Away (Sen to Chihiro no kamikakushi) (2001) |        4.155 |        87 |
| Animation | Toy Story 3 (2010)                                   |        4.109 |        55 |
| Animation | Howl's Moving Castle (Hauru no ugoku shiro) (2004)   |        4.075 |        40 |
| Children  | Toy Story 3 (2010)                                   |        4.109 |        55 |

## Rating Deciles Per Genre

*NTILE deciles of movie quality within each genre (first 40 rows)*

**40 rows returned.** Showing first 10:

| genre              | title                                                                              |   avg_rating |   decile |
|:-------------------|:-----------------------------------------------------------------------------------|-------------:|---------:|
| (no genres listed) | Death Note: Desu nôto (2006–2007)                                                  |         5    |        1 |
| (no genres listed) | Black Mirror                                                                       |         5    |        1 |
| (no genres listed) | The Adventures of Sherlock Holmes and Doctor Watson                                |         5    |        1 |
| (no genres listed) | The Godfather Trilogy: 1972-1990 (1992)                                            |         4.75 |        1 |
| (no genres listed) | Whiplash (2013)                                                                    |         4.75 |        2 |
| (no genres listed) | Ali Wong: Baby Cobra (2016)                                                        |         4.5  |        2 |
| (no genres listed) | Cosmos                                                                             |         4.5  |        2 |
| (no genres listed) | The Adventures of Sherlock Holmes and Doctor Watson: The Hunt for the Tiger (1980) |         4.5  |        2 |
| (no genres listed) | Too Funny to Fail: The Life and Death of The Dana Carvey Show (2017)               |         4.5  |        3 |
| (no genres listed) | Paterson                                                                           |         4.5  |        3 |

## Year Over Year Title Counts

*Catalog title counts per release year with YoY growth via LAG*

**106 rows returned.** Showing first 10:

|   release_year |   titles | prev_year_titles   |   yoy_growth_pct |
|---------------:|---------:|:-------------------|-----------------:|
|           1902 |        1 | <NA>               |              nan |
|           1903 |        1 | 1                  |                0 |
|           1908 |        1 | 1                  |                0 |
|           1915 |        1 | 1                  |                0 |
|           1916 |        4 | 1                  |              300 |
|           1917 |        1 | 4                  |              -75 |
|           1919 |        1 | 1                  |                0 |
|           1920 |        2 | 1                  |              100 |
|           1921 |        1 | 2                  |              -50 |
|           1922 |        1 | 1                  |                0 |

## Genre Share By Decade

*How each decade's catalog splits across genres (CTE + windowed share)*

**1501 rows returned.** Showing first 10:

|   decade | genre     |   titles |   pct_of_decade |
|---------:|:----------|---------:|----------------:|
|     1902 | Adventure |        1 |            25   |
|     1902 | Action    |        1 |            25   |
|     1902 | Sci-Fi    |        1 |            25   |
|     1902 | Fantasy   |        1 |            25   |
|     1903 | Western   |        1 |            50   |
|     1903 | Crime     |        1 |            50   |
|     1908 | Sci-Fi    |        1 |            33.3 |
|     1908 | Comedy    |        1 |            33.3 |
|     1908 | Animation |        1 |            33.3 |
|     1915 | Drama     |        1 |            50   |

## Rater Activity Quartiles

*How rating generosity varies with user activity (NTILE over users)*

**4 rows returned.** Showing first 10:

|   activity_quartile |   users |   avg_ratings_per_user |   mean_rating_given |
|--------------------:|--------:|-----------------------:|--------------------:|
|                   1 |     153 |                     26 |               3.674 |
|                   2 |     153 |                     50 |               3.737 |
|                   3 |     152 |                    114 |               3.677 |
|                   4 |     152 |                    472 |               3.54  |
