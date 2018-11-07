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

"""
SQLAlchemy models for container service
"""

from oslo_db.sqlalchemy import models
from oslo_serialization import jsonutils as json
from oslo_utils import timeutils
import six.moves.urllib.parse as urlparse
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Date
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import schema
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator, TEXT

import zun.conf


def MediumText():
    return Text().with_variant(MEDIUMTEXT(), 'mysql')


def table_args():
    engine_name = urlparse.urlparse(zun.conf.CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': zun.conf.CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class JsonEncodedType(TypeDecorator):
    """Abstract base type serialized as json-encoded string in db."""
    type = None
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            # Save default value according to current type to keep the
            # interface the consistent.
            value = self.type()
        elif not isinstance(value, self.type):
            raise TypeError("%s supposes to store %s objects, but %s given"
                            % (self.__class__.__name__,
                               self.type.__name__,
                               type(value).__name__))
        serialized_value = json.dump_as_bytes(value)
        return serialized_value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class JSONEncodedDict(JsonEncodedType):
    """Represents dict serialized as json-encoded string in db."""
    type = dict


class JSONEncodedList(JsonEncodedType):
    """Represents list serialized as json-encoded string in db."""
    type = list


class ZunBase(models.TimestampMixin,
              models.ModelBase):

    metadata = None

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d

    def save(self, session=None):
        import zun.db.sqlalchemy.api as db_api

        if session is None:
            session = db_api.get_session()

        super(ZunBase, self).save(session)


Base = declarative_base(cls=ZunBase)


class ZunService(Base):
    """Represents health status of various zun services"""
    __tablename__ = 'zun_service'
    __table_args__ = (
        schema.UniqueConstraint("host", "binary",
                                name="uniq_zun_service0host0binary"),
        table_args()
    )

    id = Column(Integer, primary_key=True)
    host = Column(String(255))
    binary = Column(String(255))
    disabled = Column(Boolean, default=False)
    disabled_reason = Column(String(255))
    last_seen_up = Column(DateTime, nullable=True)
    forced_down = Column(Boolean, default=False)
    report_count = Column(Integer, nullable=False, default=0)

class User(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'user'
    __table_args__ = (
        table_args()
    )
    id = Column(Integer, primary_key=True)
    user_name = Column(String(200), unique = True, nullable=False)
    last_name = Column(String(200))
    first_name = Column(String(200))
    middle_name = Column(String(20))
    password = Column(String(200))
    account_status = Column(Integer)
    failed_attempt = Column(Integer)
    last_login_method = Column(Integer)
    current_user_charge_tier = Column(Integer)
    admin_ind = Column(Integer)
    uuid = Column(String(128), unique = True)
    displayname = Column(String(512), unique = True)
    passreset_url = Column(String(200))
    activation_url = Column(String(200))
    activation_expir_date = Column(DateTime)
    passreset_expir_date = Column(DateTime)
    last_login_time = Column(DateTime)
    last_success_login_ip = Column(String(128))
    last_failed_login_ip = Column(String(128))



class Provideraccount(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'provideraccount'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), ForeignKey("user.uuid"), nullable=False)
    #user = relationship("user")
    provider_id = Column(String(128), ForeignKey("provider.uuid"), nullable=False)
    #provider = relationship("provider")
    access_key_id = Column(String(200))
    access_key_str = Column(String(200))
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)
    displayname2 = Column(String(512), unique=True)

class Providervm(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'providervm'

    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime, nullable=True)
    provider_account_id = Column(String(128), ForeignKey("provideraccount.uuid"), nullable=False)
    #provider_account = relationship("provideraccount")
    vm_external_ipv4 = Column(String(20))
    vm_internal_ipv4 = Column(String(20))
    status = Column(Integer)
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)

