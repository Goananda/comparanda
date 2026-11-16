# Analysis scripts

Run everything with `bash analysis/run_all.sh` from the repository root. Intermediate files go to `build/`, which is not part of the repository.

Русская версия: [README.ru.md](README.ru.md)

| Step | File | What it does |
|---|---|---|
| 1 | `prep.py` | Builds the 0/1 tradition-by-motif matrix from `data/source/` and fixes eight motif codes that carry a stray underscore. |
| 2 | `clus.py` | TF-IDF weights, 30 latent dimensions (LSA), Ward clustering. Prints the geographic coherence of the clusters, agreement with k-means and average linkage, and stability under resampling of motifs. |
| 3 | `nmf.py` | Non-negative matrix factorisation into 12 motif complexes, the best of six initialisations. |
| 4 | `embed.py` | UMAP projections of traditions and motifs, and a stability check for NMF. |
| 5 | `export.py` | Gathers everything the page needs into `data.json`: the cluster hierarchy with names and characteristic motifs, the complexes, the principal axes, the decay of similarity with distance, the motif atlas. |
| 6 | `make_tables.py` | Writes the tables in `data/derived/`. |
| 7 | `build_geo.mjs` | Projects the land outline and the coordinates of traditions (Equal Earth projection centred on 153° E). |
| 8 | `site/build.py` | Assembles `index.html` from `site/src/` and the data. |

Things to know:

- Clusters and complexes use traditions with 15 or more motifs (831 of 923) and motifs recorded in at least five of them (2,423).
- Cluster and complex names are set by hand in `export.py`, in English and Russian, from the membership of each unit. They are tied to this version of the data: if the source files change, cluster sizes will shift and the dictionary of names will need updating.
- The principal axes are computed separately for sections A–I and J–N, on traditions with 15 or more motifs of the group and motifs recorded in at least ten of them.
- The page does not show motif definitions, only codes and titles. Full definitions are in `data/source/motifs.csv`.
- `exploratory/` holds the trials and checks behind statements on the page: a comparison of methods for the axes, cluster membership, similarity between clusters, the contribution of pairs of regions to the far distance bands. They do not affect the build.

## Languages of the page

The page is in English by default and has a Russian version; the choice is kept in the browser. Motif and tradition names are not translated.

- Static text lives in `site/src/body.html` as pairs of elements marked `lang="en"` and `lang="ru"`; a CSS rule hides the language that is not selected.
- Text produced by scripts (captions, tooltips, notes) lives in the `TX` dictionary at the top of `site/src/app.js`, and the captions of the principal axes in `TXT` inside `initAxes`.
- Names of clusters and complexes in both languages come from `export.py`.

## Cluster colours

Each of the twelve clusters has its own colour, and all clusters are drawn as circles. The colours are the variables `--k0` … `--k11` in `site/src/style.css`, with separate values for the light and the dark theme. The colour slot of every node of the hierarchy is the `col` field set in `export.py`: when a cluster splits, one part keeps the colour and the other gets a new one, so the map changes as little as possible from step to step.

`exploratory/check_palette.py` prints the closest pairs of colours. In both themes every pair differs by at least 17 for normal vision and 8.8 under simulated red-green colour-vision deficiency (Euclidean distance in OKLab ×100). Twelve hues cannot all be told apart by colour alone under every condition, so the legend, the direct labels on the similarity plot and the tooltips name the cluster as well.
