#!/usr/bin/python3
# coding:utf-8

import os
from typing import Dict
import unittest

from casm.utils.compose import compose_file
from casm.utils.compose import compose_network
from casm.utils.compose import compose_networks
from casm.utils.compose import compose_service
from casm.utils.compose import compose_services
from casm.utils.compose import compose_volume
from casm.utils.compose import compose_volumes
from casm.utils.compose import default_project_name
from casm.utils.compose import service_deploy
from casm.utils.compose import service_volume
from casm.utils.compose import service_volumes
from casm.utils.yaml import safe_load_data


class Test_compose_file(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.file = os.path.join("example", "template.yml")
        cls.path = os.path.abspath(cls.file)
        cls.base = os.path.basename(cls.path)
        cls.yaml = safe_load_data(cls.path)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.compose_file = compose_file(base_dir=self.base,
                                         project_name="unittest",
                                         compose_yaml=self.yaml)

    def tearDown(self):
        pass

    def test_default_project_name(self):
        self.assertEqual(default_project_name(os.path.dirname(__file__)), "unittest")  # noqa:E501

    def test_check_compose_file(self):
        self.assertIsInstance(self.compose_file.base_dir, str)
        self.assertEqual(self.compose_file.base_dir, self.base)
        self.assertIsInstance(self.compose_file.volumes, compose_volumes)
        self.assertIsInstance(self.compose_file.volumes.root, compose_file)
        self.assertIsInstance(self.compose_file.volumes.content, Dict)
        self.assertIsInstance(self.compose_file.networks, compose_networks)
        self.assertIsInstance(self.compose_file.networks.root, compose_file)
        self.assertIsInstance(self.compose_file.networks.content, Dict)
        self.assertIsInstance(self.compose_file.services, compose_services)
        self.assertIsInstance(self.compose_file.services.root, compose_file)
        self.assertIsInstance(self.compose_file.services.content, Dict)

    def test_check_compose_volume_iter(self):
        for volume in self.compose_file.volumes:
            self.assertIsInstance(volume, compose_volume)
            self.assertIsInstance(volume.root, compose_file)
            self.assertIsInstance(volume.volumes, compose_volumes)
            self.assertIsInstance(volume.title, str)
            self.assertIsInstance(volume.value, Dict)
            self.assertTrue(
                volume.name is None or isinstance(volume.name, str))
            self.assertTrue(
                volume.external is None or isinstance(volume.external, Dict))

    def test_check_compose_volume_set_get_del(self):
        self.compose_file.volumes["unittest"] = compose_volume(
            self.compose_file.volumes, "unittest")
        volume = self.compose_file.volumes["unittest"]
        self.assertIsInstance(volume, compose_volume)
        assert isinstance(volume, compose_volume)
        self.assertIsInstance(volume.root, compose_file)
        self.assertIsInstance(volume.volumes, compose_volumes)
        self.assertIsInstance(volume.title, str)
        self.assertIsInstance(volume.value, Dict)
        self.assertTrue(volume.name is None or isinstance(volume.name, str))
        self.assertTrue(volume.external is None or isinstance(
            volume.external, Dict))
        del self.compose_file.volumes["unittest"]

    def test_check_compose_network_iter(self):
        for network in self.compose_file.networks:
            self.assertIsInstance(network, compose_network)
            self.assertIsInstance(network.root, compose_file)
            self.assertIsInstance(network.networks, compose_networks)
            self.assertIsInstance(network.title, str)
            self.assertIsInstance(network.value, Dict)

    def test_check_compose_network_set_get_del(self):
        self.compose_file.networks["unittest"] = compose_network(
            self.compose_file.networks, "unittest")
        network = self.compose_file.networks["unittest"]
        self.assertIsInstance(network, compose_network)
        assert isinstance(network, compose_network)
        self.assertIsInstance(network.root, compose_file)
        self.assertIsInstance(network.networks, compose_networks)
        self.assertIsInstance(network.title, str)
        self.assertIsInstance(network.value, Dict)
        del self.compose_file.networks["unittest"]

    def test_check_compose_service_iter(self):
        for service in self.compose_file.services:
            self.assertIsInstance(service, compose_service)
            self.assertIsInstance(service.root, compose_file)
            self.assertIsInstance(service.services, compose_services)
            self.assertIsInstance(service.title, str)
            self.assertIsInstance(service.value, Dict)
            self.assertIsInstance(service.container_name, str)
            self.assertIsInstance(service.privileged, bool)
            self.assertIsInstance(service.restart, str)
            self.assertIsInstance(service.volumes, service_volumes)
            self.assertIsInstance(service.deploy, service_deploy)
            self.assertIsInstance(service.deploy.service, compose_service)
            self.assertIsNone(service.volumes.update())
            service.mount("/test", "/unit", False)
            service.mount("/test", "/demo", False)
            service.mount("/test", "/demo", True)
            for volume in service.volumes:
                self.assertIsInstance(volume, service_volume)
                self.assertTrue(isinstance(volume.volume_name, str) or volume.volume_name is None)  # noqa:E501
                self.assertIsInstance(volume.read_only, bool)
                self.assertIsInstance(volume.target, str)
                volume.value = "test:/demo:ro"
            service.volumes = service.volumes

    def test_check_compose_service_set_get_del(self):
        self.compose_file.services["unittest"] = compose_service(
            self.compose_file.services, "unittest")
        service = self.compose_file.services["unittest"]
        self.assertIsInstance(service, compose_service)
        assert isinstance(service, compose_service)
        self.assertIsInstance(service.root, compose_file)
        self.assertIsInstance(service.services, compose_services)
        self.assertIsInstance(service.title, str)
        self.assertIsInstance(service.value, Dict)
        self.assertIsInstance(service.container_name, str)
        self.assertIsInstance(service.privileged, bool)
        self.assertIsInstance(service.restart, str)
        self.assertIsInstance(service.volumes, service_volumes)
        self.assertIsInstance(service.deploy, service_deploy)
        self.assertIsInstance(service.deploy.service, compose_service)
        del self.compose_file.services["unittest"]


if __name__ == "__main__":
    unittest.main()
