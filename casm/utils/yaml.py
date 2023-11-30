# coding:utf-8

import os
from string import Template
from typing import Any
from typing import Dict

import yaml


def safe_load_tmpl(filepath: str, variables: Dict[str, str]) -> str:
    assert type(filepath) is str
    assert os.path.isfile(filepath), f"No such file '{filepath}'"
    with open(filepath, "r", encoding="utf-8") as handle:
        return Template(handle.read()).substitute(variables)


def safe_load_yaml(filepath: str) -> Any:
    assert isinstance(filepath, str)
    assert os.path.isfile(filepath), f"No such file '{filepath}'"
    with open(filepath, "r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def safe_dump_yaml(filepath: str, data: Any):
    assert isinstance(filepath, str)
    with open(filepath, "w", encoding="utf-8") as stream:
        dump: str = yaml.safe_dump(data, allow_unicode=True,
                                   indent=2, sort_keys=False)
        stream.write(dump)
