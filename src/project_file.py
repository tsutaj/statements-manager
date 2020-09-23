import toml
from typing import Any

class ProjectFile:
    def __init__(self, project_path: str, default_project_path: str) -> None:
        self._project = toml.load(project_path)  # type: MutableMapping[str, Any]
        self._default = toml.load(
            default_project_path
        )  # type: MutableMapping[str, Any]

    def get_attr(self, attr: str, raise_error: bool = False) -> Any:
        if attr not in self._project:
            if raise_error:
                raise KeyError("a key is not in project:", attr)
            elif attr in self._default:
                logger.warning(
                    "'{}' key is not in project. use default value.".format(attr)
                )
                return self._default[attr]
            else:
                raise KeyError("unknown key:", attr)
        else:
            return self._project[attr]
