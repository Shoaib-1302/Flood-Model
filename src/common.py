"""Shared helpers: config, CRS resolution, manifest and checksum logging."""
import csv
import hashlib
from datetime import date, datetime
from pathlib import Path
import yaml
import geopandas as gpd
from shapely.geometry import box

ROOT = Path(__file__).resolve().parents[1]


def load_config():
    with open(ROOT / "config.yaml") as f:
        return yaml.safe_load(f)


def path(cfg, key, *sub):
    p = ROOT / cfg["paths"][key]
    for s in sub:
        p = p / s
    p.mkdir(parents=True, exist_ok=True)
    return p


def aoi_bbox_gdf(cfg):
    w, s, e, n = cfg["aoi"]["bbox_4326"]
    return gpd.GeoDataFrame({"name": [cfg["aoi"]["name"]]}, geometry=[box(w, s, e, n)],
                            crs=cfg["crs"]["storage"])


def project_crs(cfg):
    """Return the target projected CRS (auto-selects the UTM zone if set to 'auto')."""
    crs = cfg["crs"]["project"]
    if str(crs).lower() == "auto":
        return aoi_bbox_gdf(cfg).estimate_utm_crs().to_string()
    return crs


MANIFEST_FIELDS = ["dataset", "source", "url", "date_downloaded", "version", "resolution",
                   "crs", "license", "attribution", "used_by", "notes"]


def log_manifest(cfg, **row):
    """Add or update one dataset row in data_manifest.csv (keyed by 'dataset')."""
    mpath = ROOT / cfg["paths"]["manifest"]
    rows = []
    if mpath.exists():
        with open(mpath, newline="") as f:
            rows = list(csv.DictReader(f))
    row.setdefault("date_downloaded", date.today().isoformat())
    rows = [r for r in rows if r["dataset"] != row["dataset"]] + [row]
    with open(mpath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})


def sha256(file, chunk=1 << 20):
    h = hashlib.sha256()
    with open(file, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()
