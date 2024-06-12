# dialects/vertica/v_catalog.py
# Copyright (C) 2005-2024 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors

from .array import ARRAY
from .types import OID
from .types import REGCLASS
from ... import Column
from ... import func
from ... import MetaData
from ... import Table
from ...types import BigInteger
from ...types import Boolean
from ...types import CHAR
from ...types import Float
from ...types import Integer
from ...types import SmallInteger
from ...types import String
from ...types import Text
from ...types import TypeDecorator


# types
class NAME(TypeDecorator):
    impl = String(64, collation="C")
    cache_ok = True


class Vertica_NODE_TREE(TypeDecorator):
    impl = Text(collation="C")
    cache_ok = True


class INT2VECTOR(TypeDecorator):
    impl = ARRAY(SmallInteger)
    cache_ok = True


class OIDVECTOR(TypeDecorator):
    impl = ARRAY(OID)
    cache_ok = True


class _SpaceVector:
    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return value
            return [int(p) for p in value.split(" ")]

        return process


REGPROC = REGCLASS  # seems an alias

# functions
_v_cat = func.v_catalog
quote_ident = _v_cat.quote_ident
v_table_is_visible = _v_cat.v_table_is_visible
v_type_is_visible = _v_cat.v_type_is_visible
v_get_viewdef = _v_cat.v_get_viewdef
v_get_serial_sequence = _v_cat.v_get_serial_sequence
format_type = _v_cat.format_type
v_get_expr = _v_cat.v_get_expr
v_get_constraintdef = _v_cat.v_get_constraintdef
v_get_indexdef = _v_cat.v_get_indexdef

# constants
RELKINDS_TABLE_NO_FOREIGN = ("r", "p")
RELKINDS_TABLE = RELKINDS_TABLE_NO_FOREIGN + ("f",)
RELKINDS_VIEW = ("v",)
RELKINDS_MAT_VIEW = ("m",)
RELKINDS_ALL_TABLE_LIKE = RELKINDS_TABLE + RELKINDS_VIEW + RELKINDS_MAT_VIEW

# tables
v_catalog_meta = MetaData(schema="v_catalog")

v_schemata = Table(
    "v_schemata",
    v_catalog_meta,
    Column("schema_id", Integer),
    Column("schema_name", CHAR),
    Column("schema_owner_id", Integer),
    Column("schema_owner", CHAR),
    Column("system_schema_creator", CHAR),
    #Column("create_time", ),
    Column("is_system_schema", Boolean),
)


v_namespace = Table(
    "v_namespace",
    v_catalog_meta,
    Column("oid", OID),
    Column("nspname", NAME),
    Column("nspowner", OID),
)

v_class = Table(
    "v_class",
    v_catalog_meta,
    Column("oid", OID, info={"server_version": (9, 3)}),
    Column("relname", NAME),
    Column("relnamespace", OID),
    Column("reltype", OID),
    Column("reloftype", OID),
    Column("relowner", OID),
    Column("relam", OID),
    Column("relfilenode", OID),
    Column("reltablespace", OID),
    Column("relpages", Integer),
    Column("reltuples", Float),
    Column("relallvisible", Integer, info={"server_version": (9, 2)}),
    Column("reltoastrelid", OID),
    Column("relhasindex", Boolean),
    Column("relisshared", Boolean),
    Column("relpersistence", CHAR, info={"server_version": (9, 1)}),
    Column("relkind", CHAR),
    Column("relnatts", SmallInteger),
    Column("relchecks", SmallInteger),
    Column("relhasrules", Boolean),
    Column("relhastriggers", Boolean),
    Column("relhassubclass", Boolean),
    Column("relrowsecurity", Boolean),
    Column("relforcerowsecurity", Boolean, info={"server_version": (9, 5)}),
    Column("relispopulated", Boolean, info={"server_version": (9, 3)}),
    Column("relreplident", CHAR, info={"server_version": (9, 4)}),
    Column("relispartition", Boolean, info={"server_version": (10,)}),
    Column("relrewrite", OID, info={"server_version": (11,)}),
    Column("reloptions", ARRAY(Text)),
)

v_type = Table(
    "v_type",
    v_catalog_meta,
    Column("oid", OID, info={"server_version": (9, 3)}),
    Column("typname", NAME),
    Column("typnamespace", OID),
    Column("typowner", OID),
    Column("typlen", SmallInteger),
    Column("typbyval", Boolean),
    Column("typtype", CHAR),
    Column("typcategory", CHAR),
    Column("typispreferred", Boolean),
    Column("typisdefined", Boolean),
    Column("typdelim", CHAR),
    Column("typrelid", OID),
    Column("typelem", OID),
    Column("typarray", OID),
    Column("typinput", REGPROC),
    Column("typoutput", REGPROC),
    Column("typreceive", REGPROC),
    Column("typsend", REGPROC),
    Column("typmodin", REGPROC),
    Column("typmodout", REGPROC),
    Column("typanalyze", REGPROC),
    Column("typalign", CHAR),
    Column("typstorage", CHAR),
    Column("typnotnull", Boolean),
    Column("typbasetype", OID),
    Column("typtypmod", Integer),
    Column("typndims", Integer),
    Column("typcollation", OID, info={"server_version": (9, 1)}),
    Column("typdefault", Text),
)