class Instance(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'instance'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), ForeignKey("user.uuid"), nullable=False)
    #user = relationship("user")
    instance_type_id = Column(String(128), ForeignKey("instancetype.uuid"), nullable=False)
    #instance_type = relationship("instancetype")
    provider_vm_id = Column(String(128), ForeignKey("providervm.uuid"), nullable=False)
    #provider_vm = relationship("providervm")
    current_status = Column(Integer, nullable=True)
    current_status_time = Column(DateTime, nullable=True)
    create_time = Column(DateTime, nullable=True)
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)
    displayname2 = Column(String(512), unique=True)
    displayname3 = Column(String(512), unique=True)

class Storagerate(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'storagerate'

    id = Column(Integer, primary_key=True)
    storage_size = Column(Integer)
    provider_region_id = Column(String(128), ForeignKey("providerregion.uuid"), nullable=False)
    #provider_region = relationship("providerregion")
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    storage_rate = Column(Float)
    enable_ind = Column(Integer)
    user_tier = Column(Integer)
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)

class Provider(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'provider'

    id = Column(Integer, primary_key=True)
    provider = Column(String(200), unique=True)
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)

class Providerregion(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'providerregion'

    id = Column(Integer, primary_key=True)
    provider_id = Column(String(128), ForeignKey("provider.uuid"), nullable=False)
    #provider = relationship("provider")
    region = Column(String(200))
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)

class Instancetype(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'instancetype'

    id = Column(Integer, primary_key=True)
    memory_size = Column(Integer, nullable=False)
    no_of_cpu = Column(Integer, nullable=False)
    provider_region_id = Column(String(128), ForeignKey("providerregion.uuid"), nullable=False)
    #provider_region = relationship("providerregion")
    enable_ind = Column(Integer)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)

class Usage(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'usage'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), ForeignKey("user.uuid"), nullable=False)
    #user = relationship("user")
    instance_id = Column(String(128), ForeignKey("instance.uuid"), nullable=False)
    #instance = relationship("instance")
    compute_rate_id = Column(String(128), ForeignKey("computerate.uuid"), nullable=False)
    #compute_rate = relationship("computerate")
    storage_rate_id = Column(String(128), ForeignKey("storagerate.uuid"), nullable=False)
    #storage_rate = relationship("storagerate")
    start_time = Column(DateTime, nullable=True)
    stop_time = Column(DateTime, nullable=True)
    duration = Column(Integer)
    cost = Column(Float)
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)
    displayname2 = Column(String(512), unique=True)
    displayname3 = Column(String(512), unique=True)
    displayname4 = Column(String(512), unique=True)

class Statement(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'statement'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), ForeignKey("user.uuid"), nullable=False)
    #user = relationship("user")
    previous_balance = Column(String(20))
    billing_begin_date = Column(DateTime, nullable=True)
    billing_end_date = Column(DateTime, nullable=True)
    billing_charge_amount = Column(Float)
    current_balance = Column(Float)
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)

class Computerate(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'computerate'

    id = Column(Integer, primary_key=True)
    instance_type_id = Column(String(128), ForeignKey("instancetype.uuid"), nullable=False)
    #instance_type = relationship("instancetype")
    start_date = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    compute_rate = Column(Float)
    status = Column(Integer)
    user_tier = Column(Integer)
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)

class Payment(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    statement_id = Column(String(128), ForeignKey("statement.uuid"), nullable=False)
    #statement = relationship("statement")
    amount = Column(Float)
    payment_date = Column(DateTime, nullable=True)
    payment_method_id = Column(String(128), ForeignKey("paymentmethod.uuid"), nullable=False)
    #payment_method = relationship("paymentmethod")
    status = Column(Integer)
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)
    displayname2 = Column(String(512), unique=True)

