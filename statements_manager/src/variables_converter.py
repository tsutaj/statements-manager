from __future__ import annotations

import math
import pathlib
from logging import Logger, getLogger
from typing import Any

logger = getLogger(__name__)  # type: Logger


class VariablesConverter:
    def __init__(self, problem_attr: dict[str, Any]) -> None:
        self.vars = {}  # type: dict[str, Any]
        self.vars["constraints"] = {}  # dict[str, str]
        self.vars["samples"] = {}  # dict[str, str]
        self._convert_constraints(problem_attr)
        self._convert_samples(problem_attr)

    def _convert_constraints(self, problem_attr: dict[str, Any]) -> None:
        """
        - 制約を文字列型に変換しつつ格納
        - 数値について: 桁が大きい場合は指数表記に直され、そうでない場合はカンマがつく
        """
        if "constraints" in problem_attr:
            for name, value in problem_attr["constraints"].items():
                logger.info(f"constraints: {name} => {value}")
                self.vars["constraints"][name] = self.to_string(value)
        else:
            logger.warning("constraints are not set")

    def _convert_samples(self, problem_attr: dict[str, Any]) -> None:
        """
        - `sample_path` が指定されていない場合: 警告を出して抜ける
        - `sample_path` が指定されている場合
            - 指定ディレクトリ以下で `sample` を含むものは、すべてサンプルに関するファイルとみなす
            - 入出力の存在判定によってどのような形式 (通常 / input-only / output-only / インタラクティブ) かを判断
        """
        if "sample_path" not in problem_attr:
            logger.warning("samples are not set")
            return

        # sample_path 以下で、ファイル名に 'sample' を含むものはサンプルであるとする
        sample_names = list()
        for in_filename in problem_attr["sample_path"].glob("./*.in"):
            if str(in_filename).lower().find("sample") >= 0:
                sample_names.append(in_filename.stem)
        for out_filename in problem_attr["sample_path"].glob("./*.out"):
            if str(out_filename).lower().find("sample") >= 0:
                sample_names.append(out_filename.stem)
        for md_filename in problem_attr["sample_path"].glob("./*.md"):
            if (
                pathlib.Path(md_filename).resolve()
                != problem_attr["statement_path"].resolve()
                and str(md_filename).lower().find("sample") >= 0
            ):
                sample_names.append(md_filename.stem)
        for exp_filename in problem_attr["sample_path"].glob(
            f"./{problem_attr['lang']}/*.md"
        ):
            if str(exp_filename).lower().find("sample") >= 0:
                sample_names.append(exp_filename.stem)
        if len(sample_names) == 0:
            logger.warning("samples are not set")
        sample_names = sorted(list(set(sample_names)))

        sample_text_all = ""
        for n_sample, sample_name in enumerate(sample_names, start=1):
            logger.info(f"replace sample {n_sample} ({sample_name})")

            in_name = problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.in")
            out_name = problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.out")
            md_name = problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.md")
            exp_name = problem_attr["sample_path"] / pathlib.Path(
                f"{problem_attr['lang']}/{sample_name}.md"
            )

            # 入力 / 出力のいずれかが欠けている場合は警告だけにとどめる
            if (not in_name.exists()) and (not out_name.exists()):
                logger.warning(
                    f"{sample_name}: Neither input-file nor output-file exists."
                )
                logger.warning("Recognized as interactive sample.")
            elif not in_name.exists():
                logger.warning(f"{sample_name}: Input file does not exist.")
                logger.warning("Recognized as output-only sample.")
            elif not out_name.exists():
                logger.warning(f"{sample_name}: Output file does not exist.")
                logger.warning("Recognized as input-only sample.")

            # サンプルに対する説明が無いことに対する警告 (Markdown があるか)
            if not exp_name.exists():
                logger.warning(f"{sample_name}: There is no explanation.")

            name = "s" + str(n_sample)
            sample_text = ""
            if in_name.exists():
                with open(in_name, "r") as f:
                    input_txt = f.read()
                    if problem_attr["lang"] == "en":
                        sample_text += "### Sample Input"
                    elif problem_attr["lang"] == "ja":
                        sample_text += "### 入力例"
                    else:
                        logger.error(f"unknown lang: '{problem_attr['lang']}'")
                        raise ValueError(f"unknown lang: '{problem_attr['lang']}'")
                    if len(sample_names) >= 2:
                        sample_text += f" {n_sample}"
                    sample_text += "\n"
                    sample_text += "<pre>\n" + input_txt + "</pre>\n"
            if out_name.exists():
                with open(out_name, "r") as f:
                    output_txt = f.read()
                    if problem_attr["lang"] == "en":
                        sample_text += "### Output for the Sample Input"
                    elif problem_attr["lang"] == "ja":
                        sample_text += "### 出力例"
                    else:
                        logger.error(f"unknown lang: '{problem_attr['lang']}'")
                        raise ValueError(f"unknown lang: '{problem_attr['lang']}'")
                    if len(sample_names) >= 2:
                        sample_text += f" {n_sample}"
                    sample_text += "\n"
                    sample_text += "<pre>\n" + output_txt + "</pre>\n"
            if md_name.exists():
                with open(md_name, "r") as f:
                    md_txt = f.read()
                    sample_text += md_txt + "\n"
            if exp_name.exists():
                with open(exp_name, "r") as f:
                    exp_txt = f.read()
                    sample_text += exp_txt + "\n"
            self.vars["samples"][name] = sample_text
            sample_text_all += sample_text
        self.vars["samples"]["all"] = sample_text_all

    def to_string(self, value: Any) -> str:
        if isinstance(value, int):
            if str(value).endswith("000000"):
                k = math.floor(math.log10(abs(value)))
                if value == 10**k:
                    return f"10^{{{k}}}"
                elif value % (10**k) == 0:
                    return f"{value // 10 ** k} \\times 10^{{{k}}}"
                else:
                    return f"{value / 10 ** k} \\times 10^{{{k}}}"
            else:
                return format(value, ",").replace(",", "{,}")
        else:
            return str(value)

    def __getitem__(self, key: str) -> dict[str, str]:
        if key not in self.vars:
            logger.error(f"unknown key: {key}")
            raise KeyError(f"unknown key: {key}")
        return self.vars[key]
