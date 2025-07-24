#!/usr/bin/python3
# coding:utf-8

import unittest
from unittest import mock

from casm.utils import podman


class Test_podman_container_inspect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.health = {
            "Status": "healthy",
            "FailingStreak": 0,
        }
        cls.state = {
            "Status": "created",
            "Running": False,
            "Paused": False,
            "Restarting": False,
            "OOMKilled": False,
            "Dead": False,
            "Pid": 1,
            "ConmonPid": 2,
            "ExitCode": 3,
            "Health": cls.health,
        }
        cls.host_config = {
            "Binds": [],
        }
        cls.inspect = {
            "Id": "123456",
            "Name": "demo",
            "RestartCount": 1,
            "PidFile": "/tmp/demo.pid",
            "State": cls.state,
            "HostConfig": cls.host_config,
        }

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.container = podman.Container()
        with mock.patch.object(self.container, "inspect") as mock_inspect:
            mock_inspect.side_effect = [self.inspect]
            self.container_inspect = podman.podman_container_inspect(self.container)  # noqa:E501

    def tearDown(self):
        pass

    def test_state_struct(self):
        self.assertIs(self.container_inspect.container, self.container)
        self.assertEqual(self.container_inspect.Id, "123456")
        self.assertEqual(self.container_inspect.Name, "demo")
        self.assertEqual(self.container_inspect.RestartCount, 1)
        self.assertEqual(self.container_inspect.PidFile, "/tmp/demo.pid")
        self.assertEqual(self.container_inspect.State.Status, "created")
        self.assertFalse(self.container_inspect.State.Running)
        self.assertFalse(self.container_inspect.State.Paused)
        self.assertFalse(self.container_inspect.State.Restarting)
        self.assertFalse(self.container_inspect.State.OOMKilled)
        self.assertFalse(self.container_inspect.State.Dead)
        self.assertEqual(self.container_inspect.State.Pid, 1)
        self.assertEqual(self.container_inspect.State.ConmonPid, 2)
        self.assertEqual(self.container_inspect.State.ExitCode, 3)
        self.assertIsInstance(self.container_inspect.State.Health, podman.podman_container_inspect.state_struct.health_struct)  # noqa:E501
        assert isinstance(self.container_inspect.State.Health, podman.podman_container_inspect.state_struct.health_struct)  # noqa:E501
        self.assertEqual(self.container_inspect.State.Health.Status, "healthy")
        self.assertEqual(self.container_inspect.State.Health.FailingStreak, 0)
        self.assertEqual(self.container_inspect.HostConfig.Binds, [])


class Test_podman_container(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.container = podman.podman_container("demo")

    def tearDown(self):
        pass

    @mock.patch.object(podman.os, "system")
    def test_stop(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(self.container.stop(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_start(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(self.container.start(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_pause(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(self.container.pause(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_unpause(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(self.container.unpause(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_restart(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(self.container.restart(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_stop_service(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(self.container.stop_service(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_start_service(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(self.container.start_service(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_restart_service(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(self.container.restart_service(), 123456)

    @mock.patch.object(podman, "PodmanClient", mock.MagicMock())
    @mock.patch.object(podman, "podman_container_inspect", mock.MagicMock())
    def test_generate_service(self):
        self.assertIsInstance(self.container.generate_service(), podman.systemd_service)  # noqa:E501

    @mock.patch.object(podman.os, "system")
    def test_enable_service(self, mock_system):
        mock_system.side_effect = [123456]
        with mock.patch.object(self.container, "generate_service", mock.MagicMock()):  # noqa:E501
            self.assertEqual(self.container.enable_service(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_disable_service_systemctl_stop_error(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(self.container.disable_service(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_disable_service_systemctl_disable_error(self, mock_system):
        mock_system.side_effect = [0, 123456]
        self.assertEqual(self.container.disable_service(), 123456)

    @mock.patch.object(podman.os, "system")
    def test_guard(self, mock_system):
        mock_system.side_effect = [123, 456]
        with mock.patch.object(self.container, "inspect") as mock_inspect:
            fake_inspect = mock.MagicMock()
            fake_inspect.State.Restarting = False
            fake_inspect.State.Status = "running"
            fake_inspect.State.Running = True
            fake_inspect.State.Paused = False
            fake_inspect.State.OOMKilled = False
            fake_inspect.State.Dead = False
            fake_inspect.State.Health.Status = "unhealthy"
            mock_inspect.side_effect = [fake_inspect, fake_inspect]
            self.assertFalse(self.container.healthy)
            self.assertEqual(self.container.guard(), 456)

    @mock.patch.object(podman.DaemonTaskJob, "create_daemon_task")
    def test_daemon(self, mock_create_daemon_task):
        fake_create_daemon_task = mock.MagicMock()
        mock_create_daemon_task.side_effect = [fake_create_daemon_task]
        fake_create_daemon_task.run.side_effect = [123456]
        self.assertEqual(self.container.daemon(), 123456)
        call_args = mock_create_daemon_task.call_args[0]
        fake_task = mock.MagicMock()
        fake_task.delay_time = 1.0
        call_args[0](fake_task, 1, 2)

    @mock.patch.object(podman, "PodmanClient")
    def test_list(self, mock_client):
        fake_client = mock.MagicMock()
        fake_client.containers.list.side_effect = [[]]
        mock_client.side_effect = [fake_client]
        self.assertEqual(podman.podman_container.list(), ())


class Test_podman_containers_guard_service(unittest.TestCase):

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

    def test_generate(self):
        self.assertIsInstance(podman.podman_containers_guard_service.generate(), podman.systemd_service)  # noqa:E501

    @mock.patch.object(podman.os, "system")
    @mock.patch.object(podman.podman_containers_guard_service, "generate", mock.MagicMock())  # noqa:E501
    def test_enable(self, mock_system):
        mock_system.side_effect = [123]
        self.assertEqual(podman.podman_containers_guard_service.enable(), 123)

    @mock.patch.object(podman.os, "system")
    def test_disable_systemctl_stop_error(self, mock_system):
        mock_system.side_effect = [123]
        self.assertEqual(podman.podman_containers_guard_service.disable(), 123)

    @mock.patch.object(podman.os, "system")
    def test_disable_systemctl_disable_error(self, mock_system):
        mock_system.side_effect = [0, 123]
        self.assertEqual(podman.podman_containers_guard_service.disable(), 123)

    @mock.patch.object(podman.os, "remove", mock.MagicMock())
    @mock.patch.object(podman.os, "system")
    def test_disable(self, mock_system):
        mock_system.side_effect = [0, 0, 0]
        check = podman.podman_containers_guard_service.disable()
        self.assertTrue(check == 0 or check == podman.EEXIST)


class Test_podman_cmd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        podman.CMD = "/usr/bin/podman"

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch.object(podman.os, "system")
    def test_system_prune(self, mock_system):
        mock_system.side_effect = [123456]
        self.assertEqual(podman.podman_cmd.system_prune(), 123456)


if __name__ == "__main__":
    unittest.main()
