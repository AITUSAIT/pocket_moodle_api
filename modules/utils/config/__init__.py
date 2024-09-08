import os
from typing import Any

from . import exceptions
from .exceptions import ConfigFieldIsRequired, ConfigFieldWrongType


def get_from_env(field: str, default: Any | None = None, value_type: type[str | int | Any] = str) -> int | str | Any:
    value = os.getenv(field, default)
    if value is None and default is None:
        raise ConfigFieldIsRequired(field)

    if not isinstance(value, value_type):
        if isinstance(value, str) and value_type is int:
            try:
                return int(value)
            except Exception as exc:
                raise ConfigFieldWrongType(field, value, value_type) from exc
        raise ConfigFieldWrongType(field, value, value_type)

    return value


__all__ = ["get_from_env", "exceptions"]
