# coding:utf-8

import os

BASE = "podman-compose --file {compose_file}"


def pull(compose_file: str, *services: str) -> int:
    assert isinstance(compose_file, str)
    base = BASE.format(compose_file=compose_file)
    return os.system(f"{base} pull {' '.join(services)}")
