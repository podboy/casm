# coding:utf-8

import os
import shutil
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from podman import PodmanClient
from podman.domain.containers import Container
from xmanage import systemd_service

from .common import mountpoint

# UID: int = os.getuid()
CMD: Optional[str] = shutil.which("podman")


class podman_container_inspect:
    def __init__(self, container: Container):
        assert isinstance(container, Container)
        self.__container: Container = container
        self.__info: Dict[str, Any] = container.inspect()

    @property
    def container(self) -> Container:
        return self.__container

    @property
    def info(self) -> Dict[str, Any]:
        return self.__info

    @property
    def PidFile(self) -> str:
        return self.info["PidFile"]

    @property
    def HostConfig(self) -> Dict[str, Any]:
        return self.info["HostConfig"]

    @property
    def Binds(self) -> List[str]:
        return self.HostConfig["Binds"]


class podman_container:
    '''Manage podman container
    '''
    BASEURL: str = "unix:///run/podman/podman.sock"

    def __init__(self, container_name: str):
        assert isinstance(container_name, str)
        self.__client: Optional[PodmanClient] = None
        self.__container: Optional[Container] = None
        self.__container_name: str = container_name

    @property
    def client(self) -> PodmanClient:
        if self.__client is None:
            self.__client = PodmanClient(base_url=self.BASEURL)
        return self.__client

    @property
    def container(self) -> Container:
        if self.__container is None:
            self.__container = self.client.containers.get(self.container_name)
        return self.__container

    @property
    def container_name(self) -> str:
        return self.__container_name

    def inspect(self) -> podman_container_inspect:
        return podman_container_inspect(self.container)

    @property
    def service_unit(self) -> str:
        return f"container-{self.container_name}.service"

    def stop_service(self) -> int:
        return os.system(f"systemctl stop {self.service_unit}")

    def generate_service(self, restart_policy: str = "on-failure",
                         restart_sect: Optional[int] = None,
                         start_timeout: Optional[int] = None,
                         stop_timeout: int = 10,
                         wants: Optional[Iterable[str]] = None,
                         after: Optional[Iterable[str]] = None,
                         requires: Optional[Iterable[str]] = None
                         ) -> systemd_service:
        """generate systemd unit for a container

        same as 'podman generate systemd <container>'
        """
        if not isinstance(CMD, str):
            raise FileNotFoundError("podman command not found")

        container_inspect: podman_container_inspect = self.inspect()
        mounts: List[Optional[str]] = [mountpoint(bind.split(":")[0]) for bind in  # noqa
                                       container_inspect.Binds if bind.startswith("/")]  # noqa
        mountpoints: List[str] = ["/run/containers/storage"]
        mountpoints.extend([m for m in mounts if isinstance(m, str)])
        content: str = f"""
[Unit]
Description=Podman {self.service_unit}
Wants=network-online.target
After=network-online.target
{f"RequiresMountsFor={' '.join(mountpoints)}"}
{f"Requires={' '.join(requires)}" if requires is not None else ""}
{f"Wants={' '.join(wants)}" if wants is not None else ""}
{f"After={' '.join(after)}" if after is not None else ""}

[Service]
Environment=PODMAN_SYSTEMD_UNIT=%n
Restart={restart_policy}
{f"RestartSec={restart_sect}" if restart_sect is not None else ""}
{f"TimeoutStartSec={start_timeout}" if start_timeout is not None else ""}
TimeoutStopSec=70
ExecStart={CMD} start {self.container_name}
ExecStop={CMD} stop -t {stop_timeout} {self.container_name}
ExecStopPost={CMD} stop -t {stop_timeout} {self.container_name}
PIDFile={container_inspect.PidFile}
Type=forking

[Install]
WantedBy=default.target
"""
        return systemd_service.from_string(content)

    def enable_service(self, restart_policy: str = "on-failure") -> int:
        service = self.generate_service(restart_policy=restart_policy)
        service.create_unit(unit=self.service_unit)

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
        systemd_service.delete_unit(unit=self.service_unit)
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
