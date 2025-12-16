#!/usr/bin/python3
# coding:utf-8

from unittest import TestCase
from unittest import main
from unittest import mock

from casm.utils import common


class Test_utils_common(TestCase):

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

    @mock.patch.object(common.os.path, "ismount")
    def test_ismount_true(self, mock_ismount):
        mock_ismount.side_effect = [True]
        self.assertTrue(common.ismount("/demo"))

    def test_ismount_false(self):
        self.assertFalse(common.ismount("/demo"))

    @mock.patch.object(common.os.path, "ismount")
    def test_mountpoint(self, mock_ismount):
        mock_ismount.side_effect = [True]
        self.assertEqual(common.mountpoint("/demo"), "/demo")

    def test_mountpoint_none(self):
        self.assertIsNone(common.mountpoint("/demo"))


if __name__ == "__main__":
    main()
