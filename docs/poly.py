from datetime import datetime
from pathlib import Path

from sphinx_polyversion.api import apply_overrides
from sphinx_polyversion.driver import DefaultDriver, Environment
from sphinx_polyversion.git import Git, GitRef, GitRefType, file_predicate, refs_by_type
from sphinx_polyversion.pyvenv import Pip, VenvWrapper
from sphinx_polyversion.sphinx import SphinxBuilder, Placeholder

#: Regex matching the branches to build docs for
BRANCH_REGEX = r"^master$|^stable$"

#: Regex matching the tags to build docs for
TAG_REGEX = r"^v1\.7\.\d{2,}$|^v1\.8\.\d+$|^v([2-9]|\d{2,})\.\d+\.\d+$"

#: Output dir relative to project root
OUTPUT_DIR = "docs/_build"

#: Source directory
SOURCE_DIR = "docs/"

#: Arguments to pass to `poetry install`
# POETRY_ARGS = "--only sphinx --sync".split()

#: Arguments to pass to `sphinx-build`
SPHINX_ARGS = "-a -v".split()

#: Mock data used for building local version
MOCK_DATA = {
    "revisions": [
        GitRef("v2.0.0", "", "", GitRefType.TAG, datetime.fromtimestamp(1)),
        GitRef("v1.8.0", "", "", GitRefType.TAG, datetime.fromtimestamp(0)),
        GitRef("master", "", "", GitRefType.BRANCH, datetime.fromtimestamp(2)),
    ],
    "current": GitRef("local", "", "", GitRefType.BRANCH, datetime.fromtimestamp(3)),
}
#: Whether to build using only local files and mock data
MOCK = False

#: Whether to run the builds in sequence or in parallel
SEQUENTIAL = True

# Load overrides read from commandline to global scope
apply_overrides(globals())
# Determine repository root directory
root = Git.root(Path(__file__).parent)


def data(driver: DefaultDriver, rev: GitRef, env: Environment):
    revisions = driver.targets
    branches, tags = refs_by_type(revisions)
    tags = sorted(tags, key=lambda t: t.date, reverse=True)
    latest = max(tags or branches)
    return {
        "current": rev,
        "tags": tags,
        "branches": branches,
        "revisions": revisions,
        "latest": latest,
    }


def root_data(driver: DefaultDriver):
    revisions = driver.builds
    branches, tags = refs_by_type(revisions)
    tags = sorted(tags, key=lambda t: t.date, reverse=True)
    latest = max(tags or branches)
    return {
        "tags": tags,
        "branches": branches,
        "revisions": revisions,
        "latest": latest,
    }


# Setup driver and run it
src = Path(SOURCE_DIR)
DefaultDriver(
    root,
    OUTPUT_DIR,
    vcs=Git(
        branch_regex=BRANCH_REGEX,
        tag_regex=TAG_REGEX,
        buffer_size=1 * 10**9,  # 1 GB
        predicate=file_predicate([src]),  # exclude refs without source dir
    ),
    builder=SphinxBuilder(
        src,
        args=SPHINX_ARGS,
        pre_cmd=["python", "docs/preprocess.py", Placeholder.SOURCE_DIR],
    ),
    env=Pip.factory(
        venv=Path("docs/.venv"),
        creator=VenvWrapper(),
        args=["-r", "docs/requirements.txt"],
        temporary=True,
    ),
    template_dir=root / src / "polyversion-templates",
    data_factory=data,
    root_data_factory=root_data,
    mock=MOCK_DATA,
).run(MOCK, SEQUENTIAL)
