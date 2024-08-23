# coding:utf-8

import os
import shutil
from typing import Dict
from typing import List
from typing import Optional

from podman import PodmanClient
from podman.domain.containers import Container
from xmanage import systemd_path
from xmanage import systemd_service

UID: int = os.getuid()
CMD: Optional[str] = shutil.which("podman")


class podman_container:
    '''Manage podman container
    '''
    URI: str = f"unix:///run/user/{UID}/podman/podman.sock"

    def __init__(self, container_name: str):
        assert isinstance(container_name, str)
        self.__client: Optional[PodmanClient] = None
        self.__container: Optional[Container] = None
        self.__container_name: str = container_name

    @property
    def client(self) -> PodmanClient:
        if self.__client is None:
            self.__client = PodmanClient(base_url=self.URI)
        return self.__client

    @property
    def container(self) -> Container:
        if self.__container is None:
            self.__container = self.client.containers.get(self.container_name)
        return self.__container

    @property
    def container_name(self) -> str:
        return self.__container_name

    def inspect(self) -> Dict[str, str]:
        return self.container.inspect()

    @property
    def PidFile(self) -> str:
        return self.container.inspect()["PidFile"]

    @property
    def service_unit(self) -> str:
        return f"container-{self.container_name}.service"

    @property
    def service_path(self) -> str:
        return os.path.join(systemd_path.systemd_system_conf_dir, self.service_unit)  # noqa

    def stop_service(self) -> int:
        return os.system(f"systemctl stop {self.service_unit}")

    def generate_service(self, restart_policy: str = "on-failure",
                         stop_timeout: int = 10) -> systemd_service:
        if not isinstance(CMD, str):
            raise FileNotFoundError("podman command not found")

        content: str = f"""
[Unit]
Description=Podman {self.service_unit}
Wants=network-online.target
After=network-online.target
RequiresMountsFor=/run/containers/storage

[Service]
Environment=PODMAN_SYSTEMD_UNIT=%n
Restart={restart_policy}
TimeoutStopSec=70
ExecStart={CMD} start {self.container_name}
ExecStop={CMD} stop -t {stop_timeout} {self.container_name}
ExecStopPost={CMD} stop -t {stop_timeout} {self.container_name}
PIDFile={self.PidFile}
Type=forking

[Install]
WantedBy=default.target
"""
        return systemd_service.from_string(content)

    def enable_service(self) -> int:
        self.generate_service().create_unit(systemd_path.systemd_system_conf_dir, self.service_unit)  # noqa
        errno = os.system(f"systemctl enable --now {self.service_unit}")
        if errno != 0:
            return errno
        return 0

    def disable_service(self) -> int:
        errno = os.system(f"systemctl stop {self.service_unit}")
        if errno != 0:
            return errno
        errno = os.system(f"systemctl disable {self.service_unit}")
        if errno != 0:
            return errno
        service_path: str = self.service_path
        if os.path.isfile(service_path):
            os.remove(service_path)
        return 0


class podman_cmd:
    '''Execute podman command
    '''

    def __init__(self):
        pass

    @classmethod
    def run(cls, *args: str) -> int:
        def exec(*cmds: str) -> int:
            cmd = " ".join([c for c in cmds if c is not None])
            assert isinstance(cmd, str)
            return os.system(cmd)

        if not isinstance(CMD, str):
            raise FileNotFoundError("podman command not found")

        cmds: List[str] = [CMD]
        cmds.extend([i for i in args if len(i) > 0])
        return exec(*cmds)

    @classmethod
    def system_prune(cls, all: bool = False, external: bool = False,
                     force: bool = False, volumes: bool = False) -> int:
        return cls.run("system", "prune")
