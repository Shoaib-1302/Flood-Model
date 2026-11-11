"""AGT-309 step 2: download administrative boundaries (geoBoundaries gbOpen, CC BY 4.0)
for the country in config.yaml.

Two AOI modes (config.yaml -> aoi.mode):
  bbox  (default) boundaries are clipped to the bounding-box AOI made by 01_define_aoi.py
  admin           the ADM0 country outline BECOMES the AOI (whole-country study area);
                  ADM1/ADM2 are then kept in full

Outputs:
  data/raw/admin/<ISO3>_<ADM>.geojson              untouched download
  data/processed/admin/<ISO3>_<ADM>_aoi_4326.gpkg  storage CRS
  data/processed/admin/<ISO3>_<ADM>_aoi_utm.gpkg   project CRS (file name kept for compatibility)
  data/processed/aoi/*                             rewritten from ADM0 when mode == admin

API pattern: https://www.geoboundaries.org/api/current/gbOpen/<ISO3>/<ADMn>/
The JSON reply contains 'gjDownloadURL' (full-resolution GeoJSON).
Dutch users can alternatively use the PDOK 'Bestuurlijke Gebieden' service.
"""
import requests
import geopandas as gpd
from common import load_config, path, project_crs, log_manifest

API = "https://www.geoboundaries.org/api/current/gbOpen/{iso3}/{adm}/"
ATTRIBUTION = ("Runfola, D. et al. (2020) geoBoundaries: A global database of political "
               "administrative boundaries. PLoS ONE 15(4): e0231866.")


def fetch(iso3, adm, raw_dir):
    """Download one admin level; return (GeoDataFrame in file CRS, API metadata dict)."""
    r = requests.get(API.format(iso3=iso3, adm=adm), timeout=60)
    r.raise_for_status()
    meta = r.json()
    meta = meta[0] if isinstance(meta, list) else meta
    d = requests.get(meta["gjDownloadURL"], timeout=600)
    d.raise_for_status()
    raw_file = raw_dir / f"{iso3}_{adm}.geojson"
    raw_file.write_bytes(d.content)
    return gpd.read_file(raw_file), meta


def write_aoi_from_outline(cfg, outline_4326, crs_proj):
    """Replace the AOI files with the (dissolved) country outline. Returns model AOI in 4326."""
    out = path(cfg, "processed", "aoi")
    core = outline_4326.to_crs(crs_proj).dissolve()
    core["name"] = cfg["aoi"]["name"]
    core = core[["name", "geometry"]]
    model = core.copy()
    model["geometry"] = core.buffer(cfg["aoi"]["buffer_m"])

    outline_4326.dissolve().assign(name=cfg["aoi"]["name"])[["name", "geometry"]] \
        .to_file(out / "aoi_core_4326.gpkg", driver="GPKG")
    core.to_file(out / "aoi_core_utm.gpkg", driver="GPKG")
    model.to_file(out / "aoi_model_utm.gpkg", driver="GPKG")
    model_4326 = model.to_crs(cfg["crs"]["storage"])
    model_4326.to_file(out / "aoi_model_4326.geojson", driver="GeoJSON")
    print(f"AOI replaced by country outline: {core.area.iloc[0] / 1e6:,.0f} km2 (core), "
          f"{model.area.iloc[0] / 1e6:,.0f} km2 (with {cfg['aoi']['buffer_m']} m buffer)")
    return model_4326


def main():
    cfg = load_config()
    iso3 = cfg["aoi"]["country_iso3"]
    admin_mode = cfg["aoi"].get("mode", "bbox") == "admin"
    raw = path(cfg, "raw", "admin")
    proc = path(cfg, "processed", "admin")
    crs_proj = project_crs(cfg)
    storage = cfg["crs"]["storage"]

    # ADM0 must come first in admin mode because it defines the AOI
    levels = sorted(cfg["aoi"]["admin_levels"], key=lambda a: (a != "ADM0", a))
    aoi = None
    if not admin_mode:
        aoi = gpd.read_file(path(cfg, "processed", "aoi") / "aoi_model_4326.geojson")

    for adm in levels:
        gdf, meta = fetch(iso3, adm, raw)
        gdf = gdf.to_crs(storage)

        if admin_mode:
            if adm == "ADM0":
                aoi = write_aoi_from_outline(cfg, gdf, crs_proj)
            result = gdf                       # keep the full national layer
            note = f"{len(gdf)} units (national, not clipped)"
        else:
            result = gpd.clip(gdf, aoi)
            note = f"{len(gdf)} units nationally, {len(result)} touch the AOI"

        result.to_file(proc / f"{iso3}_{adm}_aoi_4326.gpkg", driver="GPKG")
        result.to_crs(crs_proj).to_file(proc / f"{iso3}_{adm}_aoi_utm.gpkg", driver="GPKG")
        print(f"{adm}: {note}")

        log_manifest(cfg, dataset=f"geoboundaries_{iso3}_{adm}", source="geoBoundaries gbOpen",
                     url=API.format(iso3=iso3, adm=adm), version=str(meta.get("boundaryYearRepresented", "")),
                     resolution="vector", crs=storage, license="CC BY 4.0",
                     attribution=ATTRIBUTION, used_by="AGT-309;AGT-314",
                     notes=f"source: {meta.get('boundarySource', '')}")


if __name__ == "__main__":
    main()
