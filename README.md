# Comparanda

*Comparing elements of culture across the world's traditions.*

Comparanda (Latin for "things to be compared") is an open project for comparing cultural data across many traditions with reproducible statistics and interactive maps. It starts with folklore and mythology; other kinds of cultural elements are planned.

**Interactive page:** https://goananda.github.io/comparanda/ (English by default, with a Russian version; the switch is at the top right)

Русская версия этого файла: [README.ru.md](README.ru.md)

## Study 1. Myths remember geography

An exploratory analysis of the analytical catalogue of world mythology and folklore by Yu. E. Berezkin and E. N. Duvakin in its state of 22 December 2025: 950 traditions, 3,334 motifs and 107,249 tradition–motif pairs, read from the motif pages of the authors' site. It asks which traditions resemble each other in their repertoire of motifs, which motifs travel together, and how similarity depends on distance.

### What is on the page

The home tab carries the title and a list of the sections. Each of the other tabs shows the same data in its own way.

| Tab | Method | What it shows |
|---|---|---|
| **Clusters** | LSA, Ward clustering, consensus over resampled motifs | Traditions grouped by their sets of motifs, from 2 to 12 clusters. Coordinates are not part of the calculation. Each cluster has its own colour. |
| **Tree** | the same hierarchy in full | All 874 traditions on one radial tree. Any branch can be shown on the map together with the motifs that set it apart. |
| **Axes** | principal components | The main directions of variation, separately for cosmological motifs (sections A–I) and adventure and trickster motifs (J–N). |
| **Complexes** | NMF | Twelve sets of motifs that share a range. |
| **Atlas** | UMAP of motif ranges | A map of any motif, search by code or word, and motifs with a similar range. |
| **Correlations** | phi coefficient | Pick a motif to list the motifs most often recorded in the same traditions, or a tradition to list the traditions with the most similar motifs. Two motifs give a three-colour map (only the first, only the second, both); two traditions give the motifs they share. |
| **Method** | | Data, calculations and caveats. |

A tab can be linked directly, for example `…/comparanda/#tree`. Maps are centred on the Pacific and zoom with the buttons or with Ctrl + mouse wheel. Motif titles and descriptions follow the language of the page; tradition names are in English in both versions. Pointing at a motif shows its description.

### Findings

- Clusters built without coordinates form contiguous areas on the map. With 8 clusters, 85% of a tradition's ten geographically nearest neighbours fall into its own cluster; a random partition into clusters of the same sizes would give 14%.
- The first block to split off runs from Europe and the Maghreb to India and Mongolia. Siberia and the Arctic part from North America only when the seventh cluster appears, and Chukchi, Koryak, Kamchadal and Kerek stay in one cluster with Alaska and the Eskimo traditions up to the twelfth step.
- The upper levels of the tree repeat what the 2021 tables of the catalogue gave. On the 826 traditions present in both analyses, the partitions into two to five clusters agree at 0.89–0.90 on the adjusted Rand index, and all twelve complexes are found again.
- For cosmological motifs the second principal axis sets the north (Siberia and North America) against the south (Africa, South America, southern Asia, Oceania). This is close to the contrast between the Continental Eurasian and Indo-Pacific complexes in Berezkin's work.
- Mean similarity of pairs of traditions falls from 0.22 for neighbours within 250 km to 0.023 at 12–14 thousand km. For cosmological motifs it rises again at 16–20 thousand km (0.039 against 0.030 at 10–14 thousand; 95% bootstrap interval of the difference 0.006–0.012). Adventure motifs show no such rise. The figures are in `data/derived/distance_decay.csv`.

### Caveats

