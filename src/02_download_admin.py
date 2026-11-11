"""AGT-309 step 2: download administrative boundaries (geoBoundaries gbOpen, CC BY 4.0)
for the country in config.yaml, then clip to the model AOI.

NOTE: not tested against the live service from the authoring environment.
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


def main():
    cfg = load_config()
    iso3 = cfg["aoi"]["country_iso3"]
    raw = path(cfg, "raw", "admin")
    proc = path(cfg, "processed", "admin")
    crs_utm = project_crs(cfg)
    aoi = gpd.read_file(path(cfg, "processed", "aoi") / "aoi_model_4326.geojson")

    for adm in cfg["aoi"]["admin_levels"]:
        meta = requests.get(API.format(iso3=iso3, adm=adm), timeout=60)
        meta.raise_for_status()
        meta = meta.json()
        meta = meta[0] if isinstance(meta, list) else meta
        data = requests.get(meta["gjDownloadURL"], timeout=600)
        data.raise_for_status()
        raw_file = raw / f"{iso3}_{adm}.geojson"
        raw_file.write_bytes(data.content)

        gdf = gpd.read_file(raw_file).to_crs(cfg["crs"]["storage"])
        clipped = gpd.clip(gdf, aoi)
        clipped.to_file(proc / f"{iso3}_{adm}_aoi_4326.gpkg", driver="GPKG")
        clipped.to_crs(crs_utm).to_file(proc / f"{iso3}_{adm}_aoi_utm.gpkg", driver="GPKG")
        print(f"{adm}: {len(gdf)} units nationally, {len(clipped)} touch the AOI")

        log_manifest(cfg, dataset=f"geoboundaries_{iso3}_{adm}", source="geoBoundaries gbOpen",
                     url=API.format(iso3=iso3, adm=adm), version=str(meta.get("boundaryYearRepresented", "")),
                     resolution="vector", crs="EPSG:4326", license="CC BY 4.0",
                     attribution=ATTRIBUTION, used_by="AGT-309;AGT-314",
                     notes=f"source: {meta.get('boundarySource', '')}")


if __name__ == "__main__":
    main()
