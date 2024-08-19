# coding:utf-8

import sys

from casm import podman_container


if __name__ == "__main__":
    container_name: str = sys.argv[1]
    container = podman_container(container_name)
    container.generate_service().create_unit("/tmp", container_name)