v_index = Table(
    "v_index",
    v_catalog_meta,
    Column("indexrelid", OID),
    Column("indrelid", OID),
    Column("indnatts", SmallInteger),
    Column("indnkeyatts", SmallInteger, info={"server_version": (11,)}),
    Column("indisunique", Boolean),
    Column("indnullsnotdistinct", Boolean, info={"server_version": (15,)}),
    Column("indisprimary", Boolean),
    Column("indisexclusion", Boolean, info={"server_version": (9, 1)}),
    Column("indimmediate", Boolean),
    Column("indisclustered", Boolean),
    Column("indisvalid", Boolean),
    Column("indcheckxmin", Boolean),
    Column("indisready", Boolean),
    Column("indislive", Boolean, info={"server_version": (9, 3)}),  # 9.3
    Column("indisreplident", Boolean),
    Column("indkey", INT2VECTOR),
    Column("indcollation", OIDVECTOR, info={"server_version": (9, 1)}),  # 9.1
    Column("indclass", OIDVECTOR),
    Column("indoption", INT2VECTOR),
    Column("indexprs", Vertica_NODE_TREE),
    Column("indpred", Vertica_NODE_TREE),
)

v_attribute = Table(
    "v_attribute",
    v_catalog_meta,
    Column("attrelid", OID),
    Column("attname", NAME),
    Column("atttypid", OID),
    Column("attstattarget", Integer),
    Column("attlen", SmallInteger),
    Column("attnum", SmallInteger),
    Column("attndims", Integer),
    Column("attcacheoff", Integer),
    Column("atttypmod", Integer),
    Column("attbyval", Boolean),
    Column("attstorage", CHAR),
    Column("attalign", CHAR),
    Column("attnotnull", Boolean),
    Column("atthasdef", Boolean),
    Column("atthasmissing", Boolean, info={"server_version": (11,)}),
    Column("attidentity", CHAR, info={"server_version": (10,)}),
    Column("attgenerated", CHAR, info={"server_version": (12,)}),
    Column("attisdropped", Boolean),
    Column("attislocal", Boolean),
    Column("attinhcount", Integer),
    Column("attcollation", OID, info={"server_version": (9, 1)}),
)

v_constraint = Table(
    "v_constraint",
    v_catalog_meta,
    Column("oid", OID),  # 9.3
    Column("conname", NAME),
    Column("connamespace", OID),
    Column("contype", CHAR),
    Column("condeferrable", Boolean),
    Column("condeferred", Boolean),
    Column("convalidated", Boolean, info={"server_version": (9, 1)}),
    Column("conrelid", OID),
    Column("contypid", OID),
    Column("conindid", OID),
    Column("conparentid", OID, info={"server_version": (11,)}),
    Column("confrelid", OID),
    Column("confupdtype", CHAR),
    Column("confdeltype", CHAR),
    Column("confmatchtype", CHAR),
    Column("conislocal", Boolean),
    Column("coninhcount", Integer),
    Column("connoinherit", Boolean, info={"server_version": (9, 2)}),
    Column("conkey", ARRAY(SmallInteger)),
    Column("confkey", ARRAY(SmallInteger)),
)

v_sequence = Table(
    "v_sequence",
    v_catalog_meta,
    Column("seqrelid", OID),
    Column("seqtypid", OID),
    Column("seqstart", BigInteger),
    Column("seqincrement", BigInteger),
    Column("seqmax", BigInteger),
    Column("seqmin", BigInteger),
    Column("seqcache", BigInteger),
    Column("seqcycle", Boolean),
    info={"server_version": (10,)},
)

v_attrdef = Table(
    "v_attrdef",
    v_catalog_meta,
    Column("oid", OID, info={"server_version": (9, 3)}),
    Column("adrelid", OID),
    Column("adnum", SmallInteger),
    Column("adbin", Vertica_NODE_TREE),
)

v_description = Table(
    "v_description",
    v_catalog_meta,
    Column("objoid", OID),
    Column("classoid", OID),
    Column("objsubid", Integer),
    Column("description", Text(collation="C")),
)

v_enum = Table(
    "v_enum",
    v_catalog_meta,
    Column("oid", OID, info={"server_version": (9, 3)}),
    Column("enumtypid", OID),
    Column("enumsortorder", Float(), info={"server_version": (9, 1)}),
    Column("enumlabel", NAME),
)

v_am = Table(
    "v_am",
    v_catalog_meta,
    Column("oid", OID, info={"server_version": (9, 3)}),
    Column("amname", NAME),
    Column("amhandler", REGPROC, info={"server_version": (9, 6)}),
    Column("amtype", CHAR, info={"server_version": (9, 6)}),
)

v_collation = Table(
    "v_collation",
    v_catalog_meta,
    Column("oid", OID, info={"server_version": (9, 3)}),
    Column("collname", NAME),
    Column("collnamespace", OID),
    Column("collowner", OID),
    Column("collprovider", CHAR, info={"server_version": (10,)}),
    Column("collisdeterministic", Boolean, info={"server_version": (12,)}),
    Column("collencoding", Integer),
    Column("collcollate", Text),
    Column("collctype", Text),
    Column("colliculocale", Text),
    Column("collicurules", Text, info={"server_version": (16,)}),
    Column("collversion", Text, info={"server_version": (10,)}),
)
