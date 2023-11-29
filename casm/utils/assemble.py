# coding:utf-8

import os
from string import Template
from typing import Any
from typing import Dict
from typing import Optional

from podman_compose import norm_re

from .compose import compose_file as compose
from .yaml import safe_dump_yaml
from .yaml import safe_load_tmpl
from .yaml import safe_load_yaml


def default_project_name(filepath: str):
    assert isinstance(filepath, str)
    assert os.path.isfile(filepath)
    basename, _ = os.path.basename(filepath).split(".", 1)
    return norm_re.sub("", basename.lower())


class assemble_variables(Dict[str, str]):

    def __init__(self, variables: Dict[str, str]):
        assert isinstance(variables, dict)
        vars = {k: v for k, v in os.environ.items()}
        for k, v in variables.items():
            assert v is not None, f'variable "{k}" not set'
            assert isinstance(v, str), f"{type(v)} not str"
            try:
                value = Template(v).safe_substitute(vars)
            except KeyError:
                raise KeyError(f"variable {k}: {v}")
            vars[k] = value
        for k, v in vars.items():
            assert isinstance(k, str), f"{type(k)} not str"
            assert isinstance(v, str), f"{type(v)} not str"
        self.__variables = vars

    def __iter__(self):
        return iter(self.__variables.keys())

    def __getitem__(self, key: str) -> Optional[str]:
        return self.__variables.get(key, None)

    def __setitem__(self, key: str, value: str):
        assert isinstance(value, str), f"{type(value)} not str"
        value = Template(value).safe_substitute(self.__variables)
        self.__variables[key] = value

    def __delitem__(self, key: str):
        if key in self.__variables:
            del self.__variables[key]


class assemble_file:
    '''
    assemble.yml
    '''

    DEF_CONFIG_FILE = "assemble.yml"
    DEF_TEMPLATE_FILE = "compose.yml"
    DEF_COMPOSE_FILE = "docker-compose.yml"

    KEY_VARIABLES = "variables"
    KEY_PROJECT_NAME = "project-name"
    KEY_TEMPLATE_FILE = "template-file"
    KEY_COMPOSE_FILE = "compose-file"

    def __init__(self, filepath: str = DEF_CONFIG_FILE):
        assert isinstance(filepath, str)
        self.__filepath = filepath
        self.__projname = default_project_name(filepath)
        self.__realpath = os.path.realpath(filepath)
        self.__basedir = os.path.dirname(self.__realpath)
        self.__assemble: Dict[str, Any] = safe_load_yaml(self.__filepath)
        vars: Dict[str, Any] = self.__assemble.get(self.KEY_VARIABLES, {})
        self.__variables: Dict[str, Any] = assemble_variables(vars)
        tmpl: str = safe_load_tmpl(self.template_file, self.__variables)
        self.__compose = compose(self.__basedir, self.project_name, tmpl)

    @property
    def project_name(self) -> str:
        return self.__assemble.get(self.KEY_PROJECT_NAME, self.__projname)

    @property
    def template_file(self) -> str:
        return self.__assemble.get(self.KEY_TEMPLATE_FILE,
                                   self.DEF_TEMPLATE_FILE)

    @property
    def compose_file(self) -> str:
        return self.__assemble.get(self.KEY_COMPOSE_FILE,
                                   self.DEF_COMPOSE_FILE)

    @property
    def compose(self) -> compose:
        return self.__compose

    def dump(self, filepath: Optional[str] = None):
        safe_dump_yaml(filepath if isinstance(filepath, str)
                       else self.compose_file, self.compose.dump())
