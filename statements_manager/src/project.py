from __future__ import annotations

import copy
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, List

import toml

from statements_manager.src.manager.docs_manager import DocsManager
from statements_manager.src.manager.local_manager import LocalManager
from statements_manager.src.manager.recognize_mode import recognize_mode
from statements_manager.src.utils import resolve_path

logger = getLogger(__name__)  # type: Logger


class Project:
    def __init__(self, working_dir: str, output: str) -> None:
        self._cwd = Path(working_dir).resolve()
        self._output = output  # type: str
        self._problemset_html_list = []  # type: List[str]
        self.stmts_manager = None  # type: Any
        self.problem_attr = self._search_problem_attr()
        self._check_project()

    def set_config(self, config: dict[str, Any], mode: str) -> None:
        if mode == "docs":
            self.stmts_manager = DocsManager(config)
        elif mode == "local":
            self.stmts_manager = LocalManager(config)

    def run_problem(self) -> None:
        if self.stmts_manager is not None:
            problem_html = self.stmts_manager.run_problem()  # type: str
            if len(problem_html) > 0:
                self._problemset_html_list.append(problem_html)

    def run_problemset(self) -> None:
        problemset_html = '<div style="page-break-after:always;"></div>'.join(
            self._problemset_html_list
        )
        if self.stmts_manager is not None:
            self.stmts_manager.run_problemset(problemset_html, self._cwd)

    def _check_project(self) -> None:
        acceptable_attr = [
            "mode",
            "id",
            "statement_path",
            "lang",
            "assets_path",
            "sample_path",
            "params_path",
            "constraints",
            # これ以下はユーザーが設定しない属性
            "output_path",
            "output_ext",
            "creds_path",
            "token_path",
        ]
        for problem in self.problem_attr.values():
            for key in problem.keys():
                if key not in acceptable_attr:
                    logger.error(f"unknown attribute in setting file: '{key}'")
                    raise KeyError(f"unknown attribute in setting file: '{key}'")

    def _merge_dict(
        self,
        lhs: dict[str, Any],
        rhs: dict[str, Any],
        base_path: Path,
    ) -> dict[str, Any]:
        """lhs に rhs の内容をマージする
        lhs にキーがあればそちらを優先し、なければ rhs の情報を用いる
        """
        result_dict = copy.deepcopy(rhs)
        result_dict.update(lhs)
        return self._to_absolute_path(result_dict, base_path)

    def _to_absolute_path(
        self, setting_dict: dict[str, Any], base_path: Path
    ) -> dict[str, Any]:
        """setting_dict に含まれているキーの中で
        '_path' で終わるもの全てに対して、値を絶対パスに変更 (既に絶対パスなら何もしない)
        ただし docs mode の場合の statement_path は置換しない
        """
        base_path = base_path.resolve()
        result_dict = copy.deepcopy(setting_dict)
        for k, v in result_dict.items():
            if k.endswith("_path") and not (
                setting_dict["mode"] == "docs" and k == "statement_path"
            ):
                result_dict[k] = resolve_path(base_path, Path(v))
        return result_dict

    def _search_problem_attr(
        self,
    ) -> dict[str, Any]:
        """problem.toml が含まれているディレクトリを問題ディレクトリとみなす
        問題ごとに設定ファイルを読み込む
        """
        result_dict = {}  # type: dict[str, Any]
        for problem_file in sorted(self._cwd.glob("./**/problem.toml")):
            dir_name = problem_file.parent.resolve()
            problem_dict = toml.load(problem_file)
            if "id" not in problem_dict:
                logger.error(f"{problem_file} has not 'id' key.")
                raise KeyError(f"{problem_file} has not 'id' key.")
            elif problem_dict["id"] in result_dict:
                logger.error(f'problem id \'{problem_dict["id"]}\' appears twice')
                raise ValueError(f'problem id \'{problem_dict["id"]}\' appears twice')
            problem_id = problem_dict["id"]

            # mode の自動認識 (ここで mode が確定)
            if "mode" not in problem_dict:
                mode = recognize_mode(problem_dict, problem_file.parent)
                problem_dict["mode"] = mode

            # 各プロパティは絶対パスに変換される
            # これ以降に problem_dict を使うことはない
            result_dict[problem_id] = self._to_absolute_path(
                problem_dict, problem_file.parent
            )

            # docs モードのときはパスと解釈してはならない
            # credentials と token のパスを付与
            if result_dict[problem_id].get("mode") == "docs":
                result_dict[problem_id]["creds_path"] = self._cwd / Path(
                    ".ss-manager", "credentials.json"
                )
                result_dict[problem_id]["token_path"] = self._cwd / Path(
                    ".ss-manager", "token.pickle"
                )
            # sample_path のデフォルトは problem.toml 内の tests ディレクトリ
            result_dict[problem_id].setdefault("sample_path", dir_name / Path("tests"))
            # output_path のデフォルトは problem.toml 内の ss-out ディレクトリ
            result_dict[problem_id].setdefault("output_path", dir_name / Path("ss-out"))
            # output_ext (出力ファイルの拡張子)
            result_dict[problem_id]["output_ext"] = self._output
            # 言語のデフォルトは英語
            result_dict[problem_id].setdefault("lang", "en")
            result_dict[problem_id]["lang"] = result_dict[problem_id]["lang"].lower()
        return result_dict
