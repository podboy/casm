# coding:utf-8

import hashlib
import os
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

from podman_compose import norm_re
from podman_compose import parse_short_mount
import yaml


def default_project_name(compose_file: str):
    realpath = os.path.realpath(compose_file)
    dirname = os.path.dirname(realpath)
    basename = os.path.basename(dirname)
    return norm_re.sub("", basename.lower())


class compose_volume:

    def __init__(self, root, title: str, value: Dict):
        assert isinstance(root, compose_file)
        assert isinstance(title, str)
        assert isinstance(value, Dict)
        self.__root = root
        self.__title = title
        self.__value = value

    @property
    def title(self) -> str:
        return self.__title

    @property
    def value(self) -> Dict:
        return self.__value

    @property
    def name(self) -> Optional[str]:
        name = self.__value.get("name", None)
        assert isinstance(name, str) or name is None
        return name

    @property
    def external(self) -> Optional[Dict]:
        external = self.__value.get("external", None)
        assert isinstance(external, Dict) or external is None
        return external


class compose_volumes:

    def __init__(self, root):
        assert isinstance(root, compose_file)
        volumes = root.content.get("volumes", {})
        assert isinstance(volumes, Dict)
        self.__root = root
        self.__volumes = {
            title: compose_volume(self.__root, title, value)
            for title, value in volumes.items()
        }

    def __iter__(self):
        return iter(self.__volumes.values())

    def __getitem__(self, title: str) -> Optional[compose_volume]:
        return self.__volumes.get(title, None)

    def __setitem__(self, title: str, value: compose_volume):
        assert isinstance(value, compose_network)
        self.__volumes[title] = value

    def __delitem__(self, title: str):
        if title in self.__volumes:
            del self.__volumes[title]


class compose_network:

    def __init__(self, root, title: str, value: Dict):
        assert isinstance(root, compose_file)
        assert isinstance(title, str)
        assert isinstance(value, Dict)
        self.__root = root
        self.__title = title
        self.__value = value

    @property
    def title(self) -> str:
        return self.__title

    @property
    def value(self) -> Dict:
        return self.__value


class compose_networks:

    def __init__(self, root):
        assert isinstance(root, compose_file)
        networks = root.content.get("networks", {})
        assert isinstance(networks, Dict)
        self.__root = root
        self.__networks = {
            title: compose_network(self.__root, title, value)
            for title, value in networks.items()
        }

    def __iter__(self):
        return iter(self.__networks.values())

    def __getitem__(self, title: str) -> Optional[compose_network]:
        return self.__networks.get(title, None)

    def __setitem__(self, title: str, value: compose_network):
        assert isinstance(value, compose_network)
        self.__networks[title] = value

    def __delitem__(self, title: str):
        if title in self.__networks:
            del self.__networks[title]


class service_volume:

    def __init__(self, root, service, value):
        assert isinstance(root, compose_file)
        assert isinstance(service, compose_service)
        assert isinstance(value, str)
        self.__root = root
        self.__service = service
        self.__value = value
        self.__mount = parse_short_mount(value, root.dirname)
        assert isinstance(self.__mount, dict)
        self.__volume_name = self.__get_volume_name()

    def __get_volume_name(self) -> Optional[str]:
        '''
        Same as podman_compose.fix_mount_dict()
        '''
        __volume_name = None
        if self.type == "volume":
            source = self.source
            _volume = None
            for vol in self.__root.volumes:
                if vol.title == source:
                    _volume = vol
                    break
            assert isinstance(_volume, compose_volume)
            # self.__volume = _volume
            name = _volume.name
            if not source:
                __volume_name = "_".join([
                    self.__root.project_name,
                    self.__service.title,
                    hashlib.sha256(self.target.encode("utf-8")).hexdigest(),
                ])
            elif not name:
                assert isinstance(source, str)
                external = _volume.external
                if isinstance(external, dict):
                    __volume_name = external.get("name", source)
                elif external:
                    __volume_name = f"{source}"
                else:
                    __volume_name = f"{self.__root.project_name}_{source}"
            else:
                __volume_name = name
        return __volume_name

    @property
    def value(self) -> str:
        return self.__value

    @property
    def type(self) -> str:
        type = self.__mount.get("type", None)
        assert isinstance(type, str)
        return type

    @property
    def source(self) -> str:
        source = self.__mount.get("source", None)
        assert isinstance(source, str)
        return source

    @property
    def target(self) -> str:
        target = self.__mount.get("target", None)
        assert isinstance(target, str)
        return target

    @property
    def read_only(self) -> Optional[bool]:
        read_only = self.__mount.get("read_only", None)
        assert isinstance(read_only, bool) or read_only is None
        return read_only

    @property
    def volume_name(self) -> Optional[str]:
        return self.__volume_name


