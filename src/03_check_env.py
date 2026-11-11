"""AGT-309 step 3: verify that the Python GIS stack is installed and importable."""
import importlib
import sys

PKGS = ["numpy", "scipy", "pandas", "matplotlib", "geopandas", "rasterio", "shapely",
        "pyproj", "pyflwdir", "h3", "yaml", "requests"]

print("Python", sys.version.split()[0])
missing = []
for p in PKGS:
    try:
        m = importlib.import_module(p)
        print(f"  OK   {p:<11} {getattr(m, '__version__', '')}")
    except Exception as e:
        missing.append(p)
        print(f"  FAIL {p:<11} {type(e).__name__}: {e}")

try:
    import h3
    v = h3.__version__
    print("H3 API:", "v4 (latlng_to_cell)" if hasattr(h3, "latlng_to_cell") else "v3 (geo_to_h3)", v)
except Exception:
    pass

sys.exit(1 if missing else 0)
