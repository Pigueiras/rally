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

import datetime as dt

from rally import consts
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.ceilometer import utils as ceiloutils
from rally.task import atomic
from rally.task import validation


class CeilometerCustom(ceiloutils.CeilometerScenario):
    """Benchmark scenaros for custom CERN usecases."""

    def _get_timestamp_from_hours_ago(self, hours):
        """Get timestamp from hours ago

        :param hours: how many hours ago
        """
        return (dt.datetime.utcnow() - dt.timedelta(hours=hours)).strftime(
            "%Y-%m-%dT%H:%M:%S")

    @validation.required_services(consts.Service.CEILOMETER)
    @validation.required_openstack(users=True)
    @scenario.configure()
    def list_samples_in_last_hours(self, meter_name, hours, limit):
        """Fetch samples from the last hours

        :param meter_name: the name of the registered meter
        :param hours: starting point for the timestamp interval
        :param limit: how many samples we want to get
        """

        key = self._make_profiler_key("ceilometer.list_sample_in_last_hours")
        query = [
            {
                "field": "timestamp",
                "value": self._get_timestamp_from_hours_ago(hours),
                "op": "gt"
            },
        ]

        with atomic.ActionTimer(self, key):
            self.clients("ceilometer").samples.list(meter_name=meter_name,
                                                    q=query,
                                                    limit=limit)
