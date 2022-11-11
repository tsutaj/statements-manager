from __future__ import annotations

import fnmatch
import math
import pathlib
from logging import Logger, getLogger
from typing import Any, List, Set

logger = getLogger(__name__)  # type: Logger


def to_string(value: Any) -> str:
    if isinstance(value, int):
        if str(value).endswith("000000"):
            k = math.floor(math.log10(abs(value)))
            if value == 10**k:
                return f"10^{{{k}}}"
            elif value == -(10**k):
                return f"-10^{{{k}}}"
            elif value % (10**k) == 0:
                return f"{value // 10 ** k} \\times 10^{{{k}}}"
            else:
                return f"{value / 10 ** k} \\times 10^{{{k}}}"
        else:
            return format(value, ",").replace(",", "{,}")
    else:
        return str(value)


class NaturalLanguage:
    HEADER_MD = "### "

    def __init__(self, lang: str) -> None:
        if lang == "ja":
            self.language = "ja"
        elif lang == "en":
            self.language = "en"
        else:
            logger.error(f"unknown lang: '{lang}'")
            raise ValueError(f"unknown lang: '{lang}'")

    def lang(self) -> str:
        return self.language

    def header_input(self) -> str:
        if self.language == "ja":
            return self.HEADER_MD + "入力例"
        elif self.language == "en":
            return self.HEADER_MD + "Sample Input"
        return ""

    def header_output(self) -> str:
        if self.language == "ja":
            return self.HEADER_MD + "出力例"
        elif self.language == "en":
            return self.HEADER_MD + "Output for the Sample Input"
        return ""


class ConstraintsConverter:
    def convert(
        self, constraints: dict[str, Any], problem_attr: dict[str, Any]
    ) -> None:
        """
        - 制約を文字列型に変換しつつ格納
        - 数値について: 桁が大きい場合は指数表記に直され、そうでない場合はカンマがつく
        """
        if "constraints" in problem_attr:
            for name, value in problem_attr["constraints"].items():
                logger.info(f"constraints: {name} => {value}")
                constraints[name] = to_string(value)
        else:
            logger.warning("constraints are not set")


class SampleFile:
    def __init__(self, filename: pathlib.Path) -> None:
        self.filename = filename

    def exists(self) -> bool:
        return self.filename.exists()

    def print_raw(self) -> str:
        if not self.exists():
            return ""

        with open(self.filename, "r") as f:
            contents = f.read() + "\n"
            return contents

    def make_markdown(
        self, header_kind: str, lang: NaturalLanguage, n_sample: int, numbering: bool
    ) -> str:
        if not self.exists():
            return ""

        markdown_text = ""
        with open(self.filename, "r") as f:
            contents = f.read()
            if header_kind == "input":
                markdown_text += lang.header_input()
            elif header_kind == "output":
                markdown_text += lang.header_output()
            if numbering:
                markdown_text += f" {n_sample}"
            markdown_text += "\n"
            markdown_text += "<pre>\n" + contents + "</pre>\n"
        return markdown_text


