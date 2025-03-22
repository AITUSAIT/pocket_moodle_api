import json
import logging.config
from typing import Any


class Logger(logging.Logger):
    _config_loaded = False
    _config: dict[str, Any] = {}

    @classmethod
    def load_config(cls) -> None:
        if not cls._config_loaded:
            try:
                with open("logger_config.json", "r", encoding="UTF-8") as config_file:
                    cls._config = json.load(config_file)
                    cls._config_loaded = True
            except FileNotFoundError:
                cls._config = {}
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in config file")
            logging.config.dictConfig(cls._config)