class Paymentmethod(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'paymentmethod'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), ForeignKey("user.uuid"), nullable=False)
    #user = relationship("user")
    payment_method_type = Column(String(200))
    cc_first_name = Column(String(200))
    cc_middle_name = Column(String(200))
    cc_last_name = Column(String(200))
    cc_card_no = Column(String(200))
    cc_billing_address_line1 = Column(String(200))
    cc_billing_address_line2 = Column(String(200))
    cc_billing_address_line3 = Column(String(200))
    cc_billing_address_apt_suite_no = Column(String(200))
    cc_city = Column(String(200))
    cc_state = Column(String(200))
    cc_zipcode = Column(String(20))
    cc_country = Column(String(200))
    cc_expiration_date = Column(String(20))
    cc_cvv = Column(String(10))
    pp_email = Column(String(200))
    uuid = Column(String(128), unique=True)
    displayname = Column(String(512), unique=True)


class Container(Base):
    """Represents a container."""

    __tablename__ = 'container'
    __table_args__ = (
        schema.UniqueConstraint('uuid', name='uniq_container0uuid'),
        table_args()
    )
    id = Column(Integer, primary_key=True)
    project_id = Column(String(255))
    user_id = Column(String(255))
    uuid = Column(String(36))
    container_id = Column(String(36))
    name = Column(String(255))
    image = Column(String(255))
    cpu = Column(Float)
    command = Column(String(255))
    memory = Column(String(255))
    status = Column(String(20))
    status_reason = Column(Text, nullable=True)
    task_state = Column(String(20))
    environment = Column(JSONEncodedDict)
    workdir = Column(String(255))
    ports = Column(JSONEncodedList)
    hostname = Column(String(63))
    labels = Column(JSONEncodedDict)
    meta = Column(JSONEncodedDict)
    addresses = Column(JSONEncodedDict)
    image_pull_policy = Column(Text, nullable=True)
    host = Column(String(255))
    restart_policy = Column(JSONEncodedDict)
    status_detail = Column(String(50))
    interactive = Column(Boolean, default=False)
    image_driver = Column(String(255))
    websocket_url = Column(String(255))
    websocket_token = Column(String(255))
    security_groups = Column(JSONEncodedList)
    auto_remove = Column(Boolean, default=False)
    runtime = Column(String(32))
    disk = Column(Integer, default=0)


class VolumeMapping(Base):
    """Represents a volume mapping."""

    __tablename__ = 'volume_mapping'
    __table_args__ = (
        schema.UniqueConstraint('uuid', name='uniq_volume0uuid'),
        table_args()
    )
    uuid = Column(String(36), nullable=False)
    id = Column(Integer, primary_key=True, nullable=False)
    project_id = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=True)
    volume_id = Column(String(36), nullable=False)
    volume_provider = Column(String(36), nullable=False)
    container_path = Column(String(255), nullable=True)
    container_uuid = Column(String(36), ForeignKey('container.uuid'))
    connection_info = Column(MediumText())
    container = orm.relationship(
        Container,
        backref=orm.backref('volume'),
        foreign_keys=container_uuid,
        primaryjoin='and_(VolumeMapping.container_uuid==Container.uuid)')
    auto_remove = Column(Boolean, default=False)


class Image(Base):
    """Represents an image. """

    __tablename__ = 'image'
    __table_args__ = (
        schema.UniqueConstraint('repo', 'tag', name='uniq_image0repotag'),
        table_args()
        )
    id = Column(Integer, primary_key=True)
    project_id = Column(String(255))
    user_id = Column(String(255))
    uuid = Column(String(36))
    image_id = Column(String(255))
    repo = Column(String(255))
    tag = Column(String(255))
    size = Column(String(255))


class ResourceProvider(Base):
    """Represents an resource provider. """

    __tablename__ = 'resource_provider'
    __table_args__ = (
        schema.UniqueConstraint('uuid', name='uniq_resource_provider0uuid'),
        table_args()
    )
    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(36), nullable=False)
    name = Column(String(255), nullable=False)
    root_provider = Column(String(36), nullable=False)
    parent_provider = Column(String(36), nullable=True)
    can_host = Column(Integer, default=0)


class ResourceClass(Base):
    """Represents an resource class. """

    __tablename__ = 'resource_class'
    __table_args__ = (
        schema.UniqueConstraint('uuid', name='uniq_resource_class0uuid'),
        table_args()
    )
    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(36), nullable=False)
    name = Column(String(255), nullable=False)


