# coding:utf-8

import os
from typing import Any

import yaml


def safe_load_data(filepath: str) -> str:
    assert isinstance(filepath, str)
    assert os.path.isfile(filepath), f"No such file '{filepath}'"
    with open(filepath, "r", encoding="utf-8") as stream:
        return stream.read()


def safe_load_file(filepath: str) -> Any:
    return yaml.safe_load(safe_load_data(filepath))


def safe_dump_data(data: Any) -> str:
    return yaml.safe_dump(data, allow_unicode=True, indent=2, sort_keys=False)


def safe_dump_file(filepath: str, data: Any):
    assert isinstance(filepath, str)
    with open(filepath, "w", encoding="utf-8") as stream:
        stream.write(safe_dump_data(data))
