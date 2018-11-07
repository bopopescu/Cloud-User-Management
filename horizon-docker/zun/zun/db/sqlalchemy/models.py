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
import six.moves.urllib.parse as urlparse
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Float
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import schema
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.types import TypeDecorator, TEXT
import datetime
import zun.conf


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


class Region(Base):
    """Represents health status of various region"""
    __tablename__ = 'region'
    __table_args__ = (
        schema.UniqueConstraint('name',
                                name="uniq_infra_region_idx"),
        table_args()
    )
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Country(Base):
    """Represents health status of various country"""
    __tablename__ = 'country'
    __table_args__ = (
        schema.UniqueConstraint('name',
                                name="uniq_infra_country_idx"),
        table_args()
    )
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Carriername(Base):
    """Represents health status of various carriers"""
    __tablename__ = 'carriername'
    __table_args__ = (
        schema.UniqueConstraint('name',
                                name="uniq_infra_carrier_name_idx"),
        table_args()
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

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
    uuid = Column(String(36), unique = True)

class Provideraccount(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'provideraccount'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    #user = relationship("user")
    provider_id = Column(Integer, ForeignKey("provider.id"), nullable=False)
    #provider = relationship("provider")
    access_key_id = Column(String(200))
    access_key_str = Column(String(200))
    uuid = Column(String(36), unique=True)

class Providervm(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'providervm'

    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime, nullable=True)
    provider_account_id = Column(Integer, ForeignKey("provideraccount.id"), nullable=False)
    #provider_account = relationship("provideraccount")
    vm_external_ipv4 = Column(String(20))
    vm_internal_ipv4 = Column(String(20))
    status = Column(Integer)
    uuid = Column(String(36), unique=True)

class Instance(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'instance'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    #user = relationship("user")
    instance_type_id = Column(Integer, ForeignKey("instancetype.id"), nullable=False)
    #instance_type = relationship("instancetype")
    provider_vm_id = Column(Integer, ForeignKey("providervm.id"), nullable=False)
    #provider_vm = relationship("providervm")
    current_status = Column(DateTime, nullable=True)
    current_status_time = Column(DateTime, nullable=True)
    create_time = Column(DateTime, nullable=True)
    uuid = Column(String(36), unique=True)

class Storagerate(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'storagerate'

    id = Column(Integer, primary_key=True)
    storage_size = Column(Integer)
    provider_region_id = Column(Integer, ForeignKey("providerregion.id"), nullable=False)
    #provider_region = relationship("providerregion")
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    storage_rate = Column(Float)
    enable_ind = Column(Integer)
    user_tier = Column(Integer)
    uuid = Column(String(36), unique=True)

class Provider(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'provider'

    id = Column(Integer, primary_key=True)
    provider = Column(String(200))
    uuid = Column(String(36), unique=True)

class Providerregion(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'providerregion'

    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("provider.id"), nullable=False)
    #provider = relationship("provider")
    region = Column(String(200))
    uuid = Column(String(36), unique=True)

class Instancetype(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'instancetype'

    id = Column(Integer, primary_key=True)
    memory_size = Column(Integer, nullable=False)
    no_of_cpu = Column(Integer, nullable=False)
    provider_region_id = Column(Integer, ForeignKey("providerregion.id"), nullable=False)
    #provider_region = relationship("providerregion")
    enable_ind = Column(Integer)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    uuid = Column(String(36), unique=True)

class Usage(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'usage'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    #user = relationship("user")
    instance_id = Column(Integer, ForeignKey("instance.id"), nullable=False)
    #instance = relationship("instance")
    compute_rate_id = Column(Integer, ForeignKey("computerate.id"), nullable=False)
    #compute_rate = relationship("computerate")
    storage_rate_id = Column(Integer, ForeignKey("storagerate.id"), nullable=False)
    #storage_rate = relationship("storagerate")
    start_time = Column(DateTime, nullable=True)
    stop_time = Column(DateTime, nullable=True)
    duration = Column(Integer)
    cost = Column(Float)
    uuid = Column(String(36), unique=True)

class Statement(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'statement'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    #user = relationship("user")
    previous_balance = Column(String(20))
    billing_begin_date = Column(DateTime, nullable=True)
    billing_end_date = Column(DateTime, nullable=True)
    billing_charge_amount = Column(Float)
    current_balance = Column(Float)
    uuid = Column(String(36), unique=True)

class Computerate(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'computerate'

    id = Column(Integer, primary_key=True)
    instance_type_id = Column(Integer, ForeignKey("instancetype.id"), nullable=False)
    #instance_type = relationship("instancetype")
    start_date = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    compute_rate = Column(Float)
    status = Column(Integer)
    user_tier = Column(Integer)
    uuid = Column(String(36), unique=True)

class Payment(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    statement_id = Column(Integer, ForeignKey("statement.id"), nullable=False)
    #statement = relationship("statement")
    amount = Column(Float)
    payment_date = Column(DateTime, nullable=True)
    payment_method_id = Column(Integer, ForeignKey("paymentmethod.id"), nullable=False)
    #payment_method = relationship("paymentmethod")
    status = Column(Integer)
    uuid = Column(String(36), unique=True)

class Paymentmethod(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'paymentmethod'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    #user = relationship("user")
    payment_method_type = Column(Integer)
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
    pp_email = Column(String(200))
    uuid = Column(String(36), unique=True)

class Carrier(Base):
    """Represents health status of various carrier access acount"""
    __tablename__ = 'carrier'
    __table_args__ = (
        schema.UniqueConstraint('name',
                                name="uniq_infra_carrier_account_name_idx"),
        schema.UniqueConstraint('uuid',
                                name="uniq_infra_carrier_account_uuid_idx"),
        table_args()
    )
    id = Column(Integer, primary_key=True)
    project_id = Column(String(255))
    user_id = Column(String(255))
    uuid = Column(String(36))
    host = Column(String(255))
    name = Column(String(255))
    carrier_name = Column(String(255))
    carrier_access_key_id = Column(String(255))
    carrier_access_key = Column(String(255))
    status = Column(String(20))
    status_reason = Column(Text, nullable=True)
    task_state = Column(String(20))
#    created_at = Column(DateTime, default=datetime.datetime.utcnow)
#    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class InfraServer(Base):
    """Represents health status of various servers"""
    __tablename__ = 'infraserver'
    __table_args__ = (
        schema.UniqueConstraint('server_publicip', 'server_privateip', 
                                name="uniq_infra_server_idx"),
        table_args()
    )
    id = Column(Integer, primary_key=True)
    server_privateip = Column(String(255))
    server_publicip = Column(String(255))
    carrier_account_id = Column(String(255))
    region_id = Column(String(255))
    country_id = Column(String(255))
    status = Column(String(20))

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
    runtime = Column(String(20))


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
    server_privateip = Column(String(255))
    server_publicip = Column(String(255))
    carrier_account_id = Column(String(255))
    region_id = Column(String(255))
    country_id = Column(String(255))
    status = Column(String(20))

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
    restart_policy = Column(JSONEncodedDict)
    project_id = Column(String(255))
    user_id = Column(String(255))

    status = Column(String(20))
    status_reason = Column(Text, nullable=True)
    meta_labels = Column(JSONEncodedList)
    meta_name = Column(String(255))
    spec = Column(JSONEncodedDict)
    containers_uuids = Column(JSONEncodedList)
    cpu = Column(Float)
    memory = Column(String(255))
