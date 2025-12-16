#!/usr/bin/python3
# coding:utf-8

from errno import ENOENT
from errno import ENOTRECOVERABLE
import os
import shutil
import sys
from threading import Thread
from time import time
from typing import List
from unittest import TestCase
from unittest import main
from unittest import mock

from casm.cmds.casm import main as casm
from casm.cmds.cman import main as cman
from casm.cmds.modify import template
from casm.cmds.podman import container
from casm.cmds.podman import guard
from casm.unittest.helper import FakeInspect
from casm.utils.podman import podman_container


class Test_casm(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.instance = os.path.join("example", "instance.yml")
        cls.template = os.path.join("example", "template.yml")
        cls.file = os.path.abspath(cls.template)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.argv = sys.argv

    def tearDown(self):
        sys.argv = self.argv

    def test_sys_argv_instance(self):
        sys.argv = ["casm", "--instance", self.instance]
        self.assertEqual(casm(), 0)

    def test_sys_argv_instance_ArgumentError(self):
        sys.argv = ["casm", "--instance"]
        self.assertRaises(SystemExit, casm)

    def test_sys_argv_template(self):
        sys.argv = ["casm", "--template", self.template]
        self.assertEqual(casm(), 0)

    def test_sys_argv_template_ArgumentError(self):
        sys.argv = ["casm", "--template"]
        self.assertRaises(SystemExit, casm)

    def test_instance_is_dir(self):
        cmds: List[str] = ["--instance", "example"]
        self.assertEqual(casm(cmds), ENOENT)

    def test_variables(self):
        instance = os.path.join("example", "variables", "variables.yml")
        cmds: List[str] = ["--instance", instance]
        self.assertEqual(casm(cmds), 0)

    def test_variables_null(self):
        instance = os.path.join("example", "variables", "variables_null.yml")
        cmds: List[str] = ["--instance", instance]
        self.assertEqual(casm(cmds), 0)

    def test_template(self):
        cmds: List[str] = []
        cmds.extend(["--template", self.template])
        cmds.extend(["--project-name", "unittest"])
        cmds.extend(["--env", "key=value"])
        self.assertEqual(casm(cmds), 0)

    @mock.patch.object(os, "system")
    def test_pull(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template, "pull"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} pull"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_up(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template, "up"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} up --detach"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_down(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template, "down"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} down"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_start(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template, "start"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} start"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_stop(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template, "stop"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} stop"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_restart(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template, "restart"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} restart"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_pause(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template, "pause"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} pause"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_unpause(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template, "unpause"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} unpause"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_exec(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "exec", "worker", "bash"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} exec worker bash"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_exec_opt(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "exec", "--detach", "--privileged", "--user=test",
                           "-T", "--index=1", "worker"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} exec "\
            "--detach --privileged --user test -T --index 1 worker"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_logs(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template, "logs"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} logs"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_logs_opt(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "logs", "--follow", "--tail=10"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} logs --follow --tail 10"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    @mock.patch.object(podman_container, "generate_service", mock.MagicMock())
    def test_systemd_enable(self, mock_system: mock.Mock):
        template = os.path.join("example", "systemd", "template.yml")
        mock_system.side_effect = [0, 0]
        cmds: List[str] = ["--template", template,
                           "--project-name", "unittest",
                           "systemd", "enable", "worker"]
        self.assertEqual(casm(cmds), 0)
        name = "unittest-worker"
        calls = [
            mock.call(f"systemctl enable --now container-{name}.service"),
        ]
        mock_system.assert_has_calls(calls)

    @mock.patch.object(os, "system")
    @mock.patch.object(podman_container, "generate_service", mock.MagicMock())
    def test_systemd_disable(self, mock_system: mock.Mock):
        template = os.path.join("example", "systemd", "template.yml")
        mock_system.side_effect = [0, 0, 0]
        cmds: List[str] = ["--template", template,
                           "--project-name", "unittest",
                           "systemd", "disable", "worker"]
        self.assertEqual(casm(cmds), 0)
        service = "container-unittest-worker.service"
        calls = [
            mock.call(f"systemctl stop {service}"),
            mock.call(f"systemctl disable {service}"),
            mock.call("systemctl daemon-reload"),
        ]
        mock_system.assert_has_calls(calls)

    def test_modify_assemble(self):
        self.assertEqual(casm(["--template", self.template, "modify", "assemble"]), 0)  # noqa:E501

    @mock.patch.object(template.assemble_file, "dump_template", mock.MagicMock())  # noqa:E501
    def test_modify_template_services(self):
        template = os.path.join("example", "modify", "services.yml")
        output = template + ".out"
        cmds: List[str] = ["--template", template, "modify", "template",
                           "--output", output, "services",
                           "--mount-localtime", "--privileged", "--systemd",
                           "worker"]
        self.assertEqual(casm(cmds), 0)

    def test_services(self):
        cmds: List[str] = ["--template", self.template, "services"]
        self.assertEqual(casm(cmds), 0)
        self.assertEqual(casm(cmds + ["--service-name"]), 0)
        self.assertEqual(casm(cmds + ["--container-name"]), 0)


