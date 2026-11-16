# Data

All tables are UTF-8. Tradition and motif names are in English, as in the source files.

Русская версия: [README.ru.md](README.ru.md)

## `source/`: source files

Downloaded on 16 November 2026 from https://twopoints.blog/datasets/folklore/ and left unchanged. This is the version of the catalogue by Yu. E. Berezkin and E. N. Duvakin from the replication package of Michalopoulos and Xue (2021; Harvard Dataverse, [doi:10.7910/DVN/IXOHKB](https://doi.org/10.7910/DVN/IXOHKB), CC0 1.0), cleaned by Kenneth S. Reyes for the post ["The tales we tell"](https://twopoints.blog/posts/2023-04-22-the-tales-we-tell/).

| File | Rows | Columns |
|---|---|---|
| `motifs.csv` | 2,564 | `motif_id`: motif code in the catalogue (the first letter is the section, A–N); `title`: motif title; `description`: motif definition |
| `groups_motifs.csv` | 82,046 | unnamed first column: row number of the original table; `group`: tradition; `motif_id`: a motif recorded in that tradition |
| `coords_clean.json` | 923 | `group`, `longitude`, `latitude`: a nominal point for the tradition on the map |
| `groups_concepts.csv` | 5,538 | `group`, `longitude`, `latitude`, `concept` (coldness, earthquakes, farming, fishing, hunting, pastoral), `share`: computed by the blog author, see his post |
| `regressions.csv` | 199 | country-level indicators taken by the blog author from the replication package: `cntry`, `lntrust_wvsavg`, `tricksters_punish`, `risktaking`, `challenge_competition`, `fem19`, `malebias` |

Things to know:

- In `groups_motifs.csv` eight motif codes end with an underscore (`b28e_`, `d4aa_`, `e15_`, `e15a_`, `e15b_`, `e18_`, `h36g1_`, `m81_`). In the calculations they are mapped to the codes in `motifs.csv`.
- Motif `c41` is in the motif list but is not recorded in any tradition.
- The coordinates reached the cleaned files from the repository [macleginn/mythology-queries](https://github.com/macleginn/mythology-queries) and are based on an older version of the catalogue.
- The last two tables are not used in this analysis. They are included so that the set of source files is complete.

SHA-256 checksums:

```
f77c4d08846856b486c460620a6762228591658597b7016212132423111945a5  motifs.csv
268f4c2997e934016e5039c6a05efd5a92d2c02034affa87144f9a7c7fce9ad6  groups_motifs.csv
ff51abda4896a7c423e69b9fc8de1d68f1487843e7c1e58afcf0dbdda6de5118  coords_clean.json
7359c4ba7504a76b61422b5309fbfd40ed4302fc7491e157032e4f276412ff3b  groups_concepts.csv
93bf24d0a0cdfd9238d303caabd2e7ab916677b94eb4e70c0d30a14b52170b6e  regressions.csv
```

## `derived/`: analysis outputs

All files are produced by `analysis/run_all.sh`.

### `matrix_traditions_x_motifs.csv`

923 rows and 2,564 motif columns. A cell holds 1 if the motif is recorded in the tradition and 0 otherwise.

### `traditions.csv` (923 rows)

| Column | Meaning |
|---|---|
| `tradition` | tradition name |
| `longitude`, `latitude` | coordinates |
| `n_motifs` | number of recorded motifs |
| `n_motifs_cosmology`, `n_motifs_adventure` | the same, separately for sections A–I and J–N |
| `in_analysis` | 1 if the tradition has 15 or more motifs and enters the clusters and complexes |
| `cluster_k2` … `cluster_k12` | cluster id when the traditions are divided into k clusters; see `clusters.csv` |
| `umap_x`, `umap_y` | position in the UMAP projection, from 0 to 1 |
| `nmf_01` … `nmf_12` | weight of a motif complex, from 0 to 100 (100 is the 99th percentile); see `nmf_components.csv` |
| `axis_A1` … `axis_A4` | position on the principal axes of cosmological motifs, from −100 to +100 (±100 is the 97th percentile of the absolute value); empty if the tradition has fewer than 15 such motifs |
| `axis_B1` … `axis_B4` | the same for adventure and trickster motifs |

### `clusters.csv` (22 rows)

Nodes of the cluster hierarchy. `cluster_id`; `name_ru`, `name_en`: a name given by the membership of the cluster; `created_at_k`: the step at which the cluster appears; `parent_id`: the cluster it split from (0 means all traditions); `n_traditions`; `median_share_cosmology`: median share of cosmological motifs; `indicator_motifs`: characteristic motifs with the share of traditions inside and outside the cluster; `core_traditions`: the traditions closest to the centre of the cluster.

### `cluster_membership.csv`

The same cluster membership in long format: `tradition`, `k`, `cluster_id`, `cluster_name_ru`, `cluster_name_en`.

### `motif_summary.csv` (2,564 rows)

| Column | Meaning |
|---|---|
| `motif_id`, `title` | motif code and title |
| `section` | catalogue section, a letter from A to N |
| `category` | `cosmology_etiology` for sections A–I, `adventure_trickster` for J–N |
| `n_traditions` | number of traditions with the motif, out of 923 |
| `in_analysis` | 1 if the motif is recorded in at least five of the 831 traditions |
| `atlas_x`, `atlas_y` | position of the motif in the UMAP projection by similarity of ranges, from 0 to 1 |
| `home_region` | the macro-area where the motif is recorded markedly more often, or `widespread` |
| `share_west_central_eurasia`, `share_africa_south_asia_oceania`, `share_americas_siberia` | share of the motif's occurrence falling to each of the three macro-areas, adjusted for the average frequency of motifs of the same category in the area; a motif is assigned to an area when the share is 0.6 or more |

### `nmf_components.csv` (12 rows)

Motif complexes: `component` (matches the columns `nmf_01` … `nmf_12`), `name_ru`, `name_en`, `n_traditions_weight_ge_15`, `top_motifs`, `top_traditions`.

### `axes.csv` (16 rows)

Two rows per axis (the negative and the positive pole): `axis`, `motif_set`, `variance_explained_pct`, `corr_with_log_n_motifs` (how strongly the axis is tied to how well a tradition is documented), `pole`, `top_motifs`, `top_traditions`.

### `distance_decay.csv` (15 rows)

Mean similarity of pairs of traditions by distance band: `km_from`, `km_to`, `mean_similarity_all`, `mean_similarity_cosmology`, `mean_similarity_adventure`, and the number of pairs in each band (`n_pairs_all`, `n_pairs_cosmology`, `n_pairs_adventure`).

The similarity of two traditions is the cosine between their motif vectors, where a motif's weight is ln(N / number of traditions with the motif). Only traditions with at least 10 recorded motifs of the group in question are included. Distance is measured along the great circle.
