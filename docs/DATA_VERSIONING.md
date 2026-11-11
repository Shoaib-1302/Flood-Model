# Data versioning

Raw rasters are too large for git. This project versions data in three layers:

1. `data_manifest.csv`   what each dataset is: source, URL, date, version, license, attribution.
2. `data_checksums.csv`  exact files: path, size, SHA-256. Regenerate with `python src/04_update_checksums.py`.
3. Git                   code, config, both manifests, and docs.

## Workflow
download -> `python src/04_update_checksums.py` -> `git add data_manifest.csv data_checksums.csv` -> commit

## Optional: DVC
For remote storage and `dvc pull` reproducibility:
```bash
pip install dvc
dvc init
dvc add data/raw data/processed     # then remove those paths from .gitignore if you want git to track the .dvc files
dvc remote add -d storage <s3-or-gdrive-or-ssh-url>
dvc push
```

## Rules
- Never edit files in `data/raw/`.
- Every dataset gets a manifest row with license and attribution (CC-BY needs credit).
- Tag releases (`git tag v0.1.0`) when a deliverable is handed over.
