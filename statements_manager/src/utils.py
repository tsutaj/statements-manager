from pathlib import Path


def resolve_path(base_path: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    else:
        return base_path / path
