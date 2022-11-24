from __future__ import annotations

import copy
from logging import Logger, getLogger
from pathlib import Path
from typing import Any

import toml

from statements_manager.src.manager import Manager
from statements_manager.src.recognize_mode import recognize_mode
from statements_manager.src.utils import resolve_path

logger: Logger = getLogger(__name__)


class Project:
    def __init__(self, working_dir: str, ext: str) -> None:
        self._cwd: Path = Path(working_dir).resolve()
        self._ext: str = ext
        self.problem_attr = self._search_problem_attr()
        self._check_project()
        self.template_attr = self._search_template_attr()
        self._check_template()
        self.pdf_attr_raw = self._search_pdf_attr_raw()
        self.stmts_manager = Manager(
            problem_attr=self.problem_attr,
            template_attr=self.template_attr,
            pdf_attr_raw=self.pdf_attr_raw,
        )

    def run_problems(self, make_problemset: bool, force_dump: bool) -> None:
        """問題文作成を実行する"""
        problem_ids: list[str] = sorted(list(self.problem_attr.keys()))
        self.stmts_manager.run(
            problem_ids=problem_ids,
            output_ext=self._ext,
            make_problemset=make_problemset,
            force_dump=force_dump,
        )

    def _check_project(self) -> None:
        """問題設定ファイルの中身をチェックする"""
        acceptable_attr = [
            # problem.toml 内の問題ファイルそれぞれに共通して使われる属性
            "id",
            "assets_path",
            "sample_path",
            "ignore_samples",
            "params_path",
            "constraints",
            # これ以下はユーザーが設定しない属性
            "output_path",
            "output_ext",
            "creds_path",
            "token_path",
            "statement_path",
            "mode",
            "lang",
        ]
        for problem in self.problem_attr.values():
            for key in problem.keys():
                if key not in acceptable_attr:
                    logger.warning(
                        f"unknown attribute in problem setting file: '{key}'"
                    )

    def _check_template(self) -> None:
        acceptable_attr = [
            "template_path",
            "preprocess_path",
            "postprocess_path",
            # これ以下はユーザーが設定しない属性
            "template_html",
            "sample_template_html",
            "output_path",
        ]
        for key in self.template_attr.keys():
            if key not in acceptable_attr:
                logger.warning(f"unknown attribute in template setting file: '{key}'")

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
        result_dict: dict[str, Any] = {}
        for problem_file in sorted(self._cwd.glob("./**/problem.toml")):
            dir_name = problem_file.parent.resolve()
            problem_dict = toml.load(problem_file)

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
            lang_count: dict[str, int] = {}
            lang_number: dict[str, int] = {}
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
                if len(lang_count) > 1:
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
                result_dict[problem_id]["output_ext"] = self._ext
                # 言語のデフォルトは英語
                result_dict[problem_id].setdefault("lang", "en")
                result_dict[problem_id]["lang"] = result_dict[problem_id][
                    "lang"
                ].lower()
        return result_dict

    def _search_template_attr(
        self,
    ) -> dict[str, Any]:
        """problemset.toml (問題セットの設定ファイル) を探す"""
        config_file = self._cwd / "problemset.toml"
        dir_name = config_file.parent.resolve()
        if config_file.exists():
            config_toml = toml.load(config_file)
            if "template" in config_toml:
                config_dict = config_toml["template"]
            else:
                logger.warning("template settings not found.")
                config_dict = {}
        else:
            logger.warning(f"{config_file} not found.")
            config_dict = {}

        result_dict: dict[str, Any] = {}
        # テンプレートファイル
        if "template_path" in config_dict:
            with open(dir_name / Path(config_dict["template_path"])) as f:
                result_dict["template_html"] = f.read()
        if "sample_template_path" in config_dict:
            with open(dir_name / Path(config_dict["sample_template_path"])) as f:
                result_dict["sample_template_html"] = f.read()

        result_dict["output_path"] = dir_name / "problemset"
        keys = ["preprocess_path", "postprocess_path"]
        for key in keys:
            if key in config_dict.keys():
                result_dict[key] = dir_name / config_dict[key]
        return result_dict

    def _search_pdf_attr_raw(
        self,
    ) -> dict[str, Any]:
        """problemset.toml (問題セットの設定ファイル) を探し、PDF 設定を得る"""
        config_file = self._cwd / "problemset.toml"
        if config_file.exists():
            config_toml = toml.load(config_file)
            if "pdf" in config_toml:
                config_dict = config_toml["pdf"]
            else:
                logger.warning("pdf settings not found.")
                config_dict = {}
        else:
            logger.warning(f"{config_file} not found.")
            config_dict = {}
        return config_dict