class service_volumes:

    def __init__(self, root, service, value: List[str]):
        assert isinstance(root, compose_file)
        assert isinstance(service, compose_service)
        assert isinstance(value, list)
        self.__root = root
        self.__service = service
        self.__volumes = [
            service_volume(self.__root, self.__service, vol) for vol in value
        ]

    def __iter__(self):
        return iter(self.__volumes)

    @property
    def value(self) -> List[str]:
        return [volume.value for volume in self.__volumes]

    @value.setter
    def value(self, value: List[str]):
        assert isinstance(value, list)
        self.__volumes = [
            service_volume(self.__root, self.__service, vol) for vol in value
        ]


class compose_service:

    def __init__(self, root, title: str, value: Dict, replica: int = 1):
        assert isinstance(root, compose_file)
        assert isinstance(title, str)
        assert isinstance(value, Dict)
        self.__root = root
        self.__title = title
        self.__value = value
        self.__replica = replica
        self.__volumes = service_volumes(self.__root, self,
                                         self.__value.get("volumes", []))

    @property
    def title(self) -> str:
        return self.__title

    @property
    def value(self) -> Dict:
        return self.__value

    @property
    def replica(self) -> int:
        return self.__replica

    @property
    def container_name(self) -> str:
        '''
        Same as container_names_by_service in
        podman_compose._parse_compose_file()
        '''
        project_name = self.__root.project_name
        default_name = f"{project_name}_{self.title}_{self.replica}"
        container_name = self.__value.get("container_name", default_name)
        assert isinstance(container_name, str)
        return container_name if self.replica == 1 else default_name

    @property
    def volumes(self) -> service_volumes:
        return self.__volumes

    @volumes.setter
    def volumes(self, value: service_volumes):
        if isinstance(value, service_volumes):
            self.__volumes = value


class compose_services:

    def __init__(self, root):
        assert isinstance(root, compose_file)
        services = root.content.get("services", {})
        assert isinstance(services, Dict)
        self.__root = root
        self.__services = {
            title: compose_service(self.__root, title, value)
            for title, value in services.items()
        }

    def __iter__(self):
        return iter(self.__services.values())

    def __getitem__(self, title: str) -> Optional[compose_service]:
        return self.__services.get(title, None)

    def __setitem__(self, title: str, value: compose_service):
        assert isinstance(value, compose_service)
        self.__services[title] = value

    def __delitem__(self, title: str):
        if title in self.__services:
            del self.__services[title]


class compose_file:
    '''
    For more, please visit https://docs.docker.com/compose/compose-file

    2.x: https://docs.docker.com/compose/compose-file/compose-file-v2
    3.x: https://docs.docker.com/compose/compose-file/compose-file-v3
    '''

    def __init__(self, project_name: str, compose_file: str):
        assert isinstance(project_name, str)
        assert isinstance(compose_file, str)
        self.__project_name = project_name
        self.__compose_file = compose_file
        self.__realpath = os.path.realpath(compose_file)
        self.__dirname = os.path.basename(os.path.dirname(self.__realpath))
        self.__content: dict = self.__load(compose_file)
        self.__version: str = self.__content.get("version", "")
        assert isinstance(self.__version, str)
        self.__volumes = compose_volumes(self)
        self.__networks = compose_networks(self)
        self.__services = compose_services(self)

    def __load(self, file: str):
        with open(file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def compose_file(self) -> str:
        return self.__compose_file

    @property
    def dirname(self) -> str:
        return self.__dirname

    @property
    def content(self) -> Dict:
        assert isinstance(self.__content, Dict)
        return self.__content

    @property
    def version(self) -> str:
        assert isinstance(self.__version, str)
        return self.__version

    @property
    def volumes(self) -> compose_volumes:
        return self.__volumes

    @property
    def networks(self) -> compose_networks:
        return self.__networks

    @property
    def services(self) -> compose_services:
        return self.__services
