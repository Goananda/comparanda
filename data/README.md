# Данные / Data

Все таблицы в кодировке UTF-8. Названия традиций и мотивов оставлены на английском, как в исходных файлах.
All tables are UTF-8. Tradition and motif names are in English, as in the source files.

## `source/`: исходные файлы / source files

Скачаны 16 ноября 2026 года с https://twopoints.blog/datasets/folklore/ и не изменены. Это версия каталога Ю. Е. Берёзкина и Е. Н. Дувакина из репликационного пакета Michalopoulos и Xue (2021; Harvard Dataverse, [doi:10.7910/DVN/IXOHKB](https://doi.org/10.7910/DVN/IXOHKB), CC0 1.0), очищенная Kenneth S. Reyes для записи [«The tales we tell»](https://twopoints.blog/posts/2023-04-22-the-tales-we-tell/).

| Файл | Строк | Столбцы |
|---|---|---|
| `motifs.csv` | 2 564 | `motif_id`: код мотива в каталоге (первая буква обозначает раздел A–N); `title`: название; `description`: определение мотива |
| `groups_motifs.csv` | 82 046 | первый столбец без имени: номер строки исходной таблицы; `group`: традиция; `motif_id`: мотив, записанный в этой традиции |
| `coords_clean.json` | 923 | `group`, `longitude`, `latitude`: условная точка традиции на карте |
| `groups_concepts.csv` | 5 538 | `group`, `longitude`, `latitude`, `concept` (coldness, earthquakes, farming, fishing, hunting, pastoral), `share`: расчёт автора блога, см. его запись |
| `regressions.csv` | 199 | показатели по странам, взятые автором блога из репликационного пакета: `cntry`, `lntrust_wvsavg`, `tricksters_punish`, `risktaking`, `challenge_competition`, `fem19`, `malebias` |

Что стоит знать:

