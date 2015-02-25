# Copyright 2015 Cisco Systems, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from rally.benchmark.scenarios.swift import objects
from tests.unit import fakes
from tests.unit import test


class SwiftObjectsTestCase(test.TestCase):

    def test_create_container_and_object_then_list_objects(self):
        scenario = objects.SwiftObjects()
        scenario._create_container = mock.MagicMock(return_value="AA")
        scenario._upload_object = mock.MagicMock()
        scenario._list_objects = mock.MagicMock()

        scenario.create_container_and_object_then_list_objects(
            objects_per_container=5,
            object_size=100)

        self.assertEqual(1, scenario._create_container.call_count)
        self.assertEqual(5, scenario._upload_object.call_count)
        scenario._list_objects.assert_called_once_with("AA")

        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.create_5_objects")

    def test_create_container_and_object_then_delete_all(self):
        scenario = objects.SwiftObjects()
        scenario._create_container = mock.MagicMock(return_value="BB")
        scenario._upload_object = mock.MagicMock(
            side_effect=[("etaaag", "ooobj_%i" % i) for i in range(3)])
        scenario._delete_object = mock.MagicMock()
        scenario._delete_container = mock.MagicMock()

        scenario.create_container_and_object_then_delete_all(
            objects_per_container=3,
            object_size=10)

        self.assertEqual(1, scenario._create_container.call_count)
        self.assertEqual(3, scenario._upload_object.call_count)
        scenario._delete_object.assert_has_calls(
            [mock.call("BB", "ooobj_%i" % i,
                       atomic_action=False) for i in range(3)])
        scenario._delete_container.assert_called_once_with("BB")

        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.create_3_objects")
        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.delete_3_objects")

    def test_create_container_and_object_then_download_object(self):
        scenario = objects.SwiftObjects()
        scenario._create_container = mock.MagicMock(return_value="CC")
        scenario._upload_object = mock.MagicMock(
            side_effect=[("etaaaag", "obbbj_%i" % i) for i in range(2)])
        scenario._download_object = mock.MagicMock()

        scenario.create_container_and_object_then_download_object(
            objects_per_container=2,
            object_size=50)

        self.assertEqual(1, scenario._create_container.call_count)
        self.assertEqual(2, scenario._upload_object.call_count)
        scenario._download_object.assert_has_calls(
            [mock.call("CC", "obbbj_%i" % i,
                       atomic_action=False) for i in range(2)])

        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.create_2_objects")
        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.download_2_objects")

    def test_functional_create_container_and_object_then_list_objects(self):
        names_list = ["AA", "BB", "CC", "DD"]

        scenario = objects.SwiftObjects(clients=fakes.FakeClients())
        scenario._generate_random_name = mock.MagicMock(side_effect=names_list)
        scenario._list_objects = mock.MagicMock()

        scenario.create_container_and_object_then_list_objects(
            objects_per_container=3,
            object_size=100)

        scenario._list_objects.assert_called_once_with("AA")

        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.create_3_objects")

    def test_functional_create_container_and_object_then_delete_all(self):
        names_list = ["111", "222", "333", "444", "555"]

        scenario = objects.SwiftObjects(clients=fakes.FakeClients())
        scenario._generate_random_name = mock.MagicMock(side_effect=names_list)
        scenario._delete_object = mock.MagicMock()
        scenario._delete_container = mock.MagicMock()

        scenario.create_container_and_object_then_delete_all(
            objects_per_container=4,
            object_size=240)

        scenario._delete_object.assert_has_calls(
            [mock.call("111", name,
                       atomic_action=False) for name in names_list[1:]])
        scenario._delete_container.assert_called_once_with("111")

        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.create_4_objects")
        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.delete_4_objects")

    def test_functional_create_container_and_object_then_download_object(self):
        names_list = ["aaa", "bbb", "ccc", "ddd", "eee", "fff"]

        scenario = objects.SwiftObjects(clients=fakes.FakeClients())
        scenario._generate_random_name = mock.MagicMock(side_effect=names_list)
        scenario._download_object = mock.MagicMock()

        scenario.create_container_and_object_then_download_object(
            objects_per_container=5,
            object_size=750)

        scenario._download_object.assert_has_calls(
            [mock.call("aaa", name,
                       atomic_action=False) for name in names_list[1:]])

        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.create_5_objects")
        self._test_atomic_action_timer(scenario.atomic_actions(),
                                       "swift.download_5_objects")
