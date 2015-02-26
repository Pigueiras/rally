# Copyright 2014: Mirantis Inc.
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

import six

from rally.benchmark import utils
from rally import consts

def resource(service, resource, order=0, admin_required=False,
             perform_for_admin_only=False, tenant_resource=False,
             max_attempts=3, timeout=600, interval=1, threads=20):
    """Decorator that overrides resource specification.

    Just put it on top of your resource class and specify arguments that you
    need.

    :param service: It is equal to client name for corresponding service.
                    E.g. "nova", "cinder" or "zaqar"
    :param resource: Client manager name for resource. E.g. in case of
                     nova.servers you should write here "servers"
    :param order: Used to adjust priority of cleanup for different resource
                  types
    :param admin_required: Admin user is required
    :param perform_for_admin_only: Perform cleanup for admin user only
    :param tenant_resource: Perform deletion only 1 time per tenant
    :param max_attempts: Max amount of attempts to delete single resource
    :param timeout: Max duration of deletion in seconds
    :param interval: Resource status pooling interval
    :param threads: Amount of threads (workers) that are deleting resources
                    simultaneously
    """

    def inner(cls):
        # TODO(boris-42): This can be written better I believe =)
        cls._service = service
        cls._resource = resource
        cls._order = order
        cls._admin_required = admin_required
        cls._perform_for_admin_only = perform_for_admin_only
        cls._max_attempts = max_attempts
        cls._timeout = timeout
        cls._interval = interval
        cls._threads = threads
        cls._tenant_resource = tenant_resource

        return cls

    return inner


@resource(service=None, resource=None)
class ResourceManager(object):
    """Base class for cleanup plugins for specific resources.

    You should use @resource decorator to specify major configuration of
    resource manager. Usually you should specify: service, resource and order.

    If project python client is very specific, you can override delete(),
    list() and is_deleted() methods to make them fit to your case.
    """

    def __init__(self, resource=None, admin=None, user=None, tenant_uuid=None):
        self.admin = admin
        self.user = user
        self.raw_resource = resource
        self.tenant_uuid = tenant_uuid
        self.prefix = "rally-"
        self.delete_matched = True

    def _manager(self):
        client = self._admin_required and self.admin or self.user
        return getattr(getattr(client, self._service)(), self._resource)

    def id(self):
        """Returns id of resource."""
        return self.raw_resource.id

    def name(self):
        """Returns name of resource."""
        return getattr(self.raw_resource, "name", "")

    def is_deletion_resource(self):
        """Checks if the resource is a deletion target.

        If delete_matched flag set to True, this method returns True when
        resource name starts with prefix but if the flag is False, this
        returns True when resource name doesn't start with prefix.
        """
        # NOTE(wtakase): Because except for the following services have not
        #                been tested yet, those resources are the targets.
        # TODO(wtakase): After confirming all services, we should delete
        #                following lines
        tested_services = [consts.Service.CINDER, consts.Service.GLANCE,
                           consts.Service.KEYSTONE, consts.Service.NEUTRON,
                           consts.Service.NOVA, consts.Service.DESIGNATE,
                           consts.Service.MISTRAL, consts.Service.HEAT,
                           consts.Service.CEILOMETER]
        if self._service not in tested_services:
            return True

        name = self.name()
        if not isinstance(name, six.string_types):
            return False
        if name.startswith(self.prefix):
            return self.delete_matched
        return not self.delete_matched

    def is_deleted(self):
        """Checks if the resource is deleted.

        Fetch resource by id from service and check it status.
        In case of NotFound or status is DELETED or DELETE_COMPLETE returns
        True, otherwise False.
        """
        try:
            resource = self._manager().get(self.id())
        except Exception as e:
            return getattr(e, "code", getattr(e, "http_status", 400)) == 404

        return utils.get_status(resource) in ("DELETED", "DELETE_COMPLETE")

    def delete(self):
        """Delete resource that corresponds to instance of this class."""
        self._manager().delete(self.id())

    def list(self):
        """List all resources specific for admin or user."""
        return self._manager().list()
