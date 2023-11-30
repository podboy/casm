# coding:utf-8

import os
from string import Template
from typing import Any
from typing import Dict
from typing import Optional

from podman_compose import norm_re

from .compose import compose_file as compose
from .yaml import safe_dump_file
from .yaml import safe_load_data
from .yaml import safe_load_file


def default_project_name(filepath: str):
    assert isinstance(filepath, str)
    assert os.path.isfile(filepath)
    basename, _ = os.path.basename(filepath).split(".", 1)
    return norm_re.sub("", basename.lower())


class assemble_variables(Dict[str, str]):
    KEY_PROJECT_NAME = "COMPOSE_PROJECT_NAME"

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
            os.environ[k] = v

    def __iter__(self):
        return iter(os.environ.keys())

    def __getitem__(self, key: str) -> Optional[str]:
        return os.environ.get(key, None)

    def __setitem__(self, key: str, value: str):
        assert isinstance(value, str), f"{type(value)} not str"
        value = Template(value).safe_substitute(os.environ)
        os.environ[key] = value

    def __delitem__(self, key: str):
        if key in os.environ:
            del os.environ[key]


class assemble_file:
    '''
    assemble file, default assemble.yml
    '''

    DEF_CONFIG_FILE = "assemble.yml"
    DEF_TEMPLATE_FILE = "compose.yml"
    DEF_COMPOSE_FILE = "docker-compose.yml"

    KEY_VARIABLES = "variables"
    KEY_PROJECT_NAME = "project-name"
    KEY_TEMPLATE_FILE = "template-file"
    KEY_COMPOSE_FILE = "compose-file"

    def __init__(self, filepath: str = DEF_CONFIG_FILE,
                 project_name: Optional[str] = None,
                 template_file: Optional[str] = None,
                 compose_file: Optional[str] = None):
        assert isinstance(filepath, str)
        if project_name is None:
            project_name = default_project_name(filepath)
        assert isinstance(template_file, str) or template_file is None
        assert isinstance(compose_file, str) or compose_file is None
        self.__abspath = os.path.abspath(filepath)
        self.__basedir = os.path.dirname(self.__abspath)
        self.__filepath = filepath
        self.__template_file = template_file
        self.__compose_file = compose_file
        self.__assemble: Dict[str, Any] = safe_load_file(self.__filepath)
        self.__project_name: str = self.__assemble.get(self.KEY_PROJECT_NAME,
                                                       project_name)
        assert isinstance(self.__project_name, str)
        os.environ[assemble_variables.KEY_PROJECT_NAME] = self.__project_name
        vars: Dict[str, str] = self.__assemble.get(self.KEY_VARIABLES, {})
        self.__variables: Dict[str, str] = assemble_variables(vars)
        tmpl: str = safe_load_data(self.template_file)
        self.__compose = compose(self.__basedir, self.project_name, tmpl)

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def template_file(self) -> str:
        if self.__template_file is not None:
            return self.abspath(self.__template_file)
        path: str = self.__assemble.get(self.KEY_TEMPLATE_FILE,
                                        self.DEF_TEMPLATE_FILE)
        return self.abspath(path)

    @property
    def compose_file(self) -> str:
        if self.__compose_file is not None:
            return self.abspath(self.__compose_file)
        path: str = self.__assemble.get(self.KEY_COMPOSE_FILE,
                                        self.DEF_COMPOSE_FILE)
        return self.abspath(path)

    @property
    def variables(self) -> Dict[str, str]:
        return self.__variables

    @property
    def compose(self) -> compose:
        return self.__compose

    def abspath(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.abspath(os.path.join(self.__basedir, path))

    def dump_compose(self, filepath: Optional[str] = None):
        safe_dump_file(filepath if isinstance(filepath, str)
                       else self.compose_file, self.compose.dump())