class SamplesConverter:
    def get_sample_names_list(
        self,
        sample_path: pathlib.Path,
        statement_path: pathlib.Path,
        language: str,
        ignore_samples: Set,
    ) -> List[str]:
        # sample_path 以下で、ファイル名に 'sample' を含むものはサンプルであるとする
        sample_names = set()
        for in_filename in sample_path.glob("./*.in"):
            if str(in_filename).lower().find("sample") >= 0:
                sample_names.add(in_filename.stem)
        for out_filename in sample_path.glob("./*.out"):
            if str(out_filename).lower().find("sample") >= 0:
                sample_names.add(out_filename.stem)
        for diff_filename in sample_path.glob("./*.diff"):
            if str(diff_filename).lower().find("sample") >= 0:
                sample_names.add(diff_filename.stem)
        for md_filename in sample_path.glob("./*.md"):
            if (
                pathlib.Path(md_filename).resolve() != statement_path.resolve()
                and str(md_filename).lower().find("sample") >= 0
            ):
                sample_names.add(md_filename.stem)
        for exp_filename in sample_path.glob(f"./{language}/*.md"):
            if str(exp_filename).lower().find("sample") >= 0:
                sample_names.add(exp_filename.stem)

        filtered_sample = list()
        for sample_name in sample_names:
            if not any(
                [fnmatch.fnmatch(sample_name, pattern) for pattern in ignore_samples]
            ):
                filtered_sample.append(sample_name)
        return sorted(filtered_sample)

    def print_warning(
        self,
        sample_name: str,
        in_file: SampleFile,
        out_file: SampleFile,
        diff_file: SampleFile,
        exp_file: SampleFile,
    ) -> None:
        # 入力 / 出力のいずれかが欠けている場合は警告だけにとどめる
        out_exists = out_file.exists() or diff_file.exists()
        if (not in_file.exists()) and (not out_exists):
            logger.warning(f"{sample_name}: Neither input-file nor output-file exists.")
            logger.warning("Recognized as interactive sample.")
        elif not in_file.exists():
            logger.warning(f"{sample_name}: Input file does not exist.")
            logger.warning("Recognized as output-only sample.")
        elif not out_exists:
            logger.warning(f"{sample_name}: Output file does not exist.")
            logger.warning("Recognized as input-only sample.")

        # サンプルに対する説明が無いことに対する警告 (Markdown があるか)
        if not exp_file.exists():
            logger.warning(f"{sample_name}: There is no explanation.")

    def convert(self, samples: dict[str, Any], problem_attr: dict[str, Any]) -> None:
        """
        - `sample_path` が指定されていない場合: 警告を出して抜ける
        - `sample_path` が指定されている場合
            - 指定ディレクトリ以下で `sample` を含むものは、すべてサンプルに関するファイルとみなす
            - 入出力の存在判定によってどのような形式 (通常 / input-only / output-only / インタラクティブ) かを判断
        """
        if "sample_path" not in problem_attr:
            logger.warning("samples are not set")
            return

        language = NaturalLanguage(problem_attr["lang"])
        sample_names = self.get_sample_names_list(
            problem_attr["sample_path"],
            problem_attr["statement_path"],
            problem_attr["lang"],
            problem_attr.get("ignore_samples", list()),
        )
        if len(sample_names) == 0:
            logger.warning("samples are not set")

        numbering = len(sample_names) >= 2
        sample_text_all = ""
        for n_sample, sample_name in enumerate(sample_names, start=1):
            logger.info(f"replace sample {n_sample} ({sample_name})")

            in_file = SampleFile(
                problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.in")
            )
            out_file = SampleFile(
                problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.out")
            )
            diff_file = SampleFile(
                problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.diff")
            )
            md_file = SampleFile(
                problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.md")
            )
            exp_file = SampleFile(
                problem_attr["sample_path"]
                / pathlib.Path(f"{problem_attr['lang']}/{sample_name}.md")
            )
            self.print_warning(sample_name, in_file, out_file, diff_file, exp_file)

            name = "s" + str(n_sample)
            sample_text = ""
            sample_text += in_file.make_markdown("input", language, n_sample, numbering)
            sample_text += out_file.make_markdown(
                "output", language, n_sample, numbering
            )
            sample_text += diff_file.make_markdown(
                "output", language, n_sample, numbering
            )
            sample_text += md_file.print_raw()
            sample_text += exp_file.print_raw()

            samples[name] = sample_text
            sample_text_all += sample_text
        samples["all"] = sample_text_all


class VariablesConverter:
    def __init__(self, problem_attr: dict[str, Any]) -> None:
        self.vars = {}  # type: dict[str, Any]
        self.vars["constraints"] = {}  # dict[str, str]
        self.vars["samples"] = {}  # dict[str, str]
        self.constraints_converter = ConstraintsConverter()
        self.samples_converter = SamplesConverter()

        self.constraints_converter.convert(self.vars["constraints"], problem_attr)
        self.samples_converter.convert(self.vars["samples"], problem_attr)

    def __getitem__(self, key: str) -> dict[str, str]:
        if key not in self.vars:
            logger.error(f"unknown key: {key}")
            raise KeyError(f"unknown key: {key}")
        return self.vars[key]
