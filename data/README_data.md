# Data

This project uses the **MovieLens ml-latest-small** dataset, provided free for non-commercial research by **GroupLens Research** at the University of Minnesota.

- Source: https://grouplens.org/datasets/movielens/
- Contents here: `movies.csv` (9,742 titles) and `ratings.csv` (100,836 ratings from 610 users). The other files from the zip (`links.csv`, `tags.csv`) aren't needed for this project, so I left them out.
- Citation: F. Maxwell Harper and Joseph A. Konstan. 2015. *The MovieLens Datasets: History and Context.* ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4: 19:1–19:19. <https://doi.org/10.1145/2827872>

If you want to reproduce from scratch, download `ml-latest-small.zip` from the link above, unzip it, and drop `movies.csv` and `ratings.csv` into this folder. Everything downstream runs offline from there.
