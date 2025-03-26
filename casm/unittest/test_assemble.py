#!/usr/bin/python3
# coding:utf-8

import os
import unittest
from unittest import mock

from casm.utils import assemble


class Test_assemble_variables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.variables = assemble.assemble_variables({"unit": "test"})

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_iter(self):
        for var in self.variables:
            self.assertIsInstance(var, str)

    def test_setitem(self):
        self.variables["demo"] = "test"
        del self.variables["demo"]


class Test_assemble_file(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.instance = os.path.join("example", "instance.yml")
        cls.template = os.path.join("example", "template.yml")
        cls.file = assemble.assemble_file(cls.instance)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_substitute(self):
        self.assertIsInstance(self.file.substitute("test"), str)

    @mock.patch.object(assemble, "safe_dump_file", mock.MagicMock())
    def test_dump_template(self):
        self.file.dump_template()


if __name__ == "__main__":
    unittest.main()
