# coding:utf-8

import os
import sys
from typing import Dict
from typing import Optional

from podman import PodmanClient
from podman.domain.containers import Container

UID: int = os.getuid()


class ContainerManager:
    URI: str = f"unix:///run/user/{UID}/podman/podman.sock"

    def __init__(self, container_name: str):
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

    @property
    def pid_file(self) -> str:
        return self.container.inspect()["PidFile"]

    def inspect(self) -> Dict[str, str]:
        return self.container.inspect()


if __name__ == "__main__":
    container = ContainerManager(container_name=sys.argv[1])
    print(container.inspect())
