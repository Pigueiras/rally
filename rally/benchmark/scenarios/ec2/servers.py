# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from rally.benchmark.scenarios import base
from rally.benchmark.scenarios.ec2 import utils
from rally.benchmark import validation
from rally.common import log as logging
from rally import consts


LOG = logging.getLogger(__name__)


class EC2Servers(utils.EC2Scenario):
    """Benchmark scenarios for servers using EC2."""

    @validation.required_services(consts.Service.EC2)
    @validation.required_openstack(users=True)
    @base.scenario()
    def list_servers(self):
        """List all servers.

        This simple scenario tests the EC2 API list function by listing
        all the servers.
        """
        self._list_servers()
