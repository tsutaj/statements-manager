import toml
import copy
from logging import Logger, getLogger
from typing import MutableMapping, Any
from pathlib import Path
from .utils import resolve_path

logger = getLogger(__name__)  # type: Logger


class ProjectFile:
    def __init__(self, project_path: str, default_toml: str) -> None:
        if not Path(project_path).exists():
            logger.error(f"project {project_path} does not exist.")
            raise IOError(f"project {project_path} does not exist.")

        project = toml.load(project_path)  # type: MutableMapping[str, Any]
        default = toml.loads(default_toml)  # type: MutableMapping[str, Any]
        self._cwd = Path(project_path).parent.resolve()
        self._common_attr = self._merge_dict(project, default, self._cwd)
        self.problem_attr = self._search_problem_attr()

    def _merge_dict(
        self,
        lhs: MutableMapping[str, Any],
        rhs: MutableMapping[str, Any],
        base_path: Path,
    ) -> MutableMapping[str, Any]:
        """lhs に rhs の内容をマージする
        lhs にキーがあればそちらを優先し、なければ rhs の情報を用いる
        """
        result_dict = copy.deepcopy(rhs)
        result_dict.update(lhs)
        return self._to_absolute_path(result_dict, base_path)

    def _to_absolute_path(
        self, setting_dict: MutableMapping[str, Any], base_path: Path
    ) -> MutableMapping[str, Any]:
        """setting_dict に含まれているキーの中で
        '_path' で終わるもの全てに対して、値を絶対パスに変更 (既に絶対パスなら何もしない)
        """
        base_path = base_path.resolve()
        result_dict = copy.deepcopy(setting_dict)
        for k, v in result_dict.items():
            if k.endswith("_path"):
                result_dict[k] = resolve_path(base_path, Path(v))
        for k, v in result_dict.get("docs", {}).items():
            if k.endswith("_path"):
                result_dict["docs"][k] = resolve_path(base_path, Path(v))
        for k, v in result_dict.get("style", {}).items():
            if k.endswith("_path"):
                result_dict["style"][k] = resolve_path(base_path, Path(v))
            if k == "copied_files":
                for i in range(len(result_dict["style"][k])):
                    result_dict["style"][k][i] = resolve_path(
                        base_path, Path(result_dict["style"][k][i])
                    )
        return result_dict

    def _search_problem_attr(
        self,
    ) -> MutableMapping[str, Any]:
        """ss-config.toml が含まれているディレクトリを問題ディレクトリとみなす
        問題ごとに設定ファイルを読み込む
        """
        result_dict = {}  # type: MutableMapping[str, Any]
        for problem_file in sorted(self._cwd.glob("./**/ss-config.toml")):
            dir_name = problem_file.parent.resolve()
            problem_dict = toml.load(problem_file)
            if "id" not in problem_dict:
                logger.error(f"{problem_file} has not 'id' key.")
                raise KeyError(f"{problem_file} has not 'id' key.")
            elif problem_dict["id"] in result_dict:
                logger.error(f'problem id \'{problem_dict["id"]}\' appears twice')
                raise ValueError(f'problem id \'{problem_dict["id"]}\' appears twice')
            statement_path = problem_dict.get("statement_path")
            problem_id = problem_dict["id"]
            result_dict[problem_id] = self._to_absolute_path(
                problem_dict, problem_file.parent
            )
            result_dict[problem_id].update(self._common_attr)
            # docs モードのときはパスと解釈してはならない
            if problem_dict.get("mode") == "docs":
                result_dict[problem_id]["statement_path"] = statement_path
            # sample_path のデフォルトは ss-config.toml 内の tests ディレクトリ
            result_dict[problem_id].setdefault("sample_path", dir_name / Path("tests"))
            # output_path のデフォルトは ss-config.toml 内の ss-out ディレクトリ
            result_dict[problem_id].setdefault("output_path", dir_name / Path("ss-out"))
        return result_dict
