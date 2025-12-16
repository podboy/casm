#!/usr/bin/python3
# coding:utf-8

from os.path import join
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest import main

from casm.utils import yaml


class Test_utils_yaml(TestCase):

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

    def test_safe_dump_data(self):
        self.assertEqual(yaml.safe_dump_data({"demo": "test"}), "demo: test\n")

    def test_safe_dump_file(self):
        with TemporaryDirectory() as tmpdir:
            self.assertIsNone(yaml.safe_dump_file(path := join(tmpdir, "test.yaml"), {"demo": "test"}))  # noqa:E501
            self.assertEqual(yaml.safe_load_file(path), {"demo": "test"})


if __name__ == "__main__":
    main()
