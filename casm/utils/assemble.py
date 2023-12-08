# coding:utf-8

import os
from string import Template
from typing import Any
from typing import Dict
from typing import Optional

from podman_compose import norm_re

from .compose import compose_file
from .yaml import safe_dump_file
from .yaml import safe_load_data
from .yaml import safe_load_file


def default_project_name(filepath: str):
    assert isinstance(filepath, str)
    # assert os.path.isfile(filepath)
    basename, _ = os.path.basename(filepath).split(".", 1)
    return norm_re.sub("", basename.lower())


class assemble_variables(Dict[str, str]):
    KEY_PROJECT_NAME = "COMPOSE_PROJECT_NAME"

    def __init__(self, variables: Optional[Dict[str, str]]):
        if variables is None:
            variables = dict()
        assert isinstance(variables, dict)
        vars = {k: v for k, v in os.environ.items()}
        for k, v in variables.items():
            assert v is not None, f'variable "{k}" not set'
            assert isinstance(v, str), f"{type(v)} not str"
            vars[k] = Template(v).safe_substitute(vars)
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
    DEF_TEMPLATE_FILE = "template.yml"

    KEY_VARIABLES = "variables"
    KEY_PROJECT_NAME = "project-name"
    KEY_TEMPLATE_FILE = "template-file"

    def __init__(self, filepath: str = DEF_CONFIG_FILE,
                 project_name: Optional[str] = None,
                 template_file: Optional[str] = None):
        assert isinstance(filepath, str)
        if project_name is None:
            project_name = default_project_name(filepath)
        assert isinstance(template_file, str) or template_file is None
        self.__abspath = os.path.abspath(filepath)
        self.__basedir = os.path.dirname(self.__abspath)
        self.__filepath = filepath
        self.__template_file = template_file
        data = safe_load_file(filepath) if os.path.isfile(filepath) else dict()
        self.__assemble: Dict[str, Any] = dict() if data is None else data
        self.__project_name: str = self.__assemble.get(self.KEY_PROJECT_NAME,
                                                       project_name)
        assert isinstance(self.__project_name, str)
        os.environ[assemble_variables.KEY_PROJECT_NAME] = self.__project_name
        vars: Dict[str, str] = self.__assemble.get(self.KEY_VARIABLES, {})
        self.__variables: assemble_variables = assemble_variables(vars)
        tmpl: str = safe_load_data(self.template_file)
        self.__template = compose_file(self.__basedir, self.project_name, tmpl)

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def template_file(self) -> str:
        if self.__template_file is not None:
            return self.abspath(self.safe_substitute(self.__template_file))
        path: str = self.__assemble.get(self.KEY_TEMPLATE_FILE,
                                        self.DEF_TEMPLATE_FILE)
        return self.abspath(self.safe_substitute(path))

    @property
    def variables(self) -> assemble_variables:
        return self.__variables

    @property
    def template(self) -> compose_file:
        return self.__template

    def abspath(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.abspath(os.path.join(self.__basedir, path))

    def substitute(self, value: str) -> str:
        return Template(value).substitute(self.variables)

    def safe_substitute(self, value: str) -> str:
        return Template(value).safe_substitute(self.variables)

    def dump_template(self, filepath: Optional[str] = None):
        safe_dump_file(filepath if isinstance(filepath, str)
                       else self.template_file, self.template.dump())
