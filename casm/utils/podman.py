# coding:utf-8

import os

SERVICE_NAME = "container-{name}.service"
SYSTEMD_PATH = "/etc/systemd/system/{service_name}"


def stop_service(name: str) -> int:
    assert isinstance(name, str)
    service_name = SERVICE_NAME.format(name=name)
    return os.system(f"systemctl stop {service_name}")


def enable_service(name: str) -> int:
    assert isinstance(name, str)
    service_name = SERVICE_NAME.format(name=name)
    path = SYSTEMD_PATH.format(service_name=service_name)
    errno = os.system(f"podman generate systemd --name {name} > {path}")
    if errno != 0:
        if os.path.isfile(path):
            os.remove(path)
        return errno
    errno = os.system(f"systemctl enable --now {service_name}")
    if errno != 0:
        return errno
    return 0


def disable_service(name: str) -> int:
    assert isinstance(name, str)
    service_name = SERVICE_NAME.format(name=name)
    errno = os.system(f"systemctl disable {service_name}")
    if errno != 0:
        return errno
    path = SYSTEMD_PATH.format(service_name=service_name)
    if os.path.isfile(path):
        os.remove(path)
    return 0
