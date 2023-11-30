# coding:utf-8

import hashlib
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from podman_compose import norm_re
from podman_compose import parse_short_mount
import yaml


def default_project_name(basedir: str):
    assert isinstance(basedir, str)
    assert os.path.isdir(basedir)
    realpath = os.path.realpath(basedir)
    basename = os.path.basename(realpath)
    return norm_re.sub("", basename.lower())


class compose_volume:
    KEY_NAME = "name"
    KEY_EXTERNAL = "external"

    def __init__(self, volumes, title: str):
        assert isinstance(volumes, compose_volumes)
        volumes.content.setdefault(title, {})
        if volumes.content[title] is None:
            volumes.content[title] = {}
        value = volumes.content[title]
        assert isinstance(title, str)
        assert isinstance(value, dict)
        self.__root: compose_file = volumes.root
        self.__volumes: compose_volumes = volumes
        self.__title: str = title
        self.__value: Dict[str, Any] = value

    @property
    def root(self):
        return self.__root

    @property
    def volumes(self):
        return self.__volumes

    @property
    def title(self) -> str:
        return self.__title

    @property
    def value(self) -> Dict:
        return self.__value

    @property
    def name(self) -> Optional[str]:
        name = self.__value.get(self.KEY_NAME, None)
        assert isinstance(name, str) or name is None
        return name

    @property
    def external(self) -> Optional[Dict]:
        external = self.__value.get(self.KEY_EXTERNAL, None)
        assert isinstance(external, Dict) or external is None
        return external


