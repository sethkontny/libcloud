# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = [
    'Zone',
    'Record',
    'DNSDriver'
]

from libcloud.common.base import ConnectionUserAndKey, BaseDriver
from libcloud.dns.types import RecordType


class Zone(object):
    """
    DNS zone.
    """

    def __init__(self, id, domain, type, ttl, driver, extra=None):
        """
        :param id: Zone id.
        :type id: ``str``

        :param domain: The name of the domain.
        :type domain: ``str``

        :param type: Zone type (master, slave).
        :type type: ``str``

        :param ttl: Default TTL for records in this zone (in seconds).
        :type ttl: ``int``

        :param driver: DNSDriver instance.
        :type driver: :class:`DNSDriver`

        :param extra: (optional) Extra attributes (driver specific).
        :type extra: ``dict``
        """
        self.id = str(id) if id else None
        self.domain = domain
        self.type = type
        self.ttl = ttl or None
        self.driver = driver
        self.extra = extra or {}

    def list_records(self):
        return self.driver.list_records(zone=self)

    def create_record(self, name, type, data, extra=None):
        return self.driver.create_record(name=name, zone=self, type=type,
                                         data=data, extra=extra)

    def update(self, domain=None, type=None, ttl=None, extra=None):
        return self.driver.update_zone(zone=self, domain=domain, type=type,
                                       ttl=ttl, extra=extra)

    def delete(self):
        return self.driver.delete_zone(zone=self)

    def __repr__(self):
        return ('<Zone: domain=%s, ttl=%s, provider=%s ...>' %
                (self.domain, self.ttl, self.driver.name))


class Record(object):
    """
    Zone record / resource.
    """

    def __init__(self, id, name, type, data, zone, driver, extra=None):
        """
        :param id: Record id
        :type id: ``str``

        :param name: Hostname or FQDN.
        :type name: ``str``

        :param type: DNS record type (A, AAAA, ...).
        :type type: :class:`RecordType`

        :param data: Data for the record (depends on the record type).
        :type data: ``str``

        :param zone: Zone instance.
        :type zone: :class:`Zone`

        :param driver: DNSDriver instance.
        :type driver: :class:`DNSDriver`

        :param extra: (optional) Extra attributes (driver specific).
        :type extra: ``dict``
        """
        self.id = str(id) if id else None
        self.name = name
        self.type = type
        self.data = data
        self.zone = zone
        self.driver = driver
        self.extra = extra or {}

    def update(self, name=None, type=None, data=None, extra=None):
        return self.driver.update_record(record=self, name=name, type=type,
                                         data=data, extra=extra)

    def delete(self):
        return self.driver.delete_record(record=self)

    def __repr__(self):
        return ('<Record: zone=%s, name=%s, type=%s, data=%s, provider=%s '
                '...>' %
                (self.zone.id, self.name, RecordType.__repr__(self.type),
                 self.data, self.driver.name))


