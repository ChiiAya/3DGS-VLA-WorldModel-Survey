# Benchmark sources and update notes

Updated 21 November 2026. The survey repository uses [`catalog.json`](catalog.json) as the single source of truth for paper metadata and benchmark leaderboards. README tables are generated and validated from the same file with [`scripts/sync_catalog.py`](../scripts/sync_catalog.py).

## Benchmark tracks included (2023–2026)

1. **Waymo-NOTR Dynamic Urban Scenes (D32 Split)** — 4D dynamic driving scene reconstruction and novel view synthesis (`PSNR / SSIM / LPIPS` on full images and `PSNR* / SSIM*` inside dynamic object bounding boxes), covering `3DGS`, `MARS`, `EmerNeRF`, and `S3Gaussian` (8 rows across `reconstruction` and `nvs` tracks).
2. **Waymo Novel Trajectory Synthesis** — lane-change novel-trajectory synthesis evaluated with `FID (↓)`, comparing 4DGS baselines (`Deformable-GS`, `PVG`, `S3Gaussian`) against the same backbones augmented by the `DriveDreamer4D` driving world model (6 rows).
3. **RealEstate10K and ACID Feed-Forward 3DGS** — Two-view generalizable feed-forward 3DGS on `RealEstate10K` and zero-shot cross-dataset generalization on `ACID` (`PSNR / SSIM / LPIPS`) for `pixelSplat`, `MVSplat`, and `DepthSplat` (3 rows).
4. **LERF Open-Vocabulary 3D Understanding** — Two isolated protocols on the LERF dataset: object localization accuracy (%) across `ramen`, `figurines`, `teatime`, `waldo_kitchen`, and `overall` under the `LangSplat` Table 1 protocol (`LSeg`, `LERF`, `LangSplat`), and the `LangSplatV2` Table 2 protocol reporting localization accuracy and semantic segmentation mIoU (5 rows across two tracks).
5. **RLBench Multi-Task Manipulation** — 10-task (166-variation) language-conditioned robotic manipulation Average Success Rate (`% ↑`) comparing `PerAct`, `GNFactor`, and `ManiGaussian` (3 rows).

## Original sources used

| Benchmark / Method | Original paper | Tables / Sections used | Settings |
| --- | --- | --- | --- |
| Waymo-NOTR (D32) | [2405.20323](https://arxiv.org/abs/2405.20323) | S3Gaussian Table 1 | Dynamic32 split: full-image & dynamic-box (`*`) metrics for Scene Reconstruction and NVS |
| Waymo Novel Trajectory Synthesis | [2410.13571](https://arxiv.org/abs/2410.13571) | DriveDreamer4D lane-change benchmark | FID (↓) for 4DGS backbones with and without world-model-augmented training |
| RealEstate10K & ACID | [2410.13862](https://arxiv.org/abs/2410.13862), [2403.14627](https://arxiv.org/abs/2403.14627) | DepthSplat / MVSplat evaluations | Two-view input on RealEstate10K & zero-shot transfer to ACID |
| LERF (LangSplat) | [2312.16084](https://arxiv.org/abs/2312.16084) | LangSplat Table 1 | Open-vocabulary 3D object localization accuracy (%) |
| LERF (LangSplatV2) | [2507.07136](https://arxiv.org/abs/2507.07136) | LangSplatV2 Table 2 | Localization accuracy (%) and semantic segmentation mIoU (%) on Ramen / Figurines / Teatime / Kitchen |
| RLBench (10 tasks) | [2403.08321](https://arxiv.org/abs/2403.08321) | ManiGaussian Table 1 | Multi-task manipulation average success rate (%) across 10 tasks / 166 variations |

All listed values are author-reported numbers from the cited papers, not new independent evaluations.

## Comparability and protocol notes

1. **Waymo-NOTR `PSNR*` / `SSIM*`:** Asterisks denote metrics evaluated inside 2D projected bounding boxes of moving actors to isolate dynamic object quality from static background.
2. **Feed-forward 3DGS baseline variants:** For `pixelSplat`, the original RealEstate10K benchmark numbers (`25.89 / 0.858 / 0.142`) are used to maintain consistency with `MVSplat` comparative tables (the official repository later reported `26.09 / 0.863 / 0.136` after bug fixes).
3. **LERF protocol isolation:** The `LangSplat` Table 1 track and the `LangSplatV2` Table 2 track are kept separate. Do not merge them into one ranking — the two protocols differ in the evaluated object set and metric definition.
4. **Waymo Novel Trajectory rows:** Baseline rows reproduce numbers reported *inside* the DriveDreamer4D paper, not the original baseline papers. `added: false` marks rows that are re-reported baselines rather than numbers contributed by the row's own method.

## Keeping GitHub and catalog data in sync

Edit verified result entries in `data/catalog.json`, including `source`, `sourceLabel`, `note`, exact model variant, and `paperTitle` reference. Update `updated` when publishing changes, then run:

```sh
python3 scripts/sync_catalog.py --import-papers
python3 scripts/sync_catalog.py --check
```

Benchmark rows use an explicit `paperTitle` reference when the method's primary paper is in the README paper list: `sync_catalog.py` propagates the linked paper's `venue`, `paper` URL, and `code` URL, and `--check` rejects stale metadata.