class compose_volumes:
    KEY = "volumes"

    def __init__(self, root):
        assert isinstance(root, compose_file)
        root.content.setdefault(self.KEY, {})
        volumes = root.content.get(self.KEY)
        assert isinstance(volumes, Dict)
        self.__root: compose_file = root
        self.__content: Dict[str, Any] = volumes
        self.__volumes: Dict[str, compose_volume] = {
            title: compose_volume(self, title) for title in volumes
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

    @property
    def root(self):
        return self.__root

    @property
    def content(self) -> Dict[str, Any]:
        assert isinstance(self.__content, dict)
        return self.__content


class compose_network:

    def __init__(self, networks, title: str):
        assert isinstance(networks, compose_networks)
        networks.content.setdefault(title, {})
        if networks.content[title] is None:
            networks.content[title] = {}
        value = networks.content[title]
        assert isinstance(title, str)
        assert isinstance(value, dict)
        self.__root: compose_file = networks.root
        self.__networks: compose_networks = networks
        self.__title: str = title
        self.__value: Dict[str, Any] = value

    @property
    def root(self):
        return self.__root

    @property
    def networks(self):
        return self.__networks

    @property
    def title(self) -> str:
        return self.__title

    @property
    def value(self) -> Dict:
        return self.__value


class compose_networks:
    KEY = "networks"

    def __init__(self, root):
        assert isinstance(root, compose_file)
        root.content.setdefault(self.KEY, {})
        networks = root.content.get(self.KEY)
        assert isinstance(networks, Dict)
        self.__root: compose_file = root
        self.__content: Dict[str, Any] = networks
        self.__networks: Dict[str, compose_network] = {
            title: compose_network(self, title) for title in networks
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

    @property
    def root(self):
        return self.__root

    @property
    def content(self) -> Dict[str, Any]:
        assert isinstance(self.__content, dict)
        return self.__content


class service_volume:
    '''
    Short syntax: [SOURCE:]TARGET[:MODE]

    Long syntax: Added in version 3.2 file format.
    https://docs.docker.com/compose/compose-file/compose-file-v3/#long-syntax-3
    '''

    KEY_TYPE = "type"
    KEY_SOURCE = "source"
    KEY_TARGET = "target"
    KEY_READ_ONLY = "read_only"

    def __init__(self, volumes, value: Union[str, Dict[str, Any]]):
        assert isinstance(volumes, service_volumes)
        assert isinstance(value, str) or isinstance(value, dict)
        service = volumes.service
        self.__root: compose_file = service.root
        self.__service: compose_service = service
        self.__volumes: service_volumes = volumes
        self.__value: Union[str, Dict[str, Any]] = value
        if isinstance(value, str):
            short = parse_short_mount(value, self.__root.basedir)
            assert isinstance(short, dict)
            self.__short = short

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
    def volumes(self):
        return self.__volumes

    @property
    def value(self) -> Union[str, Dict[str, Any]]:
        return self.__value

    @value.setter
    def value(self, new: Union[str, Dict[str, Any]]):
        if isinstance(new, str):
            short = parse_short_mount(new, self.__root.basedir)
            assert isinstance(short, dict)
            self.__short = short
        self.__value = new
        self.volumes.update()

    @property
    def generic(self) -> Dict[str, Any]:
        return self.__short if isinstance(self.__value, str) else self.__value

    @property
    def type(self) -> str:
        '''
        "bind", "volume"
        '''
        type = self.generic.get(self.KEY_TYPE, None)
        assert isinstance(type, str)
        return type

    @property
    def source(self) -> str:
        source = self.generic.get(self.KEY_SOURCE, None)
        assert isinstance(source, str)
        return source

    @property
    def target(self) -> str:
        target = self.generic.get(self.KEY_TARGET, None)
        assert isinstance(target, str)
        return target

    @property
    def read_only(self) -> bool:
        '''
        default read-write(rw)
        '''
        read_only = self.generic.get(self.KEY_READ_ONLY, False)
        assert isinstance(read_only, bool)
        return read_only

    @property
    def volume_name(self) -> Optional[str]:
        return self.__get_volume_name()


class service_volumes:
    KEY = "volumes"

    def __init__(self, service):
        assert isinstance(service, compose_service)
        service.value.setdefault(self.KEY, [])
        volumes = service.value.get(self.KEY)
        assert isinstance(volumes, list)
        self.__service: compose_service = service
        self.__content: List[Union[str, Dict[str, Any]]] = volumes
        self.__volumes = [service_volume(self, vol) for vol in volumes]

    def __iter__(self):
        return iter(self.__volumes)

    @property
    def service(self):
        return self.__service

    def update(self):
        self.__content.clear()
        for volume in self.__volumes:
            self.__content.append(volume.value)

    def append(self, value: Union[str, Dict[str, Any]]):
        volume = service_volume(self, value)
        self.__volumes.append(volume)
        self.__content.append(value)


class service_deploy:
    KEY = "deploy"
    KEY_REPLICAS = "replicas"

    def __init__(self, service):
        assert isinstance(service, compose_service)
        service.value.setdefault(self.KEY, {})
        deploy = service.value.get(self.KEY)
        assert isinstance(deploy, dict)
        self.__service: compose_service = service
        self.__content: Dict[str, Any] = deploy

    @property
    def service(self):
        return self.__service

    @property
    def replicas(self) -> int:
        return int(self.__content.get(self.KEY_REPLICAS, 1))


class compose_service:
    KEY_CONTAINER_NAME = "container_name"
    KEY_RESTART = "restart"

    def __init__(self, services, title: str):
        assert isinstance(services, compose_services)
        services.content.setdefault(title, {})
        if services.content[title] is None:
            services.content[title] = {}
        value = services.content[title]
        assert isinstance(title, str)
        assert isinstance(value, dict)
        self.__root: compose_file = services.root
        self.__services: compose_services = services
        self.__title: str = title
        self.__value: Dict[str, Any] = value
        self.__volumes = service_volumes(self)
        self.__deploy = service_deploy(self)

    @property
    def root(self):
        return self.__root

    @property
    def services(self):
        return self.__services

    @property
    def title(self) -> str:
        return self.__title

    @property
    def value(self) -> Dict:
        return self.__value

    @property
    def container_name(self) -> str:
        '''
        Same as container_names_by_service in
        podman_compose._parse_compose_file()
        '''
        project_name = self.__root.project_name
        default = f"{project_name}_{self.title}_{self.deploy.replicas}"
        name = self.__value.get(self.KEY_CONTAINER_NAME, default)
        assert isinstance(name, str)
        return name if self.deploy.replicas == 1 else default

    @property
    def restart(self) -> str:
        return self.__value.get(self.KEY_RESTART, "no")

    @restart.setter
    def restart(self, value: str):
        assert value in {"no", "always", "on-failure", "unless-stopped"}
        self.__value[self.KEY_RESTART] = value

    @property
    def volumes(self) -> service_volumes:
        return self.__volumes

    @volumes.setter
    def volumes(self, value: service_volumes):
        if isinstance(value, service_volumes):
            self.__volumes = value

    @property
    def deploy(self) -> service_deploy:
        return self.__deploy

    def mount(self, source: str, target: str, read_only: bool):
        mode = "ro" if read_only else "rw"
        for volume in self.volumes:
            if volume.source != source:
                continue
            if volume.target != target:
                continue
            if volume.read_only != read_only:
                volume.value = f"{source}:{target}:{mode}"
            return
        self.volumes.append(f"{source}:{target}:{mode}")


class compose_services:
    KEY = "services"

    def __init__(self, root):
        assert isinstance(root, compose_file)
        root.content.setdefault(self.KEY, {})
        services = root.content.get(self.KEY)
        assert isinstance(services, Dict)
        self.__root: compose_file = root
        self.__content: Dict[str, Any] = services
        self.__services: Dict[str, compose_service] = {
            title: compose_service(self, title) for title in services
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

    @property
    def root(self):
        return self.__root

    @property
    def content(self) -> Dict[str, Any]:
        assert isinstance(self.__content, dict)
        return self.__content


class compose_file:
    '''
    For more, please visit https://docs.docker.com/compose/compose-file

    2.x: https://docs.docker.com/compose/compose-file/compose-file-v2
    3.x: https://docs.docker.com/compose/compose-file/compose-file-v3
    '''

    def __init__(self, basedir: str, project_name: str, compose_yaml: str):
        assert isinstance(basedir, str)
        assert isinstance(project_name, str)
        assert isinstance(compose_yaml, str)
        self.__basedir = basedir
        self.__project_name = project_name
        self.__content: Dict[str, Any] = yaml.safe_load(compose_yaml)
        self.__volumes = compose_volumes(self)
        self.__networks = compose_networks(self)
        self.__services = compose_services(self)

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def basedir(self) -> str:
        return self.__basedir

    @property
    def content(self) -> Dict[str, Any]:
        assert isinstance(self.__content, dict)
        return self.__content

    @property
    def volumes(self) -> compose_volumes:
        return self.__volumes

    @property
    def networks(self) -> compose_networks:
        return self.__networks

    @property
    def services(self) -> compose_services:
        return self.__services

    def dump(self) -> Dict[str, Any]:
        return self.content
