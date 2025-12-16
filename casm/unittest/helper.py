#!/usr/bin/python3

from typing import Optional
from unittest import mock

from podman.domain.containers import Container

from casm.utils.podman import podman_container_inspect


class FakeInspect:
    def __init__(self):
        self.inspect = {
            "Id": "123456",
            "Name": "demo",
            "RestartCount": 1,
            "PidFile": "/tmp/demo.pid",
            "State": {
                "Status": "created",
                "Running": False,
                "Paused": False,
                "Restarting": False,
                "OOMKilled": False,
                "Dead": False,
                "Pid": 1,
                "ConmonPid": 2,
                "ExitCode": 3,
                "Health": {
                    "Status": "healthy",
                    "FailingStreak": 0,
                },
            },
            "HostConfig": {
                "Binds": [],
            },
        }

    def create(self, container: Optional[Container] = None) -> podman_container_inspect:  # noqa:E501
        _container: Container = container or Container()
        with mock.patch.object(_container, "inspect") as mock_inspect:
            mock_inspect.side_effect = [self.inspect]
            return podman_container_inspect(_container)