class Inventory(Base):
    """Represents an inventory. """

    __tablename__ = 'inventory'
    __table_args__ = (
        Index('inventory_resource_provider_id_idx',
              'resource_provider_id'),
        Index('inventory_resource_class_id_idx',
              'resource_class_id'),
        Index('inventory_resource_provider_resource_class_idx',
              'resource_provider_id', 'resource_class_id'),
        schema.UniqueConstraint(
            'resource_provider_id', 'resource_class_id',
            name='uniq_inventory0resource_provider_resource_class'),
        table_args()
    )
    id = Column(Integer, primary_key=True, nullable=False)
    resource_provider_id = Column(Integer, nullable=False)
    resource_class_id = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    reserved = Column(Integer, nullable=False)
    min_unit = Column(Integer, nullable=False)
    max_unit = Column(Integer, nullable=False)
    step_size = Column(Integer, nullable=False)
    allocation_ratio = Column(Float, nullable=False)
    is_nested = Column(Integer, nullable=False)
    blob = Column(JSONEncodedList)
    resource_provider = orm.relationship(
        "ResourceProvider",
        primaryjoin=('and_(Inventory.resource_provider_id == '
                     'ResourceProvider.id)'),
        foreign_keys=resource_provider_id)


class Allocation(Base):
    """Represents an allocation. """

    __tablename__ = 'allocation'
    __table_args__ = (
        Index('allocation_resource_provider_class_used_idx',
              'resource_provider_id', 'resource_class_id', 'used'),
        Index('allocation_resource_class_id_idx', 'resource_class_id'),
        Index('allocation_consumer_id_idx', 'consumer_id'),
        table_args()
    )
    id = Column(Integer, primary_key=True, nullable=False)
    resource_provider_id = Column(Integer, nullable=False)
    resource_class_id = Column(Integer, nullable=False)
    consumer_id = Column(String(36), nullable=False)
    used = Column(Integer, nullable=False)
    is_nested = Column(Integer, nullable=False)
    blob = Column(JSONEncodedList)
    resource_provider = orm.relationship(
        "ResourceProvider",
        primaryjoin=('and_(Allocation.resource_provider_id == '
                     'ResourceProvider.id)'),
        foreign_keys=resource_provider_id)


class ComputeNode(Base):
    """Represents a compute node. """

    __tablename__ = 'compute_node'
    __table_args__ = (
        table_args()
    )
    uuid = Column(String(36), primary_key=True, nullable=False)
    hostname = Column(String(255), nullable=False)
    numa_topology = Column(JSONEncodedDict, nullable=True)
    mem_total = Column(Integer, nullable=False, default=0)
    mem_free = Column(Integer, nullable=False, default=0)
    mem_available = Column(Integer, nullable=False, default=0)
    mem_used = Column(Integer, nullable=False, default=0)
    total_containers = Column(Integer, nullable=False, default=0)
    running_containers = Column(Integer, nullable=False, default=0)
    paused_containers = Column(Integer, nullable=False, default=0)
    stopped_containers = Column(Integer, nullable=False, default=0)
    cpus = Column(Integer, nullable=False, default=0)
    cpu_used = Column(Float, nullable=False, default=0.0)
    architecture = Column(String(32), nullable=True)
    os_type = Column(String(32), nullable=True)
    os = Column(String(64), nullable=True)
    kernel_version = Column(String(128), nullable=True)
    labels = Column(JSONEncodedDict)
    # Json string PCI Stats
    # '[{"vendor_id":"8086", "product_id":"1234", "count":3 }, ...]'
    pci_stats = Column(Text)


