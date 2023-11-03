from __future__ import annotations

from logging import Logger, getLogger
from pathlib import Path

from statements_manager.src.convert_task_runner import ConvertTaskRunner
from statements_manager.src.execute_config import ProblemSetConfig
from statements_manager.src.utils import read_toml_file

logger: Logger = getLogger(__name__)


class Project:
    def __init__(self, working_dir: str, ext: str) -> None:
        self._cwd: Path = Path(working_dir).resolve()
        self._ext: str = ext
        self.problemset_config = self._fetch_problemset_config()
        self.task_runner = ConvertTaskRunner(
            problemset_config=self.problemset_config,
        )

    def run_problems(
        self, make_problemset: bool, force_dump: bool, constraints_only: bool
    ) -> None:
        """問題文作成を実行する"""
        problem_ids: list[str] = self.problemset_config.get_problem_ids()
        self.task_runner.run(
            problem_ids=problem_ids,
            output_ext=self._ext,
            make_problemset=make_problemset,
            force_dump=force_dump,
            constraints_only=constraints_only,
        )

    def _fetch_problemset_config(
        self,
    ) -> ProblemSetConfig:
        """problem.toml が含まれているディレクトリを問題ディレクトリとみなす
        問題ごとに設定ファイルを読み込む
        """
        problemset_config_filename = self._cwd / "problemset.toml"
        problemset_config_dict = read_toml_file(problemset_config_filename)
        problemset_config = ProblemSetConfig(
            problemset_config_filename, problemset_config_dict
        )
        for problem_file in sorted(self._cwd.glob("./**/problem.toml")):
            problemset_config.add_problem_configs(problem_file)
        return problemset_config