class Test_cman(TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch.object(container.podman_container, "list")
    def test_container(self, mock_list):
        mock_list.return_value = ["unit", "test"]
        cmds: List[str] = ["container"]
        self.assertEqual(cman(cmds), 0)

    @mock.patch.object(container.podman_container, "list")
    @mock.patch.object(container.podman_container, "inspect")
    def test_container_inspect(self, mock_inspect, mock_list):
        mock_inspect.return_value = FakeInspect().create()
        mock_list.return_value = ["unit", "test"]
        cmds: List[str] = ["container", "inspect"]
        self.assertEqual(cman(cmds), 0)

    @mock.patch.object(container.podman_container, "list")
    @mock.patch.object(container.podman_container, "guard")
    def test_container_guard(self, mock_guard, mock_list):
        mock_guard.side_effect = [0, 0]
        mock_list.return_value = ["unit", "test"]
        cmds: List[str] = ["container", "guard", "unit", "test"]
        self.assertEqual(cman(cmds), 0)

    @mock.patch.object(container.podman_container, "list")
    @mock.patch.object(container.podman_container, "guard")
    def test_container_guard_exit(self, mock_guard, mock_list):
        mock_guard.side_effect = [0, 123456]
        mock_list.return_value = ["unit", "test"]
        cmds: List[str] = ["container", "guard", "unit", "test"]
        self.assertEqual(cman(cmds), 123456)

    @mock.patch.object(container.podman_container, "list")
    @mock.patch.object(container.podman_container, "daemon")
    def test_container_guard_daemon(self, mock_daemon, mock_list):
        fake_daemon = Thread(target=lambda: time())
        fake_daemon.start()
        mock_daemon.side_effect = [fake_daemon]
        mock_list.return_value = ["unit", "test"]
        cmds: List[str] = ["container", "guard", "--daemon", "test"]
        self.assertEqual(cman(cmds), ENOTRECOVERABLE)

    @mock.patch.object(container.podman_container, "list")
    @mock.patch.object(guard.podman_containers_guard_service, "enable")
    def test_guard_enable(self, mock_enable, mock_list):
        mock_list.return_value = ["unit", "test"]
        mock_enable.side_effect = [123456]
        cmds: List[str] = ["guard", "enable"]
        self.assertEqual(cman(cmds), 123456)

    @mock.patch.object(container.podman_container, "list")
    @mock.patch.object(guard.podman_containers_guard_service, "disable")
    def test_guard_disable(self, mock_disable, mock_list):
        mock_list.return_value = ["unit", "test"]
        mock_disable.side_effect = [123456]
        cmds: List[str] = ["guard", "disable"]
        self.assertEqual(cman(cmds), 123456)

    @mock.patch.object(container.podman_container, "list")
    def test_guard(self, mock_list):
        mock_list.return_value = ["unit", "test"]
        cmds: List[str] = ["guard"]
        self.assertEqual(cman(cmds), 0)

    @mock.patch.object(os, "system")
    @mock.patch.object(container.podman_container, "list")
    def test_system_prune(self, mock_list, mock_system: mock.Mock):
        mock_list.return_value = ["unit", "test"]
        mock_system.side_effect = [0]
        cmds: List[str] = ["system", "prune"]
        self.assertEqual(cman(cmds), 0)
        cmd = f"{shutil.which('podman')} system prune"
        mock_system.assert_called_once_with(cmd)


if __name__ == "__main__":
    main()
