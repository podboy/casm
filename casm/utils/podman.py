# coding:utf-8

from errno import EEXIST
import os
from random import randint
import shutil
from threading import Thread
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from podman import PodmanClient
from podman.domain.containers import Container
from xkits_logger.logger import Logger
from xkits_thread.task import DaemonTaskJob
from xkits_thread.task import DelayTaskJob
from xmanage import systemd_service

from casm.utils.common import mountpoint

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
    """Manage podman container"""
    BASEURL: str = "unix:///run/podman/podman.sock"

    def __init__(self, container_name: str):
        assert isinstance(container_name, str)
        self.__container_name: str = container_name

    @property
    def container_name(self) -> str:
        return self.__container_name

    def inspect(self) -> podman_container_inspect:
        with PodmanClient(base_url=self.BASEURL) as client:
            container: Container = client.containers.get(self.container_name)
            return podman_container_inspect(container)

    @property
    def service_unit(self) -> str:
        return f"container-{self.container_name}.service"

    @property
    def healthy(self) -> bool:
        def _restarting(inspect: podman_container_inspect) -> bool:
            return inspect.State.Restarting

        def _running(inspect: podman_container_inspect) -> bool:
            return inspect.State.Status == "running" and\
                inspect.State.Running and\
                not inspect.State.Paused and\
                not inspect.State.OOMKilled and\
                not inspect.State.Dead

        def _healthy(inspect: podman_container_inspect) -> bool:
            health = inspect.State.Health
            return health is None or health.Status == "healthy"

        inspect: podman_container_inspect = self.inspect()
        return _restarting(inspect) or _running(inspect) and _healthy(inspect)

    def stop(self) -> int:
        return os.system(f"podman container stop {self.container_name}")

    def start(self) -> int:
        return os.system(f"podman container start {self.container_name}")

    def pause(self) -> int:
        return os.system(f"podman container pause {self.container_name}")

    def unpause(self) -> int:
        return os.system(f"podman container unpause {self.container_name}")

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
        service_unit: str = service.create_unit(unit=self.service_unit)
        Logger.stdout_green(f"create container service unit: {service_unit}")
        return os.system(f"systemctl enable --now {self.service_unit}")

    def disable_service(self) -> int:
        errno = os.system(f"systemctl stop {self.service_unit}")
        if errno != 0:
            return errno
        errno = os.system(f"systemctl disable {self.service_unit}")
        if errno != 0:
            return errno
        return 0 if systemd_service.delete_unit(unit=self.service_unit) else EEXIST  # noqa:E501

    def guard(self) -> int:
        def __restart() -> int:
            Logger.stderr_red(f"container {self.container_name} restarting")
            return self.restart() if self.restart_service() != 0 else 0
        return __restart() if not self.healthy else 0

    def daemon(self, block: bool = True, min_delay: int = 180, max_delay: int = 3600) -> Optional[Thread]:  # noqa:E501
        max_delay = max(min_delay + 120, max_delay)

        def __daemon(task: DelayTaskJob, min_delay: int, max_delay: int) -> bool:  # noqa:E501
            success: bool = task.run() is True and task.result == 0
            Logger.stderr(f"container {self.container_name} guard task {'success' if success else 'failure'}")  # noqa:E501
            delay: float = task.delay_time * 1.1 if success else task.delay_time * 0.1  # noqa:E501
            task.renew(delay=min(max(min_delay, delay), max_delay))
            Logger.stderr(f"container {self.container_name} guard task will run again in {task.delay_time:.1f} seconds")  # noqa:E501
            return success

        delay_job: DelayTaskJob = DelayTaskJob.create_delay_task(randint(min_delay, min_delay + 120), self.guard)  # noqa:E501
        daemon_job: DaemonTaskJob = DaemonTaskJob.create_daemon_task(__daemon, delay_job, min_delay, max_delay)  # noqa:E501
        Logger.stderr(f"container {self.container_name} guard task will start in {delay_job.delay_time:.1f} seconds")  # noqa:E501
        return daemon_job.run() if block else daemon_job.run_in_background()

    @classmethod
    def list(cls, all: bool = False) -> Tuple[str, ...]:
        with PodmanClient(base_url=cls.BASEURL) as client:
            containers: List[Container] = client.containers.list(all=all)
            container_names = [container.name for container in containers]
            return tuple(name for name in container_names if isinstance(name, str))  # noqa:E501


class podman_containers_guard_service:
    """Manage podman containers guard service"""
    SERVICE_UNIT: str = "containers-guard.service"

    @classmethod
    def generate(cls, restart_policy: str = "always") -> systemd_service:
        """generate systemd unit for containers guard"""
        cmd_python = shutil.which("python")
        cmd_cman = shutil.which("cman")
        if not isinstance(cmd_python, str) or not isinstance(cmd_cman, str):
            raise FileNotFoundError("python or cman command not found")

        content: str = f"""
[Unit]
Description=Podman containers guard service
Wants=network-online.target
After=network-online.target

[Service]
ExecStart={cmd_python} {cmd_cman} container guard --daemon --debug --stdout
Restart={restart_policy}
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
"""
        return systemd_service.from_string(content)

    @classmethod
    def enable(cls, restart_policy: str = "always") -> int:
        service = cls.generate(restart_policy=restart_policy)
        unit: str = service.create_unit(unit=cls.SERVICE_UNIT, allow_update=True)  # noqa:E501
        Logger.stdout_green(f"create containers guard service unit: {unit}")
        return os.system(f"systemctl enable --now {cls.SERVICE_UNIT}")

    @classmethod
    def disable(cls) -> int:
        errno = os.system(f"systemctl stop {cls.SERVICE_UNIT}")
        if errno != 0:
            return errno
        errno = os.system(f"systemctl disable {cls.SERVICE_UNIT}")
        if errno != 0:
            return errno
        return 0 if systemd_service.delete_unit(unit=cls.SERVICE_UNIT) else EEXIST  # noqa:E501


class podman_cmd:
    """Execute podman command"""

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
