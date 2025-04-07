from pathlib import Path
from typing import TypedDict, Any
from pprint import pformat
import tomllib

from logger import logger, _


class Config(TypedDict):
    # APP
    PROJECT_NAME: str
    PROJECT_VERSION: str
    LOGGING_LEVEL: str
    LOGGING_TO_FILE: bool
    SHOW_MESSAGES: bool
    FINISH_AFTER_SUCCESS: bool

    # IMPORT FILES
    DATA_DIR: Path
    DATA_NAME: str
    DATA_PATH: Path
    DOC_TEMPLATES_FILES: list[tuple[str, str, str]]
    DOC_TEMPLATES_DIR: Path
    DOC_TEMPLATE_LABEL: str
    DOC_TEMPLATE_NAME: str
    DOC_TEMPLATE_PATH: Path
    DOC_TEMPLATE_PREFIX: str
    DOC_NUM: str

    # EXPORT FILES
    PDF_DIR: Path
    PDF_NAME_MASK: str

    # GUI ADDITIONAL VARIABLES
    EXECUTOR_LABEL: str
    EXECUTOR_DATA: dict[str, str]

    DATE_DAY: str
    DATE_MONTH_LABEL: str
    DATE_MONTH: str
    DATE_YEAR: str
    DATE_YEAR_MAX: int
    DATE_YEAR_MIN: int

    AMOUNT: str
    AMOUNT_INT: int
    AMOUNT_TEXT: str
    CURRENCY_PLURALIZE: list[str]


def config_init(config: dict[str, Any]) -> Config:
    for key in list(config.keys()):
        config[key.upper()] = config.pop(key)

    for name_path in ["PDF_DIR", "DOC_TEMPLATES_DIR", "DATA_DIR"]:
        config[name_path] = Path(config[name_path])

    config["DATA_PATH"] = config["DATA_DIR"] / config["DATA_NAME"]

    logger.debug("Config initialized")
    logger.debug("Config:\n{config}".format(config=pformat(config)))
    return Config(**config)  # type: ignore


def load_config() -> Config:
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if not pyproject_path.exists():
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    pyproject_content = pyproject_path.read_text()
    config = tomllib.loads(pyproject_content)

    tool_config = config.get("tool", {}).get("doc_fill_master", {})
    if not tool_config:
        raise KeyError(_("tool.doc_fill_master not found in pyproject.toml"))

    project_config = config.get("project", {})
    if not project_config:
        raise KeyError(_("project not found in pyproject.toml"))

    for key in list(project_config.keys()):
        project_config[f"PROJECT_{key.upper()}"] = project_config.pop(key)

    app_config = config_init(project_config | tool_config)
    logger.debug('Config loaded from "{path}"'.format(path=pyproject_path))
    return app_config
