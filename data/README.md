# data/

Local dataset storage. Nothing under this directory is committed (see root `.gitignore`) except this file and the folder placeholders.

- `raw/` — source data as received, untouched.
- `processed/` — output of `data_optimization`, ready to be consumed by the future model-training package.

Populate `raw/` locally before running the analysis/optimization packages.
