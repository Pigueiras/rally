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

from rally.benchmark.scenarios import base
from rally.benchmark import validation
from rally import consts
from rally.plugins.openstack.scenarios.neutron import utils


class NeutronLoadbalancerV1(utils.NeutronScenario):
    """Benchmark scenarios for Neutron Loadbalancer v1."""

    @validation.restricted_parameters("subnet_id", subdict="pool_create_args")
    @validation.required_services(consts.Service.NEUTRON)
    @validation.required_openstack(users=True)
    @validation.required_contexts("network")
    @base.scenario(context={"cleanup": ["neutron"]})
    def create_and_list_pools(self, pool_create_args=None):
        """Create a pool(v1) and then list pools(v1).

        Measure the "neutron lb-pool-list" command performance.
        The scenario creates a pool for every subnet and then lists pools.

        :param pool_create_args: dict, POST /lb/pools request options
        """
        for net in self.context.get("tenant", {}).get("networks", []):
            for subnet_id in net["subnets"]:
                self._create_v1_pool(subnet_id, **pool_create_args)
        self._list_v1_pools()