class Capsule(Base):
    """Represents a capsule."""

    __tablename__ = 'capsule'
    __table_args__ = (
        schema.UniqueConstraint('uuid', name='uniq_capsule0uuid'),
        table_args()
    )
    uuid = Column(String(36), nullable=False)
    id = Column(Integer, primary_key=True, nullable=False)
    host_selector = Column(String(255))
    capsule_version = Column(String(255))
    kind = Column(String(255))
    restart_policy = Column(String(255))
    project_id = Column(String(255))
    user_id = Column(String(255))

    status = Column(String(20))
    status_reason = Column(Text, nullable=True)
    meta_labels = Column(JSONEncodedDict)
    meta_name = Column(String(255))
    spec = Column(JSONEncodedDict)
    containers_uuids = Column(JSONEncodedList)
    cpu = Column(Float)
    memory = Column(String(255))
    host = Column(String(255))
    addresses = Column(JSONEncodedDict)
    volumes_info = Column(JSONEncodedDict)


class PciDevice(Base):
    """Represents a PCI host device that can be passed through to instances."""

    __tablename__ = 'pci_device'
    __table_args__ = (
        Index('ix_pci_device_compute_node_uuid',
              'compute_node_uuid'),
        Index('ix_pci_device_container_uuid',
              'container_uuid'),
        Index('ix_pci_device_compute_node_uuid_parent_addr',
              'compute_node_uuid', 'parent_addr'),
        schema.UniqueConstraint(
            "compute_node_uuid", "address",
            name="uniq_pci_device0compute_node_uuid0address")
    )
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    compute_node_uuid = Column(String(36), ForeignKey('compute_node.uuid'),
                               nullable=False)

    # physical address of device domain:bus:slot.func (0000:09:01.1)
    address = Column(String(12), nullable=False)

    vendor_id = Column(String(4), nullable=False)
    product_id = Column(String(4), nullable=False)
    dev_type = Column(String(8), nullable=False)
    dev_id = Column(String(255))

    # label is abstract device name, that is used to unify devices with the
    # same functionality with different addresses or host.
    label = Column(String(255), nullable=False)

    status = Column(String(36), nullable=False)
    # the request_id is used to identify a device that is allocated for a
    # particular request
    request_id = Column(String(36), nullable=True)

    extra_info = Column(Text)

    container_uuid = Column(String(36))

    numa_node = Column(Integer, nullable=True)

    parent_addr = Column(String(12), nullable=True)
    container = orm.relationship(Container, backref="pci_device",
                                 foreign_keys=container_uuid,
                                 primaryjoin='and_('
                                 'PciDevice.container_uuid == Container.uuid)')


class ContainerAction(Base):
    """Represents a container action.

    The intention is that there will only be one of these pre user request. A
    lookup by(container_uuid, request_id) should always return a single result.
    """

    __tablename__ = 'container_actions'
    __table_args__ = (
        Index('container_uuid_idx', 'container_uuid'),
        Index('request_id_idx', 'request_id')
    )

    id = Column(Integer, primary_key=True, nullable=False)
    action = Column(String(255))
    container_uuid = Column(String(36),
                            ForeignKey('container.uuid', ondelete='CASCADE'),
                            nullable=False)
    request_id = Column(String(255))
    user_id = Column(String(255))
    project_id = Column(String(255))
    start_time = Column(DateTime, default=timeutils.utcnow)
    finish_time = Column(DateTime)
    message = Column(String(255))
    container = orm.relationship(
        "Container", backref="container_actions",
        foreign_keys=container_uuid,
        primaryjoin='and_(ContainerAction.container_uuid == Container.uuid)'
    )


class ContainerActionEvent(Base):
    """Track events that occur during an ContainerAction."""
    __tablename__ = 'container_actions_events'
    __table_args__ = ()

    id = Column(Integer, primary_key=True, nullable=False)
    event = Column(String(255))
    action_id = Column(Integer,
                       ForeignKey('container_actions.id', ondelete='CASCADE'),
                       nullable=False)
    start_time = Column(DateTime, default=timeutils.utcnow)
    finish_time = Column(DateTime)
    result = Column(String(255))
    traceback = Column(Text)
    details = Column(Text)
