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

from rally import consts
from rally.deploy import engine
from rally import objects

@engine.configure(name="ExistingCloudNonAdmin")
class ExistingCloudNonAdmin(engine.EngineFactory):
    """Just use an existing OpenStack deployment without deploying anything.

    To use ExistingCloudNonAdmin, you should put endpoint information to
    the config:

        {
            "type": "ExistingCloudNonAdmin",
            "auth_url": "http://localhost:5000/v2.0/",
            "region_name": "RegionOne",
            "endpoint_type": "public",
            "users": [
                {
                    "username": "demo",
                    "password": "password",
                    "tenant_name": "demo"
                }
            ]
        }

    Or, using keystone v3 API endpoint:

        {
            "type": "ExistingCloudNonAdmin",
            "auth_url": "http://localhost:5000/v3/",
            "region_name": "RegionOne",
            "endpoint_type": "public",
            "users": [
                {
                    "username": "demo",
                    "password": "password",
                    "user_domain_name": "demo",
                    "project_name": "demo",
                    "project_domain_name": "demo",
                }
            ]
        }
    """

    CONFIG_SCHEMA = {
        "type": "object",

        "definitions": {
            "user": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                },
                "oneOf": [
                    {
                        # v2.0 authentication
                        "properties": {
                            "tenant_name": {"type": "string"},
                        },
                        "required": ["username", "password", "tenant_name"],
                    },
                    {
                        # Authentication in project scope
                        "properties": {
                            "user_domain_name": {"type": "string"},
                            "project_name": {"type": "string"},
                            "project_domain_name": {"type": "string"},
                        },
                        "required": ["username", "password", "project_name"],
                    }
                ]
            }
        },

        "properties": {
            "type": {"type": "string"},
            "auth_url": {"type": "string"},
            "region_name": {"type": "string"},
            "endpoint_type": {"type": "string",
                              "enum": [consts.EndpointType.INTERNAL,
                                       consts.EndpointType.PUBLIC]},
        },
        "anyOf": [
            {
                "users": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/user"}
                },
                "required": ["type", "auth_url", "users"]
            }
        ]
    }

    def _create_endpoint(self, common, user, permission):
        return objects.Endpoint(
            common["auth_url"], user["username"], user["password"],
            tenant_name=user.get("project_name", user.get("tenant_name")),
            permission=permission,
            region_name=common.get("region_name"),
            endpoint_type=common.get("endpoint_type",
                                     consts.EndpointType.PUBLIC),
            domain_name=user.get("domain_name"),
            user_domain_name=user.get("user_domain_name", "Default"),
            project_domain_name=user.get("project_domain_name", "Default")
        )

    def deploy(self):
        permissions = consts.EndpointPermission

        users = [self._create_endpoint(self.config, user, permissions.USER)
                 for user in self.config.get("users", [])]

        return {"users": users}

    def cleanup(self):
        pass
