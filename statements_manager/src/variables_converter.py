from __future__ import annotations
import pathlib
import math
from typing import Any
from logging import Logger, getLogger

logger = getLogger(__name__)  # type: Logger


class VariablesConverter:
    def __init__(self, problem_attr: dict[str, Any]) -> None:
        self.vars = {}  # type: dict[str, Any]
        self.vars["constraints"] = {}  # dict[str, str]
        self.vars["samples"] = {}  # dict[str, str]

        if "constraints" in problem_attr:
            for name, value in problem_attr["constraints"].items():
                logger.info("constraints: {} => {}".format(name, value))
                self.vars["constraints"][name] = self.to_string(value)
        else:
            logger.warning("constraints are not set")

        sample_names = set()
        print("sample path:", problem_attr["sample_path"])
        for in_filename in problem_attr["sample_path"].glob("./**/*.in"):
            sample_names.add(in_filename.stem)
        for out_filename in problem_attr["sample_path"].glob("./**/*.out"):
            sample_names.add(out_filename.stem)
        for md_filename in problem_attr["sample_path"].glob("./**/*.md"):
            if md_filename.resolve() != problem_attr["statement_path"].resolve():
                sample_names.add(md_filename.stem)
        if sample_names == set():
            logger.warning("samples are not set")
        sample_names = set(sorted(list(sample_names)))

        for n_sample, sample_name in enumerate(sample_names, start=1):
            in_name = problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.in")
            out_name = problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.out")
            md_name = problem_attr["sample_path"] / pathlib.Path(f"{sample_name}.md")

            # 入力 / 出力のいずれかが欠けている場合は警告だけにとどめる
            if (not in_name.exists()) and (not out_name.exists()):
                logger.warning(
                    f"{sample_name}: Neither input-file nor output-file exists. \
                    Recognized as interactive sample."
                )
            elif not in_name.exists():
                logger.warning(
                    f"{sample_name}: Input file does not exist. \
                    Recognized as output-only sample."
                )
            elif not out_name.exists():
                logger.warning(
                    f"{sample_name}: Output file does not exist. \
                    Recognized as input-only sample."
                )

            # 説明が無いことの報告
            if not md_name.exists():
                logger.info(f"{sample_name}: There is no explanation.")

            name = "s" + str(n_sample)
            logger.info(f"replace sample {n_sample}")
            sample_text = ""
            if in_name.exists():
                with open(in_name, "r") as f:
                    input_txt = f.read()
                    sample_text += "### 入力例 {}\n".format(n_sample)
                    sample_text += "<pre>\n" + input_txt + "</pre>\n"
            if out_name.exists():
                with open(out_name, "r") as f:
                    output_txt = f.read()
                    sample_text += "### 出力例 {}\n".format(n_sample)
                    sample_text += "<pre>\n" + output_txt + "</pre>\n"
            if md_name.exists():
                with open(md_name, "r") as f:
                    md_txt = f.read()
                    sample_text += md_txt + "\n"
            self.vars["samples"][name] = sample_text

    def to_string(self, value: Any) -> str:
        if isinstance(value, int):
            if str(value).endswith("000000"):
                k = math.floor(math.log10(abs(value)))
                if value == 10 ** k:
                    return "10^{{{}}}".format(k)
                elif value % (10 ** k) == 0:
                    return "{} \times 10^{{{}}}".format(value // 10 ** k, k)
                else:
                    return "{} \times 10^{{{}}}".format(value / 10 ** k, k)
            else:
                return format(value, ",").replace(",", "{,}")
        else:
            return str(value)

    def __getitem__(self, key: str) -> dict[str, str]:
        if key not in self.vars:
            logger.error("unknown key: {}".format(key))
            raise KeyError("unknown key: {}".format(key))
        return self.vars[key]
