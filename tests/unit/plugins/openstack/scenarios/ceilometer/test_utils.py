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

import copy

import mock
from oslotest import mockpatch

from rally.plugins.openstack.scenarios.ceilometer import utils
from tests.unit import test

BM_UTILS = "rally.benchmark.utils"
CEILOMETER_UTILS = "rally.plugins.openstack.scenarios.ceilometer.utils"


class CeilometerScenarioTestCase(test.ClientsTestCase):
    def setUp(self):
        super(CeilometerScenarioTestCase, self).setUp()
        self.scenario = utils.CeilometerScenario()
        self.res_is = mockpatch.Patch(BM_UTILS + ".resource_is")
        self.get_fm = mockpatch.Patch(BM_UTILS + ".get_from_manager")
        self.wait_for = mockpatch.Patch(CEILOMETER_UTILS +
                                        ".bench_utils.wait_for")
        self.useFixture(self.wait_for)
        self.useFixture(self.res_is)
        self.useFixture(self.get_fm)
        self.gfm = self.get_fm.mock

    def test__list_alarms_by_id(self):
        self.assertEqual(self.clients("ceilometer").alarms.get.return_value,
                         self.scenario._list_alarms("alarm-id"))
        self.clients("ceilometer").alarms.get.assert_called_once_with(
            "alarm-id")
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.list_alarms")

    def test__list_alarms(self):
        self.assertEqual(self.clients("ceilometer").alarms.list.return_value,
                         self.scenario._list_alarms())
        self.clients("ceilometer").alarms.list.assert_called_once_with()
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.list_alarms")

    def test__create_alarm(self):
        alarm_dict = {"alarm_id": "fake-alarm-id"}
        orig_alarm_dict = copy.copy(alarm_dict)
        self.scenario._generate_random_name = mock.Mock()
        self.assertEqual(self.scenario._create_alarm("fake-meter-name", 100,
                                                     alarm_dict),
                         self.clients("ceilometer").alarms.create.return_value)
        self.clients("ceilometer").alarms.create.assert_called_once_with(
            meter_name="fake-meter-name",
            threshold=100,
            description="Test Alarm",
            alarm_id="fake-alarm-id",
            name=self.scenario._generate_random_name.return_value)
        # ensure that _create_alarm() doesn't modify the alarm dict as
        # a side-effect
        self.assertDictEqual(alarm_dict, orig_alarm_dict)
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.create_alarm")

    def test__delete_alarms(self):
        self.scenario._delete_alarm("alarm-id")
        self.clients("ceilometer").alarms.delete.assert_called_once_with(
            "alarm-id")
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.delete_alarm")

    def test__update_alarm(self):
        alarm_diff = {"description": "Changed Test Description"}
        orig_alarm_diff = copy.copy(alarm_diff)
        self.scenario._update_alarm("alarm-id", alarm_diff)
        self.clients("ceilometer").alarms.update.assert_called_once_with(
            "alarm-id", **alarm_diff)
        # ensure that _create_alarm() doesn't modify the alarm dict as
        # a side-effect
        self.assertDictEqual(alarm_diff, orig_alarm_diff)
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.update_alarm")

    def test__get_alarm_history(self):
        self.assertEqual(
            self.scenario._get_alarm_history("alarm-id"),
            self.clients("ceilometer").alarms.get_history.return_value)
        self.clients("ceilometer").alarms.get_history.assert_called_once_with(
            "alarm-id")
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.get_alarm_history")

    def test__get_alarm_state(self):
        self.assertEqual(
            self.scenario._get_alarm_state("alarm-id"),
            self.clients("ceilometer").alarms.get_state.return_value)
        self.clients("ceilometer").alarms.get_state.assert_called_once_with(
            "alarm-id")
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.get_alarm_state")

    def test__set_alarm_state(self):
        alarm = mock.Mock()
        self.clients("ceilometer").alarms.create.return_value = alarm
        return_alarm = self.scenario._set_alarm_state(alarm, "ok", 100)
        self.wait_for.mock.assert_called_once_with(
            alarm,
            is_ready=self.res_is.mock(),
            update_resource=self.gfm(),
            timeout=100, check_interval=1)
        self.res_is.mock.assert_has_calls([mock.call("ok")])
        self.assertEqual(self.wait_for.mock(), return_alarm)
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.set_alarm_state")

    def test__list_meters(self):
        self.assertEqual(self.scenario._list_meters(),
                         self.clients("ceilometer").meters.list.return_value)
        self.clients("ceilometer").meters.list.assert_called_once_with()
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.list_meters")

    def test__list_resources(self):
        self.assertEqual(
            self.scenario._list_resources(),
            self.clients("ceilometer").resources.list.return_value)
        self.clients("ceilometer").resources.list.assert_called_once_with()
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.list_resources")

    def test__list_samples(self):
        self.assertEqual(
            self.scenario._list_samples(),
            self.clients("ceilometer").samples.list.return_value)
        self.clients("ceilometer").samples.list.assert_called_once_with()
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.list_samples")

    def test__get_resource(self):
        self.assertEqual(self.scenario._get_resource("fake-resource-id"),
                         self.clients("ceilometer").resources.get.return_value)
        self.clients("ceilometer").resources.get.assert_called_once_with(
            "fake-resource-id")
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.get_resource")

    def test__get_stats(self):
        self.assertEqual(
            self.scenario._get_stats("fake-meter"),
            self.clients("ceilometer").statistics.list.return_value)
        self.clients("ceilometer").statistics.list.assert_called_once_with(
            "fake-meter")
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.get_stats")

    def test__create_meter(self):
        self.scenario._generate_random_name = mock.Mock()
        self.assertEqual(
            self.scenario._create_meter(fakearg="fakearg"),
            self.clients("ceilometer").samples.create.return_value[0])
        self.clients("ceilometer").samples.create.assert_called_once_with(
            counter_name=self.scenario._generate_random_name.return_value,
            fakearg="fakearg")
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.create_meter")

    def test__query_alarms(self):
        self.assertEqual(
            self.scenario._query_alarms("fake-filter", "fake-orderby", 10),
            self.clients("ceilometer").query_alarms.query.return_value)
        self.clients("ceilometer").query_alarms.query.assert_called_once_with(
            "fake-filter", "fake-orderby", 10)
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.query_alarms")

    def test__query_alarm_history(self):
        self.assertEqual(
            self.scenario._query_alarm_history(
                "fake-filter", "fake-orderby", 10),
            self.clients("ceilometer").query_alarm_history.query.return_value)
        self.clients(
            "ceilometer").query_alarm_history.query.assert_called_once_with(
                "fake-filter", "fake-orderby", 10)
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.query_alarm_history")

    def test__query_samples(self):
        self.assertEqual(
            self.scenario._query_samples("fake-filter", "fake-orderby", 10),
            self.clients("ceilometer").query_samples.query.return_value)
        self.clients("ceilometer").query_samples.query.assert_called_once_with(
            "fake-filter", "fake-orderby", 10)
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.query_samples")

    def test__create_sample_no_resource_id(self):
        self.scenario._generate_random_name = mock.Mock()
        created_sample = self.scenario._create_sample("test-counter-name",
                                                      "test-counter-type",
                                                      "test-counter-unit",
                                                      "test-counter-volume")
        self.assertEqual(
            created_sample,
            self.clients("ceilometer").samples.create.return_value)
        self.clients("ceilometer").samples.create.assert_called_once_with(
            counter_name="test-counter-name",
            counter_type="test-counter-type",
            counter_unit="test-counter-unit",
            counter_volume="test-counter-volume",
            resource_id=self.scenario._generate_random_name.return_value)
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.create_sample")

    def test__create_sample(self):
        created_sample = self.scenario._create_sample("test-counter-name",
                                                      "test-counter-type",
                                                      "test-counter-unit",
                                                      "test-counter-volume",
                                                      "test-resource-id")
        self.assertEqual(
            created_sample,
            self.clients("ceilometer").samples.create.return_value)
        self.clients("ceilometer").samples.create.assert_called_once_with(
            counter_name="test-counter-name",
            counter_type="test-counter-type",
            counter_unit="test-counter-unit",
            counter_volume="test-counter-volume",
            resource_id="test-resource-id")
        self._test_atomic_action_timer(self.scenario.atomic_actions(),
                                       "ceilometer.create_sample")
