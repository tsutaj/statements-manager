import pathlib
import math
from typing import Dict, Any
from logging import Logger, getLogger

logger = getLogger(__name__)  # type: Logger


class VariablesConverter:
    def __init__(self, problem: Dict[str, Any]) -> None:
        self.vars = {}  # type: Dict[str, Any]
        self.vars["constraints"] = {}  # Dict[str, str]

        if "constraints" in problem:
            for name, value in problem["constraints"].items():
                logger.info("constraints: {} => {}".format(name, value))
                self.vars["constraints"][name] = self.to_string(value)
        else:
            logger.warning("constraints are not set")

        self.vars["samples"] = {}
        if "samples" in problem:
            n_sample = 1
            for sample in problem["samples"]:
                name = "s" + str(n_sample)
                tp = sample.get("type", "default")
                logger.info("replace sample {} [type: {}]".format(n_sample, tp))
                sample_text = ""
                if (tp == "default") or (tp == "input_only"):
                    with open(pathlib.Path(sample["input_path"]), "r") as f:
                        input_txt = f.read()
                        sample_text += "### 入力例 {}\n".format(n_sample)
                        sample_text += "<pre>\n" + input_txt + "</pre>\n"
                if (tp == "default") or (tp == "output_only"):
                    with open(pathlib.Path(sample["output_path"]), "r") as f:
                        output_txt = f.read()
                        sample_text += "### 出力例 {}\n".format(n_sample)
                        sample_text += "<pre>\n" + output_txt + "</pre>\n"
                if tp == "interactive":
                    with open(pathlib.Path(sample["interactive_path"]), "r") as f:
                        interactive_txt = f.read()
                        sample_text += "### 入出力例 {}\n".format(n_sample)
                        sample_text += interactive_txt
                self.vars["samples"][name] = sample_text
                n_sample += 1
        else:
            logger.warning("samples are not set")

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

    def __getitem__(self, key: str) -> Dict[str, str]:
        if key not in self.vars:
            logger.error("unknown key: {}".format(key))
            raise KeyError("unknown key: {}".format(key))
        return self.vars[key]
