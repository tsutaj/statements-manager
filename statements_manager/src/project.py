from __future__ import annotations

from logging import Logger, getLogger
from pathlib import Path

from statements_manager.src.convert_task_runner import ConvertTaskRunner
from statements_manager.src.execute_config import ProblemSetConfig
from statements_manager.src.output_file_kind import OutputFileKind
from statements_manager.src.utils import find_in_parents, read_toml_file

logger: Logger = getLogger(__name__)


class Project:
    def __init__(self, working_dir: str, ext: str, make_problemset: bool) -> None:
        self._cwd: Path = Path(working_dir).resolve()
        self._ext: OutputFileKind = OutputFileKind(ext)
        self.problemset_config = self._fetch_problemset_config(make_problemset)
        self.task_runner = ConvertTaskRunner(
            problemset_config=self.problemset_config,
        )

    def run_problems(
        self,
        make_problemset: bool,
        force_dump: bool,
        constraints_only: bool,
        keep_going: bool,
        fail_on_suggestions: bool,
    ) -> None:
        """問題文作成を実行する"""
        problem_ids: list[str] = self.problemset_config.get_problem_ids()
        self.task_runner.run(
            problem_ids=problem_ids,
            output_ext=self._ext,
            make_problemset=make_problemset,
            force_dump=force_dump,
            constraints_only=constraints_only,
            keep_going=keep_going,
            fail_on_suggestions=fail_on_suggestions,
        )

    def _fetch_problemset_config(self, make_problemset: bool) -> ProblemSetConfig:
        """problem.toml が含まれているディレクトリを問題ディレクトリとみなす
        問題ごとに設定ファイルを読み込む
        """
        default_filename = self._cwd / "problemset.toml"
        problemset_config_filename = find_in_parents(default_filename)
        if problemset_config_filename is None:
            problemset_config_filename = default_filename
            if make_problemset:
                logger.warn("problemset.toml not found.")
                logger.warn(
                    "You can change the design of the problem set. "
                    "see the document: https://statements-manager.readthedocs.io/ja/stable/problemset_config.html"  # noqa
                )
        logger.debug(f"path to problemset: {problemset_config_filename}")
        problemset_config_dict = read_toml_file(problemset_config_filename)
        problemset_config = ProblemSetConfig(
            problemset_config_filename, problemset_config_dict
        )

        # if make_problemset, try to read all problems.
        problem_dir = (
            problemset_config_filename.parent if make_problemset else self._cwd
        )
        for problem_file in sorted(problem_dir.glob("./**/problem.toml")):
            problemset_config.add_problem_configs(problem_file)
        return problemset_config
