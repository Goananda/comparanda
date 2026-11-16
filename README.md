# Comparanda

*Comparing elements of culture across the world's traditions.*

Comparanda (Latin for "things to be compared") is an open project for comparing cultural data across many traditions with reproducible statistics and interactive maps. It starts with folklore and mythology; other kinds of cultural elements are planned.

**Interactive page:** https://goananda.github.io/comparanda/ (English by default, with a Russian version; the switch is at the top right)

Русская версия этого файла: [README.ru.md](README.ru.md)

## Study 1. Myths remember geography

An exploratory analysis of the analytical catalogue of world mythology and folklore by Yu. E. Berezkin and E. N. Duvakin: 923 traditions, 2,563 motifs and 82,046 tradition–motif pairs. It asks which traditions resemble each other in their repertoire of motifs, which motifs travel together, and how similarity depends on distance.

### What is on the page

1. **Culture clusters.** Hierarchical clustering of traditions by their sets of motifs, from 2 to 12 clusters. Coordinates are not part of the calculation. Each cluster has its own colour.
2. **Motif complexes.** Twelve sets of motifs that share a range (non-negative matrix factorisation).
3. **Principal axes.** Principal components, separately for cosmological motifs (catalogue sections A–I) and for adventure and trickster motifs (J–N).
4. **Similarity and distance.** A map of how similar any tradition is to all the others, and curves of how similarity falls with distance.
5. **Motif atlas.** A map of any motif, search by code or word, and motifs with a similar range.

Maps are centred on the Pacific and zoom with the buttons or with Ctrl + mouse wheel. Motif and tradition names are in English in both language versions, as in the source files.

### Findings

- Clusters built without coordinates form contiguous areas on the map. With 8 clusters, 88% of a tradition's ten geographically nearest neighbours fall into its own cluster; a random partition into clusters of the same sizes would give 15%.
- The first block to split off runs from Europe and the Maghreb to India and Mongolia. Siberia and the Arctic part from North America only at the sixth step, and Chukchi, Koryak, Itelmen and Kerek stay in one cluster with Alaska and the Eskimo traditions up to the twelfth step.
- For cosmological motifs the second principal axis sets the north (Siberia and North America) against the south (Africa, South America, southern Asia, Oceania). This is close to the contrast between the Continental Eurasian and Indo-Pacific complexes in Berezkin's work.
- Mean similarity of pairs of traditions falls from 0.22 for neighbours within 250 km to 0.024 at 12–14 thousand km. For cosmological motifs it rises again at 16–20 thousand km (0.040 against 0.032 at 10–14 thousand; 95% bootstrap interval of the difference 0.005–0.011). Adventure motifs show no such rise.

### Caveats

- Coverage is uneven: from 2 to 598 motifs per tradition. A missing motif may simply not have been recorded.
- The genre mix differs. Cosmological motifs make up about 20% of the record in Europe and about 72% in Mesoamerica. Part of the difference between clusters reflects what collectors wrote down.
- Clusters and complexes use the 831 traditions with 15 or more motifs. The other 92 traditions appear on the cluster map as hollow circles.
- Cluster boundaries depend on the similarity measure and the method. A few traditions land in a cluster centred on another continent, and ancient written traditions (Sumer, Akkad, Egypt, Ancient Greece) fall outside the Eurasian block.
- Cluster and complex names were given by their membership while preparing this work. The catalogue has no such units.
- This is the version of the catalogue cleaned in 2023, and the coordinates of traditions come from an older version.

## What is in the repository

| Path | Contents |
|---|---|
| [`index.html`](index.html) | The interactive page as a single file. Data are embedded; the D3 library is loaded from cdnjs. |
| [`data/source/`](data/source) | Source files exactly as downloaded: motifs, tradition–motif pairs, coordinates, and two derived tables by the blog author. |
| [`data/derived/`](data/derived) | Analysis results as CSV: the 0/1 matrix, clusters, complexes, axes, the distance-decay table. |
| [`data/README.md`](data/README.md) | Description of every file and column, and the provenance of the data. |
| [`analysis/`](analysis) | The scripts that computed everything, and the sources of the page. |

## How to reproduce

You need Python 3.10 or newer and Node.js 18 or newer.

```bash
pip install -r analysis/requirements.txt
bash analysis/run_all.sh
```

The script rebuilds the matrix, clusters, complexes, axes, the tables in `data/derived/` and `index.html`. It takes about ten minutes. Random seeds are fixed, but UMAP projections may differ slightly with other library versions. The scripts in `analysis/exploratory/` do not affect the page: they are the checks and trials behind statements in the text.

## Data sources and terms of use

- **The catalogue.** Yu. E. Berezkin, E. N. Duvakin. Thematic classification and areal distribution of folklore and mythological motifs. Analytical catalogue (in Russian). https://www.ruthenia.ru/folklore/berezkin/
- **The catalogue as tables.** Michalopoulos S., Xue M. M. (2021). Folklore. *The Quarterly Journal of Economics*, 136(4), 1993–2046. Replication package: Harvard Dataverse, https://doi.org/10.7910/DVN/IXOHKB, licence CC0 1.0.
- **Cleaned files.** Kenneth S. Reyes, Two Points blog, "The tales we tell" (2023): https://twopoints.blog/posts/2023-04-22-the-tales-we-tell/. The blog's text and images are distributed under CC BY 4.0. The files in `data/source/` were downloaded from there on 16 November 2026 and have not been changed.
- **Coordinates of traditions** reached the cleaned files from the repository [macleginn/mythology-queries](https://github.com/macleginn/mythology-queries).
- **Land outline** on the maps: Natural Earth (public domain) through the world-atlas package.

If you are the author or rights holder of any of these materials and object to its being placed here, please open an issue in this repository.

## How it was made

The analysis and the page were prepared in dialogue with Claude (Anthropic). All calculations can be reproduced with the scripts in `analysis/`.
