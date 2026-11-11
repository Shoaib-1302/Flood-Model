"""AGT-309 step 1: define the AOI in EPSG:4326 and the target UTM CRS.

Outputs in data/processed/aoi/:
  aoi_core_4326.gpkg   core box as given
  aoi_core_utm.gpkg    core box in the project UTM CRS
  aoi_model_utm.gpkg   core + buffer (use this to clip data)
  aoi_model_4326.geojson   same, for web use
"""
from common import load_config, path, aoi_bbox_gdf, project_crs


def main():
    cfg = load_config()
    out = path(cfg, "processed", "aoi")
    crs_utm = project_crs(cfg)

    core4326 = aoi_bbox_gdf(cfg)
    core = core4326.to_crs(crs_utm)
    model = core.copy()
    model["geometry"] = core.buffer(cfg["aoi"]["buffer_m"])

    core4326.to_file(out / "aoi_core_4326.gpkg", driver="GPKG")
    core.to_file(out / "aoi_core_utm.gpkg", driver="GPKG")
    model.to_file(out / "aoi_model_utm.gpkg", driver="GPKG")
    model.to_crs(cfg["crs"]["storage"]).to_file(out / "aoi_model_4326.geojson", driver="GeoJSON")

    print(f"AOI name       : {cfg['aoi']['name']}")
    print(f"Storage CRS    : {cfg['crs']['storage']}")
    print(f"Project CRS    : {crs_utm}")
    print(f"Core area      : {core.area.iloc[0] / 1e6:.2f} km2")
    print(f"Model area     : {model.area.iloc[0] / 1e6:.2f} km2 (buffer {cfg['aoi']['buffer_m']} m)")
    print(f"Model bounds 4326 [w,s,e,n]: {model.to_crs(cfg['crs']['storage']).total_bounds.round(5)}")
    print(f"Saved to       : {out}")
    print("Write the chosen CRS into config.yaml (crs.project) to freeze it for the whole project.")


if __name__ == "__main__":
    main()
