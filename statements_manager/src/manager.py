from __future__ import annotations

import pathlib
import shutil
from enum import Enum
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, List, Tuple, cast

from googleapiclient.discovery import build

from statements_manager.src.params_maker.lang_to_class import lang_to_class
from statements_manager.src.renderer import Renderer
from statements_manager.src.utils import create_token
from statements_manager.template import default_template_html, template_pdf_options

logger = getLogger(__name__)  # type: Logger


class ContentsStatus(Enum):
    OK, NG = range(2)


class Manager:
    def __init__(self, problem_attr: dict[str, Any], template_attr: dict[str, Any]):
        self._cwd = Path.cwd()
        self.problem_attr = problem_attr  # type: dict[str, Any]
        self.renderer = Renderer(
            template_attr.get("template_html", default_template_html),
            template_attr.get("preprocess_path", None),
            template_attr.get("postprocess_path", None),
        )
        self.problemset_dir = template_attr["output_path"]

    def get_local_contents(self, problem_id: str) -> Tuple[ContentsStatus, str]:
        try:
            with open(self.problem_attr[problem_id]["statement_path"]) as f:
                return (ContentsStatus.OK, f.read())
        except EnvironmentError:
            logger.error(
                f"{self.problem_attr[problem_id]['statement_path']} does not exist"
            )
            return (ContentsStatus.NG, "")

    def get_docs_contents(self, problem_id: str) -> Tuple[ContentsStatus, str]:
        statement_path = self.problem_attr[problem_id]["statement_path"]
        setting_dir = pathlib.Path(
            pathlib.Path(self.problem_attr[problem_id]["creds_path"]).parent
        )
        if not setting_dir.exists():
            logger.error(f"setting dir '{setting_dir}' does not exist")
            logger.warning(
                "tips: try 'ss-manager reg-creds' before running on docs mode."
            )
            return (ContentsStatus.NG, "")

        token = create_token(
            creds_path=self.problem_attr[problem_id]["creds_path"],
            token_path=self.problem_attr[problem_id]["token_path"],
        )
        service = build("docs", "v1", credentials=token)
        document = service.documents().get(documentId=statement_path).execute()
        contents = ""
        for content in document.get("body")["content"]:
            if "paragraph" not in content:
                continue
            for element in content["paragraph"]["elements"]:
                statement = element["textRun"]["content"]
                if "suggestedInsertionIds" not in element["textRun"]:
                    contents += statement
                else:
                    logger.warning(
                        f"proposed element for addition (ignored in rendering): {statement}"
                    )
                if "suggestedDeletionIds" in element["textRun"]:
                    logger.warning(f"proposed element for deletion: {statement}")
        return (ContentsStatus.OK, contents)

    def get_contents(self, problem_id: str) -> Tuple[ContentsStatus, str]:
        if self.problem_attr[problem_id]["mode"] == "local":
            return self.get_local_contents(problem_id)
        elif self.problem_attr[problem_id]["mode"] == "docs":
            return self.get_docs_contents(problem_id)
        else:
            logger.error(f"unknown mode: {self.problem_attr[problem_id]['mode']}")
            raise ValueError(f"unknown mode: {self.problem_attr[problem_id]['mode']}")

    def save_file(self, text: str, output_path: str):
        with open(output_path, "w") as f:
            f.write(text)

    def create_params_file(self, problem_id: str) -> None:
        logger.info("create params file")
        if (
            "params_path" in self.problem_attr[problem_id]
            and "constraints" in self.problem_attr[problem_id]
        ):
            ext = Path(self.problem_attr[problem_id]["params_path"]).suffix  # type: str
            if ext in lang_to_class:
                params_maker = lang_to_class[ext](
                    self.problem_attr[problem_id]["constraints"],
                    self.problem_attr[problem_id]["params_path"],
                )  # type: Any
                params_maker.run()
            else:
                logger.warning(
                    f"skip creating params: no language config which matches '{ext}'"
                )
        elif "constraints" not in self.problem_attr[problem_id]:
            logger.warning("skip creating params: constraints are not set")
        else:
            logger.warning("skip creating params: params_path is not set")

    def copy_assets(self, problem_id: str, output_path: Path) -> None:
        if "assets_path" in self.problem_attr[problem_id]:
            assets_src_path = Path(self.problem_attr[problem_id]["assets_path"])
            assets_dst_path = output_path / Path("assets")
            if assets_src_path.exists():
                logger.info("copy assets file")
                if assets_dst_path.exists():
                    logger.warning(
                        f"assets directory '{assets_dst_path}' already exists."
                    )
                shutil.copytree(assets_src_path, assets_dst_path, dirs_exist_ok=True)
            else:
                logger.warning(
                    f"assets_path '{self.problem_attr[problem_id]['assets_path']}' does not exist."
                )

    def run_rendering(
        self,
        output_dir: Path,
        output_ext: str,
        problem_ids: List[str],
        is_problemset: bool,
    ) -> None:
        if is_problemset:
            output_path = str(output_dir / ("problemset." + output_ext))
        else:
            output_path = str(output_dir / (problem_ids[0] + "." + output_ext))
        logger.info(f"saving replaced {output_ext}")
        if output_ext == "html":
            html = self.renderer.generate_html(
                problem_attr=self.problem_attr,
                problem_ids=problem_ids,
                is_problemset=is_problemset,
            )
            self.save_file(html, output_path)
        elif output_ext == "pdf":
            wait_second = (
                int(cast(int, template_pdf_options["javascript-delay"])) // 1000
            )
            logger.info(f"please wait... ({wait_second} sec or greater)")
            self.renderer.generate_and_dump_pdf(
                problem_attr=self.problem_attr,
                problem_ids=problem_ids,
                is_problemset=is_problemset,
                pdf_path=output_path,
                pdf_options=template_pdf_options,
            )
        elif output_ext == "md":
            md = self.renderer.generate_markdown(
                problem_attr=self.problem_attr,
                problem_ids=problem_ids,
                is_problemset=is_problemset,
            )
            self.save_file(md, output_path)
        else:
            logger.error(f"invalid extension '{output_ext}'")
            raise ValueError(f"invalid extension '{output_ext}'")

    def run(
        self,
        problem_ids: List[str],
        output_ext: str,
        make_problemset: bool,
    ) -> None:
        # 問題文を取ってきて変換
        valid_problem_ids = []
        for problem_id in problem_ids:
            logger.info(f"rendering [problem id: {problem_id}]")
            status, raw_statement = self.get_contents(problem_id)

            if status == ContentsStatus.NG:
                logger.info(f"skipped [problem id: {problem_id}]")
                logger.info("")
                continue

            # 問題文取得
            valid_problem_ids.append(problem_id)
            raw_statement = self.renderer.replace_vars(
                problem_attr=self.problem_attr[problem_id],
                statement_str=raw_statement,
            )
            self.problem_attr[problem_id]["raw_statement"] = raw_statement

            # パラメータファイル作成
            self.create_params_file(problem_id)

            # 問題文ファイル出力先
            output_dir = self.problem_attr[problem_id]["output_path"]
            if output_dir.exists():
                logger.warning(f"output directory '{output_dir}' already exists.")
            else:
                output_dir.mkdir()
            self.copy_assets(problem_id, output_dir)
            self.run_rendering(
                output_dir=output_dir,
                output_ext=output_ext,
                problem_ids=[problem_id],
                is_problemset=False,
            )
            logger.info("")

        # 問題セットに対応するものを出力
        if not valid_problem_ids:
            logger.warning("problem files not found")
        elif make_problemset:
            logger.info("rendering problemset")
            self.run_rendering(
                output_dir=self.problemset_dir,
                output_ext=output_ext,
                problem_ids=valid_problem_ids,
                is_problemset=True,
            )