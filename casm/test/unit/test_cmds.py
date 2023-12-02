#!/usr/bin/python3
# coding:utf-8

from errno import ENOENT
import os
from typing import List
import unittest

import mock

from casm.cmds import main as casm
from casm.cmds.podman import main as cman


class Test_casm(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.template = os.path.join("example", "template.yml")
        cls.compose = os.path.join("example", "docker-compose.yml")
        cls.file = os.path.abspath(cls.compose)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instance_is_dir(self):
        cmds: List[str] = ["--instance", "example"]
        self.assertEqual(casm(cmds), ENOENT)

    def test_variables_null(self):
        instance = os.path.join("example", "variables", "variables_null.yml")
        cmds: List[str] = ["--instance", instance]
        self.assertEqual(casm(cmds), 0)

    def test_template(self):
        cmds: List[str] = []
        cmds.extend(["--template", self.template, "--compose", self.compose])
        cmds.extend(["--project-name", "unittest"])
        cmds.append("--mount-timezone")
        cmds.append("--mount-localtime")
        cmds.append("--systemd")
        self.assertEqual(casm(cmds), 0)

    @mock.patch.object(os, "system")
    def test_pull(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "pull"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} pull"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_up(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "up"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} up --detach"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_down(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "down"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} down"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_start(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "start"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} start"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_stop(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "stop"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} stop"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_restart(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "restart"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} restart"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_pause(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "pause"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} pause"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_unpause(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "unpause"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} unpause"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_exec(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "exec", "worker", "bash"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} exec worker bash"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_exec_opt(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "exec", "--detach", "--privileged", "--user=test",
                           "-T", "--index=1", "worker"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} exec "\
            "--detach --privileged --user test -T --index 1 worker"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_logs(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "logs"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} logs"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_logs_opt(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "logs", "--follow", "--tail=10"]
        self.assertEqual(casm(cmds), 0)
        cmd = f"podman-compose --file {self.file} logs --follow --tail 10"
        mock_system.assert_called_once_with(cmd)

    @mock.patch.object(os, "system")
    def test_systemd_enable(self, mock_system: mock.Mock):
        template = os.path.join("example", "systemd", "template.yml")
        compose = os.path.join("example", "systemd", "docker-compose.yml")
        mock_system.side_effect = [0, 0]
        cmds: List[str] = ["--template", template, "--compose", compose,
                           "--project-name", "unittest",
                           "systemd", "enable", "worker", "service"]
        self.assertEqual(casm(cmds), 0)
        name = "unittest-worker"
        calls = [
            mock.call(f"podman generate systemd --name {name} > "
                      f"/etc/systemd/system/container-{name}.service"),
            mock.call(f"systemctl enable --now container-{name}.service"),
        ]
        mock_system.assert_has_calls(calls)

    @mock.patch.object(os, "system")
    def test_systemd_disable(self, mock_system: mock.Mock):
        template = os.path.join("example", "systemd", "template.yml")
        compose = os.path.join("example", "systemd", "docker-compose.yml")
        mock_system.side_effect = [0, 0]
        cmds: List[str] = ["--template", template, "--compose", compose,
                           "--project-name", "unittest",
                           "systemd", "disable", "worker", "service"]
        self.assertEqual(casm(cmds), 0)
        service = "container-unittest-worker.service"
        calls = [
            mock.call(f"systemctl stop {service}"),
            mock.call(f"systemctl disable {service}"),
        ]
        mock_system.assert_has_calls(calls)

    def test_services(self):
        cmds: List[str] = ["--template", self.template,
                           "--compose", self.compose,
                           "services"]
        self.assertEqual(casm(cmds), 0)
        self.assertEqual(casm(cmds + ["--service-name"]), 0)
        self.assertEqual(casm(cmds + ["--container-name"]), 0)


class Test_cman(unittest.TestCase):

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

    @mock.patch.object(os, "system")
    def test_system_prune(self, mock_system: mock.Mock):
        mock_system.side_effect = [0]
        cmds: List[str] = ["system", "prune"]
        self.assertEqual(cman(cmds), 0)
        cmd = "podman system prune"
        mock_system.assert_called_once_with(cmd)
