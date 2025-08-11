from __future__ import annotations

import hashlib
import pathlib
import shutil
from enum import Enum
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, List, Tuple, cast

import pdfkit
from googleapiclient.discovery import build

from statements_manager.src.auth.oauth_routing import get_oauth_token
from statements_manager.src.execute_config import ProblemSetConfig
from statements_manager.src.output_file_kind import OutputFileKind
from statements_manager.src.params_maker.lang_to_class import lang_to_class
from statements_manager.src.render_result_cache import RenderResultCache
from statements_manager.src.renderer import Renderer
from statements_manager.src.statement_location_mode import StatementLocationMode

logger: Logger = getLogger(__name__)


class ContentsStatus(Enum):
    OK, NG = range(2)


class ConvertTaskRunner:
    def __init__(self, problemset_config: ProblemSetConfig):
        self._cwd = Path.cwd()
        self.problemset_config = problemset_config
        self.renderer = Renderer(
            problemset_config.template_content,
            problemset_config.sample_template_content,
            problemset_config.template.preprocess_path,
            problemset_config.template.postprocess_path,
            problemset_config.template.preprocess_command,
            problemset_config.template.postprocess_command,
        )
        self.problemset_dir = problemset_config.output_path

    def get_local_contents(self, problem_id: str) -> Tuple[ContentsStatus, str]:
        try:
            with open(
                self.problemset_config.get_problem(problem_id).statement.path,
                encoding=self.problemset_config.encoding,
            ) as f:
                return (ContentsStatus.OK, f.read())
        except EnvironmentError:
            logger.error(f"problem_id {problem_id}: statement path does not exist")
            return (ContentsStatus.NG, "")

    def get_docs_contents(
        self, problem_id: str, fail_on_suggestions: bool = False
    ) -> Tuple[ContentsStatus, str]:
        statement_path = self.problemset_config.get_problem(problem_id).statement.path
        try:
            token = get_oauth_token()
            if token is None:
                raise FileNotFoundError("token not found")

            logger.info("trying to get docs file using authenticated token")
            service = build("docs", "v1", credentials=token)
            document = service.documents().get(documentId=statement_path).execute()
            contents = ""
            has_suggestions = False
            for content in document.get("body")["content"]:
                if "paragraph" not in content:
                    continue
                for element in content["paragraph"]["elements"]:
                    statement = element["textRun"]["content"]
                    if "suggestedInsertionIds" not in element["textRun"]:
                        contents += statement
                    else:
                        has_suggestions = True
                        logger.warning(
                            f"proposed element for addition (ignored in rendering): {statement}"
                        )
                    if "suggestedDeletionIds" in element["textRun"]:
                        has_suggestions = True
                        logger.warning(f"proposed element for deletion: {statement}")

            if has_suggestions and fail_on_suggestions:
                logger.error(
                    f"unresolved suggestions found in Google Docs for problem {problem_id}"
                )
                return (ContentsStatus.NG, "")

            return (ContentsStatus.OK, contents)
        except Exception as e:
            logger.error(f"error occured: {e}")

        # どのパスでも生成できなかったらエラー
        logger.error("cannot get docs contents")
        logger.warning(
            "If this document belongs to you and was created by ss-manager, "
            "run 'ss-manager auth login' to authenticate with your Google account."
        )
        logger.warning(
            "Alternatively, you can use manually registered credentials. "
            "Run 'ss-manager reg-creds CREDS_PATH' to register your credentials file."
        )
        logger.warning(
            "For instructions on creating a credentials file, see: "
            "https://statements-manager.readthedocs.io/ja/stable/register_credentials.html"
        )
        return (ContentsStatus.NG, "")

    # ローカルまたは Google Docs から問題文のテキストファイルを取得
    def get_contents(
        self, problem_id: str, fail_on_suggestions: bool = False
    ) -> Tuple[ContentsStatus, str]:
        mode = self.problemset_config.get_problem(problem_id).statement.mode
        if mode == StatementLocationMode.LOCAL:
            return self.get_local_contents(problem_id)
        elif mode == StatementLocationMode.DOCS:
            return self.get_docs_contents(problem_id, fail_on_suggestions)
        else:
            logger.error(f"unknown mode: {mode}")
            raise ValueError(f"unknown mode: {mode}")

    def save_file(self, text: str, output_path: str):
        with open(output_path, "w", encoding=self.problemset_config.encoding) as f:
            f.write(text)

    # 制約パラメータファイル (e.g. constraints.hpp) の作成
    def create_params_file(self, problem_id: str) -> None:
        logger.info("create params file")
        problem_config = self.problemset_config.get_problem(problem_id)
        if (
            problem_config.params_path is not None
            and problem_config.constraints is not None
        ):
            ext: str = Path(problem_config.params_path).suffix
            if ext in lang_to_class:
                params_maker = lang_to_class[ext](
                    params=problem_config.constraints,
                    output_path=problem_config.params_path,
                    encoding=self.problemset_config.encoding,
                )
                params_maker.run()
            else:
                logger.warning(
                    f"skip creating params: no language config which matches '{ext}'"
                )
        elif problem_config.constraints is None:
            logger.warning("skip creating params: constraints are not set")
        else:
            logger.warning("skip creating params: params_path is not set")

    # 添付ファイル群のコピー
    def copy_assets(
        self,
        problem_id: str,
        output_path: Path,
    ) -> dict[str, str]:
        cache = {}
        problem_config = self.problemset_config.get_problem(problem_id)
        if problem_config.assets_path is not None:
            assets_src_path = Path(problem_config.assets_path)
            assets_dst_path = output_path
            if assets_src_path.exists():
                logger.info("copy assets file")
                if assets_dst_path.exists():
                    logger.warning(
                        f"assets directory '{assets_dst_path}' already exists. overwriting..."
                    )
                    shutil.rmtree(assets_dst_path)
                shutil.copytree(assets_src_path, assets_dst_path)

                for path in assets_dst_path.glob("**/*"):
                    with open(path, "rb") as f:
                        hash = hashlib.sha256(f.read()).hexdigest()
                        relpath = str(path.relative_to(output_path))
                        cache[relpath] = hash

            else:
                logger.warning(
                    f"assets_path '{problem_config.assets_path}' does not exist."
                )
        return cache

    def make_pdf_attr(self, is_problemset: bool) -> dict[str, Any]:
        pdf_attr = self.problemset_config.pdf_config.common
        if is_problemset:
            pdf_attr.update(self.problemset_config.pdf_config.problemset)
        else:
            pdf_attr.update(self.problemset_config.pdf_config.problem)
        return pdf_attr

    def run_rendering(
        self,
        output_dir: Path,
        output_ext: OutputFileKind,
        problem_ids: List[str],
        is_problemset: bool,
        force_dump: bool,
        cache: RenderResultCache,
    ) -> None:
        # Determine the actual file extension to use
        if output_ext == OutputFileKind.CUSTOM:
            if self.problemset_config.template.output_extension is None:
                logger.error(
                    "output_extension must be specified in problemset.toml [template] section "
                    "when using --output custom",
                )
                raise ValueError("output_extension not configured for custom output")
            actual_extension = self.problemset_config.template.output_extension
        else:
            actual_extension = output_ext.value

        if is_problemset:
            output_path = str(output_dir / ("problemset." + actual_extension))
        else:
            output_path = str(output_dir / (problem_ids[0] + "." + actual_extension))

        if output_ext == OutputFileKind.CUSTOM:
            logger.info(f"saving replaced custom format as {actual_extension}")
        else:
            logger.info(f"saving replaced {output_ext.value}")
        if output_ext == OutputFileKind.HTML:
            html = self.renderer.generate_html(
                problemset_config=self.problemset_config,
                problem_ids=problem_ids,
                is_problemset=is_problemset,
            )
            cache.set_content(html)
            if cache.need_to_save(force_dump):
                self.save_file(html, output_path)
            else:
                logger.warning("skip dumping html: same result as before")
        elif output_ext == OutputFileKind.PDF:
            pdf_attr = self.make_pdf_attr(is_problemset)
            html = self.renderer.generate_html_for_pdf(
                problemset_config=self.problemset_config,
                problem_ids=problem_ids,
                is_problemset=is_problemset,
                pdf_path=output_path,
            )
            cache.set_content(html)
            if cache.need_to_save(force_dump):
                wait_second = int(cast(int, pdf_attr["javascript-delay"]))
                if wait_second > 0:
                    logger.info(f"please wait... ({wait_second} [msec] or greater)")
                pdfkit.from_string(html, output_path, verbose=True, options=pdf_attr)
            else:
                logger.warning("skip dumping pdf: same result as before")
        elif output_ext == OutputFileKind.MARKDOWN:
            md = self.renderer.generate_markdown(
                problemset_config=self.problemset_config,
                problem_ids=problem_ids,
                is_problemset=is_problemset,
            )
            cache.set_content(md)
            if cache.need_to_save(force_dump):
                self.save_file(md, output_path)
            else:
                logger.warning("skip dumping md: same result as before")
        elif output_ext == OutputFileKind.CUSTOM:
            custom_result = self.renderer.generate_custom(
                problemset_config=self.problemset_config,
                problem_ids=problem_ids,
                is_problemset=is_problemset,
            )
            cache.set_content(custom_result)
            if cache.need_to_save(force_dump):
                self.save_file(custom_result, output_path)
            else:
                logger.warning("skip dumping custom: same result as before")
        else:
            logger.error(f"invalid extension '{output_ext.value}'")
            raise ValueError(f"invalid extension '{output_ext.value}'")

    def run(
        self,
        problem_ids: List[str],
        output_ext: OutputFileKind,
        make_problemset: bool,
        force_dump: bool,
        constraints_only: bool,
        keep_going: bool = False,
        fail_on_suggestions: bool = False,
    ) -> None:
        # 問題文を取ってきて変換
        valid_problem_ids = []
        has_diff = False
        for problem_id in problem_ids:
            logger.info(f"rendering [problem id: {problem_id}]")
            problem_config = self.problemset_config.get_problem(problem_id)
            self.create_params_file(problem_id)
            if constraints_only:
                continue

            status, raw_statement = self.get_contents(problem_id, fail_on_suggestions)
            if status == ContentsStatus.NG:
                if keep_going:
                    logger.info(f"skipped [problem id: {problem_id}]")
                    logger.info("")
                    continue
                else:
                    logger.error(
                        f"failed to retrieve statement for problem id: {problem_id}"
                    )
                    raise RuntimeError(
                        f"Statement retrieval failed for problem '{problem_id}'. "
                        "Use -k or --keep-going to skip failed retrievals."
                    )

            valid_problem_ids.append(problem_id)
            problem_config.statement.raw_text = raw_statement

            # 問題文ファイル出力先
            output_dir = pathlib.Path(problem_config.output_path)
            if output_dir.exists():
                logger.warning(f"output directory '{output_dir}' already exists.")
            else:
                output_dir.mkdir()

            # キャッシュの記録
            cache = RenderResultCache(
                output_dir,
                output_ext,
                problem_id,
                self.problemset_config.get_problem_group(problem_id),
            )
            cache.set_assets(self.copy_assets(problem_id, output_dir / "assets"))
            self.run_rendering(
                output_dir=output_dir,
                output_ext=output_ext,
                problem_ids=[problem_id],
                is_problemset=False,
                force_dump=force_dump,
                cache=cache,
            )
            has_diff |= cache.save_and_check_diff()
            logger.info("")

        # 問題セットに対応するものを出力
        if not valid_problem_ids and not constraints_only:
            logger.warning("problem files not found")
        elif make_problemset:
            if self.problemset_dir.exists():
                logger.warning(
                    f"output problemset directory '{self.problemset_dir}' already exists."
                )
            else:
                self.problemset_dir.mkdir()

            # 添付ファイルのコピー
            for problem_id in valid_problem_ids:
                self.copy_assets(
                    problem_id,
                    self.problemset_dir / "assets" / problem_id,
                )
            logger.info("rendering problemset")
            cache = RenderResultCache(self.problemset_dir, output_ext)
            self.run_rendering(
                output_dir=self.problemset_dir,
                output_ext=output_ext,
                problem_ids=valid_problem_ids,
                is_problemset=True,
                force_dump=force_dump or has_diff,
                cache=cache,
            )
            cache.save_and_check_diff()
