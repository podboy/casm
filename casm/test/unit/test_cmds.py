#!/usr/bin/python3
# coding:utf-8

from errno import ENOENT
import os
import sys
from typing import List
import unittest

import mock

from casm.cmds import main as casm
from casm.cmds.podman import main as cman


class Test_casm(unittest.TestCase):

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
    def test_systemd_enable(self, mock_system: mock.Mock):
        template = os.path.join("example", "systemd", "template.yml")
        mock_system.side_effect = [0, 0]
        cmds: List[str] = ["--template", template,
                           "--project-name", "unittest",
                           "systemd", "enable", "worker"]
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
        mock_system.side_effect = [0, 0]
        cmds: List[str] = ["--template", template,
                           "--project-name", "unittest",
                           "systemd", "disable", "worker"]
        self.assertEqual(casm(cmds), 0)
        service = "container-unittest-worker.service"
        calls = [
            mock.call(f"systemctl stop {service}"),
            mock.call(f"systemctl disable {service}"),
        ]
        mock_system.assert_has_calls(calls)

    def test_modify_template_services(self):
        template = os.path.join("example", "modify", "services.yml")
        output = template + ".out"
        cmds: List[str] = ["--template", template, "modify", "template",
                           "--output", output, "services",
                           "--mount-localtime", "--privileged", "--systemd"]
        self.assertEqual(casm(cmds), 0)

    def test_services(self):
        cmds: List[str] = ["--template", self.template, "services"]
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
