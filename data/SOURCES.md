# Benchmark sources and update notes

Updated 18 November 2026. The survey repository uses [`catalog.json`](catalog.json) as the single source of truth for paper metadata and benchmark leaderboards. README tables are generated and validated from the same file with [`scripts/sync_catalog.py`](../scripts/sync_catalog.py).

## Benchmark tracks included (2023–2024 Baseline)

1. **Waymo-NOTR Dynamic Urban Scenes (D32 Split)** — 4D dynamic driving scene reconstruction and novel view synthesis (`PSNR / SSIM / LPIPS` on full images and `PSNR* / SSIM*` inside dynamic object bounding boxes), covering `3DGS`, `MARS`, and `EmerNeRF` (6 rows across `reconstruction` and `nvs` tracks).
2. **RealEstate10K and ACID Feed-Forward 3DGS** — Two-view generalizable feed-forward 3DGS on `RealEstate10K` and zero-shot cross-dataset generalization on `ACID` (`PSNR / SSIM / LPIPS`) for `pixelSplat` and `MVSplat` (2 rows).
3. **LERF Open-Vocabulary 3D Understanding** — Open-vocabulary 3D object localization accuracy (%) across `ramen`, `figurines`, `teatime`, `waldo_kitchen`, and `overall` under the `LangSplat` Table 1 protocol (`LSeg`, `LERF`, `LangSplat`; 3 rows).
4. **RLBench Multi-Task Manipulation** — 10-task (166-variation) language-conditioned robotic manipulation Average Success Rate (`% ↑`) comparing `PerAct`, `GNFactor`, and `ManiGaussian` (3 rows).

## Original sources used

| Benchmark / Method | Original paper | Tables / Sections used | Settings |
| --- | --- | --- | --- |
| Waymo-NOTR (D32) | [2405.20323](https://arxiv.org/abs/2405.20323) | S3Gaussian Table 1 (2023–2024 baselines) | Dynamic32 split: full-image & dynamic-box (`*`) metrics for Scene Reconstruction and NVS |
| RealEstate10K & ACID | [2410.13862](https://arxiv.org/abs/2410.13862) | DepthSplat / MVSplat Evaluations (2024 baselines) | Two-view input on RealEstate10K & zero-shot transfer to ACID |
| LERF (LangSplat) | [2312.16084](https://arxiv.org/abs/2312.16084) | LangSplat Table 1 | Open-vocabulary 3D object localization accuracy (%) |
| RLBench (10 tasks) | [2403.08321](https://arxiv.org/abs/2403.08321) | ManiGaussian Table 1 | Multi-task manipulation average success rate (%) across 10 tasks / 166 variations |

All listed values are author-reported numbers from the cited papers, not new independent evaluations.

## Comparability and protocol notes

1. **Waymo-NOTR `PSNR*` / `SSIM*`:** Asterisks denote metrics evaluated inside 2D projected bounding boxes of moving actors to isolate dynamic object quality from static background.
2. **Feed-forward 3DGS baseline variants:** For `pixelSplat`, the original RealEstate10K benchmark numbers (`25.89 / 0.858 / 0.142`) are used to maintain consistency with `MVSplat` comparative tables (the official repository later reported `26.09 / 0.863 / 0.136` after bug fixes).

## Keeping GitHub and catalog data in sync

Edit verified result entries in `data/catalog.json`, including `source`, `sourceLabel`, `note`, exact model variant, and `paperTitle` reference. Update `updated` when publishing changes, then run:

```sh
python3 scripts/sync_catalog.py --import-papers
python3 scripts/sync_catalog.py --check
```

Benchmark rows use an explicit `paperTitle` reference when the method's primary paper is in the README paper list: `sync_catalog.py` propagates the linked paper's `venue`, `paper` URL, and `code` URL, and `--check` rejects stale metadata.
