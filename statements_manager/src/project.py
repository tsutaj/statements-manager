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
from statements_manager.template import template_html

logger = getLogger(__name__)  # type: Logger


class Project:
    def __init__(self, working_dir: str, output: str) -> None:
        self._cwd = Path(working_dir).resolve()
        self._output = output  # type: str
        self._problemset_html_list = []  # type: List[str]
        self.stmts_manager = None  # type: Any
        self.problem_attr = self._search_problem_attr()
        self._check_project()

    def run_problems(self) -> None:
        """それぞれの問題について問題文作成を実行する"""
        for problem_id, config in self.problem_attr.items():
            mode = config["mode"].lower()  # type: str
            lang = config["lang"].lower()  # type: str

            if mode == "docs":
                logger.info(f"{problem_id}: running in 'docs' mode (lang: {lang})")
                self.stmts_manager = DocsManager(config)
            elif mode == "local":
                logger.info(f"{problem_id}: running in 'local' mode (lang: {lang})")
                self.stmts_manager = LocalManager(config)
            else:
                logger.error(f"unknown mode: {mode}")
                raise ValueError(f"unknown mode: {mode}")

            problem_html = self.stmts_manager.run_problem()  # type: str
            if len(problem_html) > 0:
                self._problemset_html_list.append(problem_html)

            logger.info("")

    def run_problemset(self) -> None:
        """問題セット全体の PDF を作成する"""
        problemset_html = '<div style="page-break-after:always;"></div>'.join(
            self._problemset_html_list
        )
        if self.stmts_manager is not None:
            self.stmts_manager.run_problemset(problemset_html, self._cwd)

    def _check_project(self) -> None:
        """問題設定ファイルの中身をチェックする"""
        acceptable_attr = [
            # problem.toml 内の問題ファイルそれぞれに共通して使われる属性
            "id",
            "assets_path",
            "sample_path",
            "params_path",
            "constraints",
            "template_path",
            "preprocess_path",
            "postprocess_path",
            # これ以下はユーザーが設定しない属性
            "output_path",
            "output_ext",
            "creds_path",
            "token_path",
            "template_html",
            "statement_path",
            "mode",
            "lang",
        ]
        for problem in self.problem_attr.values():
            for key in problem.keys():
                if key not in acceptable_attr:
                    logger.warning(f"unknown attribute in setting file: '{key}'")

    def _check_statement_info(self, statement_info: dict[str, Any]):
        """[[statement]] の中身をチェックする"""
        acceptable_attr = [
            "path",  # これは後で 'statement_path' に置換される
            "lang",
            "mode",
        ]
        for key in statement_info.keys():
            if key not in acceptable_attr:
                logger.warning(f"unknown attribute in [[statement]]: '{key}'")

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
        ids = set()
        result_dict = {}  # type: dict[str, Any]
        for problem_file in sorted(self._cwd.glob("./**/problem.toml")):
            dir_name = problem_file.parent.resolve()
            problem_dict = toml.load(problem_file)

            # HTML テンプレートを表す文字列 (指定がなければデフォルトのものを使う)
            if "template_path" not in problem_dict:
                problem_dict["template_html"] = template_html
            else:
                with open(dir_name / Path(problem_dict["template_path"])) as f:
                    problem_dict["template_html"] = f.read()

            # id は必ず設定が必要
            # id は重複してはならない (既に見たものは set で持つ)
            if "id" not in problem_dict:
                logger.error(f"{problem_file} has not 'id' key.")
                raise KeyError(f"{problem_file} has not 'id' key.")
            elif problem_dict["id"] in ids:
                logger.error(f'problem id \'{problem_dict["id"]}\' appears twice')
                raise ValueError(f'problem id \'{problem_dict["id"]}\' appears twice')
            ids.add(problem_dict["id"])

            # statements で設定されているものそれぞれについて回す
            # id と、どの lang が何回来たかに応じてファイル名が決定
            lang_count = {}  # type: dict[str, int]
            lang_number = {}  # type: dict[str, int]
            for statement_info in problem_dict["statements"]:
                lang = statement_info.get("lang", "en")
                lang_number.setdefault(lang, 0)
                lang_count.setdefault(lang, 0)
                lang_count[lang] += 1

            for statement_info in problem_dict["statements"]:
                id = problem_dict["id"]
                lang = statement_info.get("lang", "en")
                lang_number[lang] += 1
                # 1 個しかないならナンバリングしない
                problem_id = f"{id}"
                if lang_count[lang] > 1:
                    problem_id += f"{lang_number[lang]}"
                if len(problem_dict["statements"]) > 1:
                    problem_id += f"_{lang}"

                # 問題全体の設定と問題文特有の設定とをマージする
                self._check_statement_info(statement_info)
                result_dict[problem_id] = {**problem_dict, **statement_info}
                result_dict[problem_id].pop("statements")
                result_dict[problem_id]["id"] = problem_id
                result_dict[problem_id]["statement_path"] = result_dict[problem_id].pop(
                    "path"
                )

                # mode の自動認識 (ここで mode が確定)
                if "mode" not in statement_info:
                    mode = recognize_mode(result_dict[problem_id], problem_file.parent)
                    result_dict[problem_id]["mode"] = mode

                # 各プロパティは絶対パスに変換される
                result_dict[problem_id] = self._to_absolute_path(
                    result_dict[problem_id], problem_file.parent
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
                result_dict[problem_id].setdefault(
                    "sample_path", dir_name / Path("tests")
                )
                # output_path のデフォルトは problem.toml 内の ss-out ディレクトリ
                result_dict[problem_id].setdefault(
                    "output_path", dir_name / Path("ss-out")
                )
                # output_ext (出力ファイルの拡張子)
                result_dict[problem_id]["output_ext"] = self._output
                # 言語のデフォルトは英語
                result_dict[problem_id].setdefault("lang", "en")
                result_dict[problem_id]["lang"] = result_dict[problem_id][
                    "lang"
                ].lower()
        return result_dict
