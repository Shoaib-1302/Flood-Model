# Flood Model (AGT project)

Flood risk and inundation modelling pipeline. See `project.yaml` for metadata and `docs/` for decisions.

## Setup
```bash
./setup.sh                     # venv + dependencies + environment check + git init
# or with conda:  conda env create -f environment.yml && conda activate floodenv
```

## AGT-309 workflow
1. Edit `config.yaml` (AOI bbox in EPSG:4326, ISO3 country code).
2. `python src/01_define_aoi.py`      AOI in 4326 + UTM, with buffer
3. `python src/02_download_admin.py`  administrative boundaries, clipped
4. `python src/03_check_env.py`       verify dependencies
5. `python src/04_update_checksums.py` data versioning manifest
6. Fill `docs/AOI_DECISION.md`, commit.

## Directory tree
```
data/raw/        untouched downloads (admin, dem, rainfall, landcover_soil, population, infrastructure, validation)
data/processed/  clipped / reprojected / derived data (aoi, admin, dem, rainfall, runoff, exposure)
models/          hydrology/ and hydraulics/ model setups and runs
outputs/         maps, reports, dashboard
src/             numbered pipeline scripts
docs/            decisions, methodology, data versioning
```

## Rules
Raw data is read-only. Compute in the project UTM CRS. Every dataset gets a manifest row. Scripts read `config.yaml`.
