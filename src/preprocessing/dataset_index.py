"""
src/preprocessing/dataset_index.py

Builds processed dataset CSV for DataLoader use.
- Scans processed faces directory (train/val/test, real/fake)
- Outputs: data/processed/faces_index.csv
- Columns: split,label,path
"""

import csv
from pathlib import Path
from typing import List

def build_index(processed_root: str, out_csv: str):
    """
    Scan processed faces dir and write CSV index.
    Args:
        processed_root: root dir (e.g. data/processed/faces)
        out_csv: output CSV path
    """
    root = Path(processed_root)
    rows: List[dict] = []
    for split in ["train", "val", "test"]:
        for label in ["real", "fake"]:
            dir_path = root / split / label
            if not dir_path.exists():
                continue
            for img_path in dir_path.rglob("*.png"):
                rows.append({
                    "split": split,
                    "label": label,
                    "path": str(img_path.relative_to(root.parent))
                })
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["split", "label", "path"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} entries to {out_csv}")

if __name__ == "__main__":
    build_index("data/processed/faces", "data/processed/faces_index.csv")
