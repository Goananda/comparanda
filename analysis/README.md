# Analysis scripts

Run everything with `bash analysis/run_all.sh` from the repository root (about fifteen minutes). Intermediate files go to `build/`, which is not part of the repository. The input in `data/source/` is made from the catalogue's site by `bash analysis/catalogue/run_catalogue.sh`, described at the end of this file.

Русская версия: [README.ru.md](README.ru.md)

| Step | File | What it does |
|---|---|---|
| 1 | `prep.py` | Builds the 0/1 tradition-by-motif matrix from `data/source/`. |
| 2 | `clus.py` | TF-IDF weights, 30 latent dimensions (LSA, exact decomposition), Ward clustering, and a consensus over 1,200 resamples of motifs: the final tree is a Ward hierarchy on how often two traditions fall into one cluster. Prints the agreement between two independent halves of the resamples, the geographic coherence of the clusters, and the agreement with k-means and average linkage. This step takes about eight minutes. |
| 3 | `nmf.py` | Non-negative matrix factorisation into 12 motif complexes, the best of six initialisations. |
| 4 | `embed.py` | UMAP projections of traditions and motifs, and a stability check for NMF. |
| 5 | `export.py` | Gathers everything the page needs into `data.json`: the cluster hierarchy with names and characteristic motifs, the complexes, the principal axes, the decay of similarity with distance, the motif atlas. |
| 6 | `make_tables.py` | Writes the tables in `data/derived/`. |
| 7 | `build_geo.mjs` | Projects the land outline and the coordinates of traditions (Equal Earth projection centred on 153° E). |
| 8 | `site/build.py` | Assembles `index.html` from `site/src/` and the data. |

Things to know:

- Clusters and complexes use traditions with 15 or more motifs (874 of 950) and motifs recorded in at least five of them (3,102).
- Why a consensus: one Ward tree on all motifs agrees with a tree on resampled motifs at only 0.41–0.80 (adjusted Rand index), and with the randomised decomposition used earlier it also depended on the random seed. Two independent consensus trees of 600 resamples agree at 0.86–0.92. `exploratory/consensus_conv.py` shows how the agreement grows with the number of resamples.
- Cluster names are set in `export.py`, in English and Russian. A cluster is recognised by the anchor traditions it contains (twelve anchors, one per smallest cluster), so the names survive small shifts in membership. If the data change so much that a cluster holds an unforeseen set of anchors, the log of `export.py` flags it with `CHECK` and a name has to be added. Complexes are matched to those of the 2021 analysis by the correlation of their tradition weights (`reference/`).
- The principal axes are computed separately for sections A–I and J–N, on traditions with 15 or more motifs of the group and motifs recorded in at least ten of them.
- Pointing at a motif shows its description; the Atlas shows it in full. Titles and descriptions travel in `data/source/motifs.csv` in both languages (`title`, `description`, `title_ru`, `description_ru`) and are shown in the language of the page. [`data/README.md`](../data/README.md) explains how the two versions were put together. The texts add about 1.6 MB to `index.html`.
- The Correlations tab computes its coefficients in the browser from the tradition–motif pairs embedded in the page.
- `exploratory/` holds the trials and checks behind statements on the page: a comparison of methods for the axes, cluster membership, similarity between clusters, the contribution of pairs of regions to the far distance bands. They do not affect the build.

## Languages of the page

The page is in English by default and has a Russian version; the choice is kept in the browser. Motif titles and descriptions follow the language of the page; tradition names stay in English.

- The frame of the page and the original views are in `site/src/body.html`, `app.js` and `style.css`. Every newer view is a pair of files in `site/src/views/` (`tree.html` and `tree.js`, `correlations.html` and `correlations.js`), inserted by `build.py`. Views are built when their tab is first opened.
- Static text is written as pairs of elements marked `lang="en"` and `lang="ru"`; a CSS rule hides the language that is not selected.
- Text produced by scripts (captions, tooltips, notes) lives in the `TX` dictionary at the top of `site/src/app.js`; each view file adds its own strings to it. The captions of the principal axes are in `TXT` inside `initAxes`.
- Names of clusters and complexes in both languages come from `export.py`.

