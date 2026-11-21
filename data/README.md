# Data

All tables are UTF-8. Tradition names are in English; motif titles and descriptions are given in English and in Russian.

Русская версия: [README.ru.md](README.ru.md)

## `catalogue/`: tables read from the catalogue pages

The catalogue of Yu. E. Berezkin and E. N. Duvakin is published as one web page per motif: https://www.ruthenia.ru/folklore/berezkin/ (licence stated on the site: CC BY-NC-SA 4.0). These tables were made from its state of 22 December 2025, read on 17 November 2026 by the scripts in [`analysis/catalogue/`](../analysis/catalogue) and compared with the site again on 21 November 2026 (every page still carried the date of 26 December 2025). On a motif page a text normally starts with an underlined name of an ethnic group (about 1,200 texts name the group without underlining); many pages also carry the authors' own list of groups. The scripts match these names to the catalogue's list of ethnic groups («Этносы и ареалы», 1,013 numbered units) and then to the traditions of the 2021 tables.

| File | Rows | Contents |
|---|---|---|
| `pairs.csv` | 112,280 | Tradition–motif pairs. `tradition`; `motif_id`; `tradition_status` (`old`: a tradition of the 2021 tables, `old-merged`: two of them that the catalogue now treats as one, `new`); `in_old_pairs` (1 or 0 if the motif is in the 2021 table, empty otherwise); `motif_in_old_database`; `motif_in_digital_db` (1 if the heading of the motif lists areas outside brackets, which is how the catalogue marks motifs of its digital database); `n_entries`; `names_on_page`; `units`; `how` (the kind of evidence, see below) |
| `motifs.csv` | 3,488 | `motif_id`; `title_en`, `description_en`: the English version, with `title_en_source` and `description_en_source` (`site (English list)`: the entry of the site's English list under the same code; `site (English list, entry …)`: an entry that the list keeps under another code; `old database`: the 2021 table; `translated from Russian`); `title_ru`, `description_ru`: the Russian version, with `title_ru_source` and `description_ru_source` (`translated from English` or `site`); `title_ru_site`, `definition_ru_site`: the Russian page as it stands on the site; `in_old_database`; `in_digital_db`; `n_traditions`; `n_traditions_old`; `n_names_on_page`; `n_names_open`; `n_compare_entries`; `includes` (motifs whose traditions are added by a rule stated in the definition); `area_codes` (the codes of the heading written out one by one, bracketed ones in brackets); `n_areas`; `url` |
| `traditions.csv` | 954 | `tradition`; `status`; `n_motifs` (motifs of the digital database); `n_motifs_all_pages`; `n_motifs_old`; `longitude`, `latitude`; `coordinates_source` (`old database`, or `assigned here, approximate` for new traditions); `areas`; `units` |
| `units.csv` | 1,019 | The units of the authors' list and six traditions added here (numbers `x1`, `x2`, see below): `unit_id` (area and number), `area_ru`, `no`, `unit_ru`, `in_table` (0 for units marked as having too little data), `tradition`, `relation_to_old` (`same`, `split`, `merge`, `new`, `not-in-table`), `negligible_data`, `n_entries` |
| `entries.csv` | 144,708 | Every name that opens a text (underlined on the site, or recognised without underlining): `motif_id`, `order`, `region`, `name`, `qualifier`, `kind` (`main`, `compare`, `abstract`), `tradition`, `resolution`, `unit_id`, `unit_candidates` |
| `open_names.csv` | 332 | Names in the texts that stayed unresolved or ambiguous, with the number of entries, examples of motifs and the candidates |
| `learned_rules.csv` | 55 | Rules taken from the 2021 table: the usual tradition of an ambiguous name, and the tradition of a name that the authors' list does not contain |

Things to know:

- **How a pair is established** (`how`): `area`, `area-weak`, `global`, `global-weak`: the name matches one unit in its own area or elsewhere, exactly or loosely; `manual`: a rule in `analysis/catalogue/manual/names.tsv`; `group`: all candidate units belong to one tradition; `summary`, `source`, `default`, `old-table`: an ambiguous name settled by the authors' list on the same page, by the cited publication, by its usual meaning, or by the 2021 table; `learned`: a rule from `learned_rules.csv`; `summary-list`: the tradition stands only in the authors' list; `included-from-…`: added by a rule in the motif definition.
- **Check against the 2021 tables.** The two sources share 2,548 motifs with 81,659 pairs in the 2021 table. Matching by the site alone finds 88.8% of them; with rules learned from the 2021 table and tested on motifs not used for learning (five-fold), 93.0%; the final tables, where remaining ambiguity is settled by the 2021 table, 94.3%. Half of the traditions with 15 or more old pairs recover at least 95% of them. The new tables add 14,237 pairs on shared motifs and 21,009 pairs on motifs that the 2021 table lacks.
- **Which motifs belong to the digital database.** The heading of a motif page lists the codes of the areas where the authors' database has the motif; codes in brackets, or no codes at all, mean that the motif is not used in the authors' counts. The index of the site has 3,489 entries for 3,488 pages (K37B stands there twice, once under a general title that has no page of its own). 3,334 pages carry codes outside brackets, while the introduction of the site gives 3,328 motifs. Six headings write the codes without the leading dot (B6A, B47A, E30A, K27ZZ2, K99A2, N25); they are read as codes here, which may account for the difference.
- **Which texts count.** Names in paragraphs or brackets marked «Ср.» (compare) are not counted. The headings support this reading: of the areas that have only such texts, 960 stand in brackets in the heading, 353 are absent from it and 42 are listed as ordinary areas. Names in other brackets do count («включая …», «то же у …»).
- **Headings against texts.** Of the 34,813 area codes in the headings of database motifs, 770 (2.2%) have no counted text on the page: 503 leave no trace there, 195 are named only in the authors' list and 55 have compared texts only. Another 843 areas have texts but are missing from the heading; in 28 of these cases the texts stand under «Боливия – Гуапоре» while the heading lists Montaña – Juruá (66), and in 33 the heading still carries the former code 58 for texts that now stand under Guiana. The tables follow the texts.
- **Where the two disagree,** part of the cause seems to lie in the revision of the catalogue since 2021: some units look divided or redefined (the Oto-Manguean groups of Oaxaca are an example), and two columns of the 2021 table, Muisca and Yukpa, do not match the names that stand on the pages now.
- **What stays open.** 639 entries (332 different names, 0.5% of the names that open a text) could not be assigned: groups that the page itself leaves unspecified («даяки, группа не указана»), names that fit two traditions with nothing on the page to choose by, and labels of archaeological finds or written sources that the list of units lacks. In addition, a name that stands only in the authors' list and merely resembles the name of a unit is not counted when the page has texts of its own. The lists are therefore slightly incomplete.
- **Traditions follow the 2021 tables.** The catalogue now divides some groups into several units (Russians into six, Chinese folklore into twelve, Yakut into four). They are kept together here, because the texts often do not say which part is meant. Twenty-four units have no counterpart in the 2021 tables and are new traditions. Six more traditions are named in the texts of many motif pages but are absent from the list of units: Transylvanian Saxons (218 motifs), Zaza (57), Nawar (42), Maldives (31), Byzantium (31) and Kokna (26). The 2021 table does not count their texts under a neighbouring tradition, so they are added here as traditions of their own (`analysis/catalogue/manual/extra_units.tsv`), with approximate coordinates.
- **Motif texts.** The English version takes titles and descriptions from the English list on the site (`eng.html`) and, for motifs the list lacks, from the 2021 table. The list is older than the Russian pages, so every entry was compared with the present page of the same code (through a Russian translation and a word-overlap score, then by reading). 34 entries stand under an earlier number of the motif and were moved to the present one. For 788 motifs of the analysis there is no usable English entry: the list lacks the motif, repeats the text of a neighbour, or describes a motif that now has another number. Their English text was translated for these tables from the Russian page. Where the English entry and the Russian page word the same motif differently, the two were set against the texts of the page: the 240 pairs that differ most were read in full, together with some 580 pairs of titles, and for disputed points the texts that mention each element were counted. In 42 motifs the Russian page proved closer to the texts (its definition is wider, narrower or about another episode); its text is shown in both languages. These cases, and nine checked ones where the English entry was kept, are listed with the counts in `analysis/catalogue/manual/text_choices.tsv`. The other pairs were screened by a word-overlap score only. The Russian version is a translation of the English one wherever the English text is the authors' own (2,504 titles and 2,500 descriptions of the analysis) and the text of the Russian page elsewhere, with the index numbers after the title removed. 27 motifs have no description. The translations were made by a language model (Claude) and have not been reviewed by the authors of the catalogue. The decisions are recorded in `analysis/catalogue/manual/english_fixes.tsv`, `text_choices.tsv` and `text_fixes.tsv`, the translations in `en_from_ru.tsv` and `ru_from_en.tsv`.

## `source/`: input of the analysis

Made from `catalogue/` by `analysis/catalogue/scripts/make_source.py`, in the layout that the analysis scripts read. Only motifs of the digital database are kept.

| File | Rows | Columns |
|---|---|---|
| `motifs.csv` | 3,334 | `motif_id`: motif code in the catalogue (the first letter is the section, A–N); `title`, `description`: the English version; `title_ru`, `description_ru`: the Russian version; `title_source`, `description_source`: where the English text comes from (see `motifs.csv` of `catalogue/` above) |
| `groups_motifs.csv` | 107,249 | unnamed first column: row number; `group`: tradition; `motif_id`: a motif recorded in that tradition |
| `coords_clean.json` | 950 | `group`, `longitude`, `latitude`: a nominal point for the tradition on the map |

SHA-256 checksums:

```
d843bba4af4fcc934c50ec47f95f452417e1d7c1cdee98d92460e9fd1c4a0e60  motifs.csv
d7d0bead60ed09685126c5a4e4b5e65e3691a09cc046e32c889d57951c0e7cc7  groups_motifs.csv
30588c0305224329124f3d6347a2bfa85261d2902573f57d570ba694fed3256a  coords_clean.json
```

## `source_2021/`: the 2021 tables

The tables behind the first version of this study, now used as the reference for checking `catalogue/`. Downloaded on 16 November 2026 from https://twopoints.blog/datasets/folklore/ and left unchanged. This is the version of the catalogue by Yu. E. Berezkin and E. N. Duvakin from the replication package of Michalopoulos and Xue (2021; Harvard Dataverse, [doi:10.7910/DVN/IXOHKB](https://doi.org/10.7910/DVN/IXOHKB), CC0 1.0), cleaned by Kenneth S. Reyes for the post ["The tales we tell"](https://twopoints.blog/posts/2023-04-22-the-tales-we-tell/).

| File | Rows | Columns |
|---|---|---|
| `motifs.csv` | 2,564 | `motif_id`: motif code in the catalogue (the first letter is the section, A–N); `title`: motif title; `description`: motif definition |
| `groups_motifs.csv` | 82,046 | unnamed first column: row number of the original table; `group`: tradition; `motif_id`: a motif recorded in that tradition |
| `coords_clean.json` | 923 | `group`, `longitude`, `latitude`: a nominal point for the tradition on the map |
| `groups_concepts.csv` | 5,538 | `group`, `longitude`, `latitude`, `concept` (coldness, earthquakes, farming, fishing, hunting, pastoral), `share`: computed by the blog author, see his post |
| `regressions.csv` | 199 | country-level indicators taken by the blog author from the replication package: `cntry`, `lntrust_wvsavg`, `tricksters_punish`, `risktaking`, `challenge_competition`, `fem19`, `malebias` |

Things to know:

- In `groups_motifs.csv` eight motif codes end with an underscore (`b28e_`, `d4aa_`, `e15_`, `e15a_`, `e15b_`, `e18_`, `h36g1_`, `m81_`). When the tables are compared they are mapped to the codes in `motifs.csv`.
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

950 rows and 3,334 motif columns. A cell holds 1 if the motif is recorded in the tradition and 0 otherwise.

### `traditions.csv` (950 rows)

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

### `motif_summary.csv` (3,334 rows)

| Column | Meaning |
|---|---|
| `motif_id`, `title` | motif code and title |
| `section` | catalogue section, a letter from A to N |
| `category` | `cosmology_etiology` for sections A–I, `adventure_trickster` for J–N |
| `n_traditions` | number of traditions with the motif, out of 950 |
| `in_analysis` | 1 if the motif is recorded in at least five of the 874 traditions |
| `atlas_x`, `atlas_y` | position of the motif in the UMAP projection by similarity of ranges, from 0 to 1 |
| `home_region` | the macro-area where the motif is recorded markedly more often, or `widespread` |
| `share_west_central_eurasia`, `share_africa_south_asia_oceania`, `share_americas_siberia` | share of the motif's occurrence falling to each of the three macro-areas, adjusted for the average frequency of motifs of the same category in the area; a motif is assigned to an area when the share is 0.6 or more |

### `nmf_components.csv` (12 rows)

Motif complexes: `component` (matches the columns `nmf_01` … `nmf_12`), `name_ru`, `name_en`, `n_traditions_weight_ge_15`, `top_motifs`, `top_traditions`.

### `axes.csv` (16 rows)

Two rows per axis (the negative and the positive pole): `axis`, `motif_set`, `variance_explained_pct`, `corr_with_log_n_motifs` (how strongly the axis is tied to how well a tradition is documented), `pole`, `top_motifs`, `top_traditions`.

### `distance_decay.csv` (15 rows)

Mean similarity of pairs of traditions by distance band: `km_from`, `km_to`, `mean_similarity_all`, `mean_similarity_cosmology`, `mean_similarity_adventure`, and the number of pairs in each band (`n_pairs_all`, `n_pairs_cosmology`, `n_pairs_adventure`).

### `cluster_tree.csv` (865 rows)

The whole consensus hierarchy behind the clusters, one row per merge: `merge` (`#1` … `#865`, in the order of merging), `child_a`, `child_b` (a tradition name or an earlier merge), `height`, `n_traditions`.

## Similarity

The similarity of two traditions is the cosine between their motif vectors, where a motif's weight is ln(N / number of traditions with the motif). Only traditions with at least 10 recorded motifs of the group in question are included. Distance is measured along the great circle.
