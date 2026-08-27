# LLMResponseClassification

## Project layout

```
data/                     gitignored — local dataset only (see data/README.md)
  raw/                    source data as received
  processed/              output of data_optimization, ready for training
packages/                 uv workspace members
  data_analysis/          exploration/profiling of the raw dataset
  data_optimization/      cleaning/transformation ahead of model training
  model_training/         (future phase — not created yet)
```

This repo is a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/): each folder under `packages/` is an independent, installable Python package sharing one lockfile. Add a new package by dropping a directory with its own `pyproject.toml` under `packages/` — no root config changes needed, since `packages/*` is already declared as a workspace member pattern in the root `pyproject.toml`.

## Setup

```bash
uv sync
```

Then populate `data/raw/` locally (it is not tracked by git) before running the analysis or optimization packages.