import subprocess
import sys
from pathlib import Path

SOURCE_DIR = "docs"
DESTINATION_DIR = sys.argv[1]
BRANCH_NAME = "master"
FILES = [
    ("polyversion-templates/versions/versions.html", "_templates/versions.html"),
    ("conf.py", "conf.py"),
]
IS_LOCAL = False

for (src_file, dst_file) in FILES:
    dst_path = Path(DESTINATION_DIR) / dst_file
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    if IS_LOCAL:
        with open(f"{SOURCE_DIR}/{src_file}", "rb") as f:
            p = f.read()
    else:
        p = subprocess.run(
            ["git", "show", f"{BRANCH_NAME}:{SOURCE_DIR}/{src_file}"], capture_output=True
        ).stdout
    with open(f"{DESTINATION_DIR}/{dst_file}", "wb") as f:
        f.write(p)