- В `groups_motifs.csv` восемь кодов мотивов оканчиваются на знак подчёркивания (`b28e_`, `d4aa_`, `e15_`, `e15a_`, `e15b_`, `e18_`, `h36g1_`, `m81_`). В расчётах они приведены к кодам из `motifs.csv`.
- Мотив `c41` есть в справочнике, но не записан ни у одной традиции.
- Координаты попали в очищенные файлы из репозитория [macleginn/mythology-queries](https://github.com/macleginn/mythology-queries) и основаны на более старой версии каталога.
- Последние две таблицы в этом анализе не используются. Они приложены, чтобы набор исходных файлов был полным.

Контрольные суммы SHA-256:

```
f77c4d08846856b486c460620a6762228591658597b7016212132423111945a5  motifs.csv
268f4c2997e934016e5039c6a05efd5a92d2c02034affa87144f9a7c7fce9ad6  groups_motifs.csv
ff51abda4896a7c423e69b9fc8de1d68f1487843e7c1e58afcf0dbdda6de5118  coords_clean.json
7359c4ba7504a76b61422b5309fbfd40ed4302fc7491e157032e4f276412ff3b  groups_concepts.csv
93bf24d0a0cdfd9238d303caabd2e7ab916677b94eb4e70c0d30a14b52170b6e  regressions.csv
```

## `derived/`: результаты анализа / analysis outputs

Все файлы создаёт `analysis/run_all.sh`. All files are produced by `analysis/run_all.sh`.

### `matrix_traditions_x_motifs.csv`

923 строки, 2 564 столбца мотивов. В ячейке 1, если мотив записан в традиции, иначе 0.
Binary matrix: one row per tradition, one column per motif; 1 = the motif is recorded in the tradition.

### `traditions.csv` (923 строки / rows)

| Столбец / Column | Значение / Meaning |
|---|---|
| `tradition` | название традиции / tradition name |
| `longitude`, `latitude` | координаты / coordinates |
| `n_motifs` | число записанных мотивов / number of recorded motifs |
| `n_motifs_cosmology`, `n_motifs_adventure` | то же отдельно для разделов A–I и J–N / the same for sections A–I and J–N |
| `in_analysis` | 1, если у традиции 15 и более мотивов и она вошла в кластеры и комплексы / 1 if the tradition has 15+ motifs and enters clustering and NMF |
| `cluster_k2` … `cluster_k12` | номер кластера при делении на k кластеров, расшифровка в `clusters.csv` / cluster id at k clusters, see `clusters.csv` |
| `umap_x`, `umap_y` | положение в проекции UMAP, от 0 до 1 / UMAP coordinates scaled to 0–1 |
| `nmf_01` … `nmf_12` | вес комплекса мотивов, от 0 до 100 (100 соответствует 99-му процентилю), расшифровка в `nmf_components.csv` / NMF loading, 0–100 |
| `axis_A1` … `axis_A4` | положение на главных осях космологических мотивов, от −100 до +100 (±100 соответствует 97-му процентилю модуля); пусто, если у традиции меньше 15 таких мотивов / scores on the principal axes of A–I motifs |
| `axis_B1` … `axis_B4` | то же для приключенческих и трикстерских мотивов / the same for J–N motifs |

### `clusters.csv` (22 строки / rows)

Узлы иерархии кластеров. `cluster_id`; `name_ru`, `name_en`: название, данное по составу кластера; `created_at_k`: на каком шаге кластер появился; `parent_id`: кластер, из которого он выделился (0 означает все традиции); `n_traditions`; `median_share_cosmology`: медианная доля космологических мотивов; `indicator_motifs`: характерные мотивы с долей традиций в кластере и вне его; `core_traditions`: традиции, ближайшие к центру кластера.

Nodes of the cluster hierarchy with hand-given names, parent, size, indicator motifs (share of traditions inside / outside the cluster) and core traditions.

### `cluster_membership.csv`

Та же принадлежность к кластерам в длинном виде: `tradition`, `k`, `cluster_id`, `cluster_name_ru`, `cluster_name_en`.
Cluster membership in long format.

### `motif_summary.csv` (2 564 строки / rows)

| Столбец / Column | Значение / Meaning |
|---|---|
| `motif_id`, `title` | код и название мотива / motif code and title |
| `section` | раздел каталога, буква A–N / catalogue section letter |
| `category` | `cosmology_etiology` для разделов A–I, `adventure_trickster` для J–N |
| `n_traditions` | число традиций с мотивом из 923 / number of traditions with the motif |
| `in_analysis` | 1, если мотив записан хотя бы у пяти из 831 традиции / 1 if recorded in at least 5 of the 831 traditions |
| `atlas_x`, `atlas_y` | положение мотива в проекции UMAP по сходству ареалов, от 0 до 1 / UMAP of motifs by similarity of ranges |
| `home_region` | область, где мотив записан заметно чаще, или `widespread` / macro-area where the motif is clearly more frequent, or `widespread` |
| `share_west_central_eurasia`, `share_africa_south_asia_oceania`, `share_americas_siberia` | доля встречаемости мотива, приходящаяся на каждую из трёх областей, с поправкой на среднюю частоту мотивов этой категории в области; мотив отнесён к области при доле от 0,6 / share of the motif's prevalence falling to each macro-area after normalising by the area's average prevalence |

### `nmf_components.csv` (12 строк / rows)

Комплексы мотивов: `component` (соответствует столбцам `nmf_01` … `nmf_12`), `name_ru`, `name_en`, `n_traditions_weight_ge_15`, `top_motifs`, `top_traditions`.
The twelve NMF motif complexes with their most specific motifs and strongest traditions.

### `axes.csv` (16 строк / rows)

По две строки на ось (отрицательный и положительный полюс): `axis`, `motif_set`, `variance_explained_pct`, `corr_with_log_n_motifs` (связь оси с изученностью традиции), `pole`, `top_motifs`, `top_traditions`.
Two rows per principal axis (negative and positive pole).

### `distance_decay.csv` (15 строк / rows)

Среднее сходство пар традиций по интервалам расстояния: `km_from`, `km_to`, `mean_similarity_all`, `mean_similarity_cosmology`, `mean_similarity_adventure` и число пар в каждом интервале.

Сходство двух традиций считается как косинус между векторами мотивов, где вес мотива равен ln(N / число традиций с мотивом). В расчёт входят традиции, у которых записано не меньше 10 мотивов соответствующей группы. Расстояние считается по дуге большого круга.

Mean cosine similarity of IDF-weighted motif vectors by great-circle distance bin, for all motifs, sections A–I and sections J–N.
