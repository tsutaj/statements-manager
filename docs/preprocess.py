import subprocess
import sys
from pathlib import Path

SOURCE_DIR = "docs"
DESTINATION_DIR = sys.argv[1]
BRANCH_NAME = "master"
FILES = [
    "_templates/versions.html",
    "conf.py",
]
IS_LOCAL = False

for file in FILES:
    path = Path(DESTINATION_DIR) / file
    path.parent.mkdir(parents=True, exist_ok=True)

    if IS_LOCAL:
        with open(f"{SOURCE_DIR}/{file}", "rb") as f:
            p = f.read()
    else:
        p = subprocess.run(
            ["git", "show", f"{BRANCH_NAME}:{SOURCE_DIR}/{file}"], capture_output=True
        ).stdout
    with open(f"{DESTINATION_DIR}/{file}", "wb") as f:
        f.write(p)
