# coding:utf-8

import getpass
import os
import shutil
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from podman import PodmanClient
from podman.domain.containers import Container
from xmanage import systemd_service

from .common import mountpoint

# UID: int = os.getuid()
CMD: Optional[str] = shutil.which("podman")


class podman_container_inspect:

    class state_struct:

        class health_struct:
            def __init__(self, value: Dict[str, Any]):
                assert isinstance(value, dict)
                self.__value: Dict[str, Any] = value

            @property
            def Status(self) -> str:
                return self.__value["Status"]

            @property
            def FailingStreak(self) -> int:
                return self.__value["FailingStreak"]

        def __init__(self, value: Dict[str, Any]):
            assert isinstance(value, dict)
            self.__value: Dict[str, Any] = value
            health: Optional[Dict[str, Any]] = value.get("Health")
            self.__health = self.health_struct(health) if health else None

        @property
        def Status(self) -> str:
            return self.__value["Status"]

        @property
        def Running(self) -> bool:
            return self.__value["Running"]

        @property
        def Paused(self) -> bool:
            return self.__value["Paused"]

        @property
        def Restarting(self) -> bool:
            return self.__value["Restarting"]

        @property
        def OOMKilled(self) -> bool:
            return self.__value["OOMKilled"]

        @property
        def Dead(self) -> bool:
            return self.__value["Dead"]

        @property
        def Pid(self) -> int:
            return self.__value["Pid"]

        @property
        def ConmonPid(self) -> int:
            return self.__value["ConmonPid"]

        @property
        def ExitCode(self) -> int:
            return self.__value["ExitCode"]

        @property
        def Health(self) -> Optional[health_struct]:
            return self.__health

    class host_config_struct:
        def __init__(self, value: Dict[str, Any]):
            assert isinstance(value, dict)
            self.__value: Dict[str, Any] = value

        @property
        def Binds(self) -> List[str]:
            return self.__value["Binds"]

    def __init__(self, container: Container):
        assert isinstance(container, Container)
        self.__container: Container = container
        self.__info: Dict[str, Any] = container.inspect()
        self.__state: Optional[podman_container_inspect.state_struct] = None
        self.__host_config: Optional[podman_container_inspect.host_config_struct] = None  # noqa:E501

    @property
    def container(self) -> Container:
        return self.__container

    @property
    def info(self) -> Dict[str, Any]:
        return self.__info

    @property
    def Id(self) -> str:
        return self.info["Id"]

    @property
    def Name(self) -> str:
        return self.info["Name"]

    @property
    def RestartCount(self) -> int:
        return self.info["RestartCount"]

    @property
    def PidFile(self) -> str:
        return self.info["PidFile"]

    @property
    def State(self) -> state_struct:
        if self.__state is None:
            self.__state = self.state_struct(self.info["State"])
        return self.__state

    @property
    def HostConfig(self) -> host_config_struct:
        if self.__host_config is None:
            self.__host_config = self.host_config_struct(self.info["HostConfig"])  # noqa:E501
        return self.__host_config


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

    @property
    def guard_crontab_file(self) -> str:
        return f"/etc/cron.d/guard-container-{self.container_name}.sh"

    @property
    def healthy(self) -> bool:
        inspect = self.inspect()

        def __restarting() -> bool:
            return inspect.State.Restarting

        def __running() -> bool:
            return inspect.State.Status == "running" and\
                inspect.State.Running and\
                not inspect.State.Paused and\
                not inspect.State.OOMKilled and\
                not inspect.State.Dead

        def __healthy() -> bool:
            health = inspect.State.Health
            return health is None or health.Status == "healthy"

        return __restarting() or __running() and __healthy()

    def stop(self) -> int:
        return os.system(f"podman container stop {self.container_name}")

    def start(self) -> int:
        return os.system(f"podman container start {self.container_name}")

    def restart(self) -> int:
        return os.system(f"podman container restart {self.container_name}")

    def stop_service(self) -> int:
        return os.system(f"systemctl stop {self.service_unit}")

    def start_service(self) -> int:
        return os.system(f"systemctl start {self.service_unit}")

    def restart_service(self) -> int:
        return os.system(f"systemctl restart {self.service_unit}")

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
        mounts: List[Optional[str]] = [mountpoint(bind.split(":")[0]) for bind in  # noqa:E501
                                       container_inspect.HostConfig.Binds if bind.startswith("/")]  # noqa:E501
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

    def generate_guard_task(self, interval: int = 3) -> int:
        with open(self.guard_crontab_file, "w") as hdl:
            username: str = getpass.getuser()
            hdl.write(f"PATH={os.environ['PATH']}\n")
            hdl.write(f"*/{interval} * * * * {username} cman container guard {self.container_name}\n")  # noqa:E501
        return 0

    def destroy_guard_task(self) -> int:
        crontab_file: str = self.guard_crontab_file
        if os.path.isfile(crontab_file):
            os.remove(crontab_file)
        return 0

    def guard(self) -> bool:
        def __restart() -> bool:
            return self.restart_service() == 0 or self.restart() == 0
        return __restart() if not self.healthy else True

    @classmethod
    def list(cls, all: bool = False) -> Tuple[str, ...]:
        client: PodmanClient = PodmanClient(base_url=cls.BASEURL)
        containers: List[Container] = client.containers.list(all=all)
        container_names = [container.name for container in containers]
        return tuple(name for name in container_names if isinstance(name, str))


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
