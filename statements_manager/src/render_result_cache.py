from __future__ import annotations

import copy
import enum
import glob
import json
import os
import pathlib
from typing import Any, Optional

from statements_manager.src.output_file_kind import OutputFileKind


@enum.unique
class CacheKey(enum.Enum):
    ASSETS = "assets"
    CONTENTS = "contents"


class RenderResultCache:
    def __init__(
        self,
        output_dir: pathlib.Path,
        output_ext: OutputFileKind,
        problem_id: Optional[str] = None,
        problem_group: Optional[list[str]] = None,
    ):
        self.output_dir = output_dir
        self.output_ext = output_ext
        self.cache_path = output_dir / "cache.json"
        self.problem_id = "problemset" if problem_id is None else problem_id
        self.problem_group = ["problemset"] if problem_group is None else problem_group
        self.cache = self._load_and_setup_cache()
        self.prev_cache = copy.deepcopy(self.cache)

    def _load_cache(self) -> dict:
        if not self.cache_path.exists():
            return {}
        with open(self.cache_path, "r") as f:
            return self._cleanup(json.load(f))

    def _setup_cache(self, cache: dict) -> dict:
        cache.setdefault(self.output_ext.value, {})
        cache[self.output_ext.value].setdefault(self.problem_id, {})
        cache[self.output_ext.value][self.problem_id].setdefault(
            CacheKey.ASSETS.value, {}
        )
        return cache

    def _load_and_setup_cache(self) -> dict:
        cache = self._load_cache()
        return self._setup_cache(cache)

    def _cleanup(self, cache: dict) -> dict:
        for ext in cache.keys():
            obsoleted_ids = list(
                filter(lambda id: id not in self.problem_group, cache[ext].keys())
            )
            for id in obsoleted_ids:
                cache[ext].pop(id)
        obsolete_filenames = list(
            filter(
                lambda filename: pathlib.Path(filename).stem not in self.problem_group,
                sum(
                    [
                        list(glob.glob(str(self.output_dir) + f"/*.{ext}"))
                        for ext in OutputFileKind.values()
                    ],
                    [],
                ),
            )
        )
        for filename in obsolete_filenames:
            os.remove(filename)
        return cache

    def get_current(self) -> dict[str, Any]:
        return self.cache[self.output_ext.value][self.problem_id]

    def get_previous(self) -> dict[str, Any]:
        return self.prev_cache[self.output_ext.value][self.problem_id]

    def set_assets(self, assets_dict: dict[str, Any]):
        self.cache[self.output_ext.value][self.problem_id][
            CacheKey.ASSETS.value
        ] = assets_dict

    def save_and_check_diff(self, cache_dict: dict[str, Any]) -> bool:
        self.cache[self.output_ext.value][self.problem_id] = cache_dict
        json.dump(
            self.cache,
            open(self.cache_path, "w"),
            indent=4,
            sort_keys=True,
        )
        has_diff = (
            self.cache[self.output_ext.value][self.problem_id]
            != self.prev_cache[self.output_ext.value][self.problem_id]
        )
        self.prev_cache = copy.deepcopy(self.cache)
        return has_diff