- Coverage is uneven: from 1 to 1,013 motifs per tradition. A missing motif may simply not have been recorded.
- The genre mix differs. Cosmological motifs make up about 22% of the record in Europe and about 72% in Mesoamerica and the Andes. Part of the difference between clusters reflects what collectors wrote down.
- Clusters and complexes use the 874 traditions with 15 or more motifs. The other 76 traditions appear on the cluster map as hollow circles.
- Cluster boundaries depend on the similarity measure and the method. A few traditions land in a cluster centred on another continent, and ancient written traditions (Sumer, Akkad, Egypt, Ancient Greece) fall outside the Eurasian block. Australia lands in one cluster with Mesoamerica and the Andes; these traditions are recorded mostly through cosmological motifs.
- Cluster and complex names were given by their membership while preparing this work. The catalogue has no such units.
- The lists of traditions were rebuilt by script from the motif pages of the site. A blind test against the 2021 tables finds 93% of their pairs again, and some names on the pages stay unassigned (see [`data/README.md`](data/README.md)). Traditions follow the 2021 tables: groups that the catalogue now divides are kept together, coordinates come from those tables, and 30 new traditions were placed approximately.
- A single cluster tree changes noticeably when the sample of motifs changes, so the page shows a consensus of 1,200 resampled trees. Two independent halves of the resamples agree at 0.99–1.00 on the adjusted Rand index.

## What is in the repository

| Path | Contents |
|---|---|
| [`index.html`](index.html) | The interactive page as a single file. Data are embedded; the D3 library is loaded from cdnjs. |
| [`data/catalogue/`](data/catalogue) | Tables read from the catalogue pages: tradition–motif pairs, motifs, traditions, the units of the authors' list, every name found in the texts, and the names left open. |
| [`data/source/`](data/source) | The input of the analysis, made from `data/catalogue/`: motifs, tradition–motif pairs, coordinates. |
| [`data/source_2021/`](data/source_2021) | The 2021 tables behind the first version of this study, exactly as downloaded. They serve as the reference for checking the new tables. |
| [`data/derived/`](data/derived) | Analysis results as CSV: the 0/1 matrix, clusters and the full tree, complexes, axes, the distance-decay table. |
| [`data/README.md`](data/README.md) | Description of every file and column, and the provenance of the data. |
| [`analysis/`](analysis) | The scripts that computed everything, and the sources of the page. |

## How to reproduce

You need Python 3.10 or newer and Node.js 18 or newer.

```bash
pip install -r analysis/requirements.txt
bash analysis/run_all.sh
```

The script rebuilds the matrix, clusters, complexes, axes, the tables in `data/derived/` and `index.html`. It takes about fifteen minutes. To read the catalogue pages again, run `bash analysis/catalogue/run_catalogue.sh` first: it downloads about 125 MB from the authors' site at one or two requests per second (some 40 minutes) and rebuilds `data/catalogue/` and `data/source/`. Random seeds are fixed, but UMAP projections may differ slightly with other library versions. The scripts in `analysis/exploratory/` do not affect the page: they are the checks and trials behind statements in the text.

## Data sources and terms of use

- **The catalogue.** Yu. E. Berezkin, E. N. Duvakin. Thematic classification and areal distribution of folklore and mythological motifs. Analytical catalogue (in Russian). https://www.ruthenia.ru/folklore/berezkin/ The site states the licence CC BY-NC-SA 4.0. The tables in `data/catalogue/` and `data/source/` are derived from its pages (state of 22 December 2025, read on 17 November 2026) and are offered under the same licence.
- **The catalogue as tables.** Michalopoulos S., Xue M. M. (2021). Folklore. *The Quarterly Journal of Economics*, 136(4), 1993–2046. Replication package: Harvard Dataverse, https://doi.org/10.7910/DVN/IXOHKB, licence CC0 1.0.
- **Cleaned files.** Kenneth S. Reyes, Two Points blog, "The tales we tell" (2023): https://twopoints.blog/posts/2023-04-22-the-tales-we-tell/. The blog's text and images are distributed under CC BY 4.0. The files in `data/source_2021/` were downloaded from there on 16 November 2026 and have not been changed.
- **Coordinates of traditions** reached the cleaned files from the repository [macleginn/mythology-queries](https://github.com/macleginn/mythology-queries).
- **Land outline** on the maps: Natural Earth (public domain) through the world-atlas package.

If you are the author or rights holder of any of these materials and object to its being placed here, please open an issue in this repository.

## How it was made

The analysis and the page were prepared in dialogue with Claude (Anthropic). All calculations can be reproduced with the scripts in `analysis/`.
