"""AGT-309 step 4: data versioning manifest.
Walks data/raw and data/processed and writes data_checksums.csv (path, size, sha256, modified).
Commit this file (not the data): it proves which exact files produced a result.
Re-run after every download or processing step; `git diff data_checksums.csv` shows what changed.
"""
import csv
from datetime import datetime
from common import ROOT, load_config, sha256


def main():
    cfg = load_config()
    rows = []
    for key in ("raw", "processed"):
        base = ROOT / cfg["paths"][key]
        for f in sorted(base.rglob("*")):
            if f.is_file() and f.name != ".gitkeep":
                st = f.stat()
                rows.append(dict(path=str(f.relative_to(ROOT)), size_bytes=st.st_size, sha256=sha256(f),
                                 modified=datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")))
    out = ROOT / cfg["paths"]["checksums"]
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["path", "size_bytes", "sha256", "modified"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} files recorded in {out.name}")


if __name__ == "__main__":
    main()
