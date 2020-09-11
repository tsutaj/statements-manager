import argparse
import toml
import pathlib
from logging import Logger, basicConfig, getLogger
from typing import Any, MutableMapping

logger = getLogger(__name__)  # type: Logger

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--project",
        type=str,
        default="./config/default.toml",
        help="Path to project file"
    )
    return parser


class ProjectFile:
    def __init__(self, project_path: str, default_project_path: str) -> None:
        self._project = toml.load(project_path)  # type: MutableMapping[str, Any]
        self._default = toml.load(default_project_path)  # type: MutableMapping[str, Any]
        
    def get_attr(self, attr: str, raise_error: bool=False) -> Any:
        if attr not in self._project:
            if raise_error:
                raise KeyError("a key is not in project:", attr)
            elif attr in self._default:
                logger.warning("'{}' key is not in project. use default value.".format(attr))
                return self._default[attr]
            else:
                raise KeyError("unknown key:", attr)
        else:
            return self._project[attr]


def run(project_path: str, default_project_path: str) -> None:
    project = ProjectFile(project_path, default_project_path)  # type: MutableMapping[str, Any]

    # check mode
    mode = project.get_attr("mode").lower()  # type: str
    if mode == "docs":
        raise NotImplementedError("docs mode is not supported yet")
    elif mode == "local":
        raise NotImplementedError("local mode is not supported yet")
    else:
        raise ValueError("unknown mode: {}".format(mode))


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    run(project_path=args.project, default_project_path="./config/default.toml")