## Cluster colours

Each of the twelve clusters has its own colour, and all clusters are drawn as circles. The colours are the variables `--k0` … `--k11` in `site/src/style.css`, with separate values for the light and the dark theme. The colour slot of every node of the hierarchy is the `col` field set in `export.py`: when a cluster splits, one part keeps the colour and the other gets a new one, so the map changes as little as possible from step to step.

`exploratory/check_palette.py` prints the closest pairs of colours. In both themes every pair differs by at least 17 for normal vision and 8.8 under simulated red-green colour-vision deficiency (Euclidean distance in OKLab ×100). Twelve hues cannot all be told apart by colour alone under every condition, so the legend, the direct labels on the similarity plot and the tooltips name the cluster as well.

## Reading the catalogue: `catalogue/`

`bash analysis/catalogue/run_catalogue.sh` downloads every motif page of the catalogue (about 3,500 pages, 125 MB, one or two requests per second) and rebuilds `data/catalogue/` and `data/source/`. The pages themselves are not kept in the repository.

| Step | File | What it does |
|---|---|---|
| 1 | `scripts/fetch_all.py` | Downloads the motif pages listed in the index of the site; pages already on disk are skipped. |
| 2 | `scripts/parse_areas.py` | Reads the page «Этносы и ареалы»: the numbered units of the authors' list, by area. `manual/extra_units.tsv` adds six traditions that are named on many motif pages but are absent from that list. |
| 3 | `scripts/parse_pages.py` | Reads every motif page: title, definition, area codes, the authors' list of groups, and every name that opens a text, with its region, remark in brackets and cited publications. The name is normally underlined; a text without underlining is taken when it opens with a name that is underlined elsewhere in the same region. Area codes are read in any of the spellings found in the headings. Names inside comparisons («Ср.») and inside abstracts are marked and not counted; names in other brackets count. |
| 4 | `scripts/match_units.py` | Matches each name to a unit of the authors' list, first inside its own area. `manual/names.tsv` holds the rules written by hand; `manual/regions.tsv` the variants of region headings. |
| 5 | `scripts/match_old.py` | Links units to the traditions of the 2021 tables with `manual/unit_old.tsv` (every link was checked by hand). |
| 6 | `scripts/assemble.py` | Decides the tradition of every entry, applies the rules stated in motif definitions, adds the authors' lists, compares the result with the 2021 table (`--cv` runs the five-fold test) and writes the tables. |
| 7 | `scripts/motif_texts.py` | Sets the English and the Russian text of every motif: takes the entry of the site's English list (or of the 2021 table) that describes the motif, adds the translations kept in `manual/`, and removes the index numbers from the titles of the Russian pages. |
| 8 | `scripts/make_source.py` | Writes `data/source/` in the layout the analysis reads. |

`manual/english_fixes.tsv` names the entry of the English list that describes a motif where the codes differ, or says that the Russian page is to be used; `manual/text_choices.tsv` lists the motifs whose English entry and Russian page were compared with the texts, with the counts behind each choice; `manual/en_from_ru.tsv` and `manual/ru_from_en.tsv` hold the translations of motif texts, `manual/text_fixes.tsv` single corrected fields, and `manual/new_units_en.tsv` the English names and approximate coordinates of units that the 2021 tables did not have. `checks/` contains the scripts used to look for mistakes: agreement with the 2021 table by tradition (`per_trad.py`), traditions that resemble another tradition more than their namesake (`content_match.py`), the names behind missing or added pairs (`diag_missing.py`, `gain_names.py`, `area_matrix.py`), the area codes of headings against the areas of the texts (`heading_areas.py`), and the comparison of the English entries with the Russian pages (`version_similarity.py` for the screen, `text_support.py` for the share of texts that contain the words specific to each version).
