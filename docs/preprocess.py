import sys
import subprocess

SOURCE_DIR = "docs"
DESTINATION_DIR = sys.argv[1]
BRANCH_NAME = "master"
FILES = ["_templates/versions.html", "conf.py"]

subprocess.run(["mkdir", "-p", f"{DESTINATION_DIR}/_templates"])
for file in FILES:
    p = subprocess.run(
        ["git", "show", f"{BRANCH_NAME}:{SOURCE_DIR}/{file}"], capture_output=True
    )
    with open(f"{DESTINATION_DIR}/{file}", "wb") as f:
        f.write(p.stdout)
