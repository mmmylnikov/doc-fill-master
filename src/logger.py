import gettext
import logging
import tomllib
from pathlib import Path


def load_config() -> dict:
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    if not pyproject_path.exists():
        pyproject_path = Path(__file__).parent / "pyproject.toml"
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    pyproject_content = pyproject_path.read_text()
    config = tomllib.loads(pyproject_content)

    tool_config = config.get("tool", {}).get("doc_fill_master", {})
    if not tool_config:
        raise KeyError("tool.doc_fill_master not found in pyproject.toml")

    project_config = config.get("project", {})
    if not project_config:
        raise KeyError("project not found in pyproject.toml")
    log_config = project_config | tool_config
    return log_config


log_config = load_config()
lang_name = log_config["language"]
lang = gettext.translation(
    "messages", localedir="translations", languages=[lang_name]
)
lang.install()
_ = lang.gettext

logger_level = log_config["logging_level"]

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, logger_level))

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

if log_config["logging_to_file"]:
    ligging_file_name = log_config["logging_file_name"]
    logging_file_dir = log_config["logging_file_dir"]
    logging_file_path = Path(logging_file_dir) / ligging_file_name
    file_handler = logging.FileHandler(logging_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

logger.info(_("Logger initialized"))
