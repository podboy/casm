# coding:utf-8

import os

BASE = "podman-compose --file {compose_file}"


def pull(compose_file: str, *services: str) -> int:
    assert isinstance(compose_file, str)
    base = BASE.format(compose_file=compose_file)
    return os.system(f"{base} pull {' '.join(services)}")


def up(compose_file: str, *services: str) -> int:
    assert isinstance(compose_file, str)
    base = BASE.format(compose_file=compose_file)
    return os.system(f"{base} up --detach {' '.join(services)}")


def down(compose_file: str, *services: str) -> int:
    assert isinstance(compose_file, str)
    base = BASE.format(compose_file=compose_file)
    return os.system(f"{base} down {' '.join(services)}")


def start(compose_file: str, *services: str) -> int:
    assert isinstance(compose_file, str)
    base = BASE.format(compose_file=compose_file)
    return os.system(f"{base} start {' '.join(services)}")


def stop(compose_file: str, *services: str) -> int:
    assert isinstance(compose_file, str)
    base = BASE.format(compose_file=compose_file)
    return os.system(f"{base} stop {' '.join(services)}")


def restart(compose_file: str, *services: str) -> int:
    assert isinstance(compose_file, str)
    base = BASE.format(compose_file=compose_file)
    return os.system(f"{base} restart {' '.join(services)}")


def pause(compose_file: str, *services: str) -> int:
    assert isinstance(compose_file, str)
    base = BASE.format(compose_file=compose_file)
    return os.system(f"{base} pause {' '.join(services)}")


def unpause(compose_file: str, *services: str) -> int:
    assert isinstance(compose_file, str)
    base = BASE.format(compose_file=compose_file)
    return os.system(f"{base} unpause {' '.join(services)}")
