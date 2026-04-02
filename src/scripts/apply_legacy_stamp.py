import os
from pathlib import Path
import sys

# CORE Imports
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from src.daemons.dread_membrane_daemon import iter_md_files, check_md_file

def stamp_legacy_files():
    md_paths = iter_md_files()
    stamped_count = 0

    for p in md_paths:
        if check_md_file(p) == "FAIL":
            try:
                # Appending the stamp
                with open(p, "a", encoding="utf-8") as f:
                    f.write("\n\n[LEGACY_UNAUDITED]\n")
                stamped_count += 1
                print(f"Stamped: {p.relative_to(_REPO_ROOT)}")
            except Exception as e:
                print(f"Failed to stamp {p}: {e}")

    print(f"\nDone. Stamped {stamped_count} legacy files.")

if __name__ == "__main__":
    stamp_legacy_files()
