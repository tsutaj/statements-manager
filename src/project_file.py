import toml
from logging import Logger, getLogger
from typing import MutableMapping, Any

logger = getLogger(__name__)  # type: Logger


class ProjectFile:
    def __init__(self, project_path: str, default_toml: str) -> None:
        self._project = toml.load(project_path)  # type: MutableMapping[str, Any]
        self._default = toml.loads(default_toml)  # type: MutableMapping[str, Any]

    def get_attr(self, attr: str, raise_error: bool = False) -> Any:
        if attr not in self._project:
            if raise_error:
                logger.error("a key is not in project: {}".format(attr))
                raise KeyError("a key is not in project:", attr)
            elif attr in self._default:
                logger.warning(
                    "'{}' key is not in project. use default value.".format(attr)
                )
                return self._default[attr]
            else:
                logger.error("unknown key: {}".format(attr))
                raise KeyError("unknown key:", attr)
        else:
            return self._project[attr]