class DNSDriver(BaseDriver):
    """
    A base DNSDriver class to derive from

    This class is always subclassed by a specific driver.
    """
    connectionCls = ConnectionUserAndKey
    name = None
    website = None

    def __init__(self, key, secret=None, secure=True, host=None, port=None,
                 **kwargs):
        """
        :param    key: API key or username to used (required)
        :type     key: ``str``

        :param    secret: Secret password to be used (required)
        :type     secret: ``str``

        :param    secure: Weither to use HTTPS or HTTP. Note: Some providers
                only support HTTPS, and it is on by default.
        :type     secure: ``bool``

        :param    host: Override hostname used for connections.
        :type     host: ``str``

        :param    port: Override port used for connections.
        :type     port: ``int``

        :return: ``None``
        """
        super(DNSDriver, self).__init__(key=key, secret=secret, secure=secure,
                                        host=host, port=port, **kwargs)

    def list_record_types(self):
        """
        Return a list of RecordType objects supported by the provider.

        :return: ``list`` of :class:`RecordType`
        """
        return list(self.RECORD_TYPE_MAP.keys())

    def iterate_zones(self):
        """
        Return a generator to iterate over available zones.

        :rtype: ``generator`` of :class:`Zone`
        """
        raise NotImplementedError(
            'iterate_zones not implemented for this driver')

    def list_zones(self):
        """
        Return a list of zones.

        :return: ``list`` of :class:`Zone`
        """
        return list(self.iterate_zones())

    def iterate_records(self, zone):
        """
        Return a generator to iterate over records for the provided zone.

        :param zone: Zone to list records for.
        :type zone: :class:`Zone`

        :rtype: ``generator`` of :class:`Record`
        """
        raise NotImplementedError(
            'iterate_records not implemented for this driver')

    def list_records(self, zone):
        """
        Return a list of records for the provided zone.

        :param zone: Zone to list records for.
        :type zone: L{Zone}

        :return: ``list`` of :class:`Record`
        """
        return list(self.iterate_records(zone))

    def get_zone(self, zone_id):
        """
        Return a Zone instance.

        :param zone_id: ID of the required zone
        :type  zone_id: ``str``

        :rtype: :class:`Zone`
        """
        raise NotImplementedError(
            'get_zone not implemented for this driver')

    def get_record(self, zone_id, record_id):
        """
        Return a Record instance.

        :param zone_id: ID of the required zone
        :type  zone_id: ``str``

        :param record_id: ID of the required record
        :type  record_id: ``str``

        :rtype: :class:`Record`
        """
        raise NotImplementedError(
            'get_record not implemented for this driver')

    def create_zone(self, domain, type='master', ttl=None, extra=None):
        """
        Create a new zone.

        :param domain: Zone domain name (e.g. example.com)
        :type domain: ``str``

        :param type: Zone type (master / slave).
        :type  type: ``str``

        :param ttl: TTL for new records. (optional)
        :type  ttl: ``int``

        :param extra: Extra attributes (driver specific). (optional)
        :type extra: ``dict``

        :rtype: :class:`Zone`
        """
        raise NotImplementedError(
            'create_zone not implemented for this driver')

    def update_zone(self, zone, domain, type='master', ttl=None, extra=None):
        """
        Update en existing zone.

        :param zone: Zone to update.
        :type  zone: :class:`Zone`

        :param domain: Zone domain name (e.g. example.com)
        :type  domain: ``str``

        :param type: Zone type (master / slave).
        :type  type: ``str``

        :param ttl: TTL for new records. (optional)
        :type  ttl: ``int``

        :param extra: Extra attributes (driver specific). (optional)
        :type  extra: ``dict``

        :rtype: :class:`Zone`
        """
        raise NotImplementedError(
            'update_zone not implemented for this driver')

    def create_record(self, name, zone, type, data, extra=None):
        """
        Create a new record.

        :param name: Record name without the domain name (e.g. www).
                     Note: If you want to create a record for a base domain
                     name, you should specify empty string ('') for this
                     argument.
        :type  name: ``str``

        :param zone: Zone where the requested record is created.
        :type  zone: :class:`Zone`

        :param type: DNS record type (A, AAAA, ...).
        :type  type: :class:`RecordType`

        :param data: Data for the record (depends on the record type).
        :type  data: ``str``

        :param extra: Extra attributes (driver specific). (optional)
        :type extra: ``dict``

        :rtype: :class:`Record`
        """
        raise NotImplementedError(
            'create_record not implemented for this driver')

    def update_record(self, record, name, type, data, extra):
        """
        Update an existing record.

        :param record: Record to update.
        :type  record: :class:`Record`

        :param name: Record name without the domain name (e.g. www).
                     Note: If you want to create a record for a base domain
                     name, you should specify empty string ('') for this
                     argument.
        :type  name: ``str``

        :param type: DNS record type (A, AAAA, ...).
        :type  type: :class:`RecordType`

        :param data: Data for the record (depends on the record type).
        :type  data: ``str``

        :param extra: (optional) Extra attributes (driver specific).
        :type  extra: ``dict``

        :rtype: :class:`Record`
        """
        raise NotImplementedError(
            'update_record not implemented for this driver')

    def delete_zone(self, zone):
        """
        Delete a zone.

        Note: This will delete all the records belonging to this zone.

        :param zone: Zone to delete.
        :type  zone: :class:`Zone`

        :rtype: ``bool``
        """
        raise NotImplementedError(
            'delete_zone not implemented for this driver')

    def delete_record(self, record):
        """
        Delete a record.

        :param record: Record to delete.
        :type  record: :class:`Record`

        :rtype: ``bool``
        """
        raise NotImplementedError(
            'delete_record not implemented for this driver')

    def _string_to_record_type(self, string):
        """
        Return a string representation of a DNS record type to a
        libcloud RecordType ENUM.
        """
        string = string.upper()
        record_type = getattr(RecordType, string)
        return record_type
