# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/spider_entity/fixed_rules_spider.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n,proto/spider_entity/fixed_rules_spider.proto\x1a\'spider_common/proto/spider/spider.proto\x1a.spider_common/proto/spider/parse_setting.proto\"\x8b\x02\n\x10\x46ixedRulesSpider\x12\n\n\x02id\x18\x01 \x01(\t\x12\x1e\n\x06spider\x18\x02 \x01(\x0b\x32\x0e.SpiderMessage\x12\x13\n\x0b\x63reate_time\x18\x03 \x01(\x05\x12\x13\n\x0b\x64\x65lete_time\x18\x04 \x01(\x05\x12\x38\n\x06status\x18\x05 \x01(\x0e\x32(.FixedRulesSpiderMessage.FixedRulesSpiderMessageStatus\x12\x33\n\x15parse_setting_message\x18\x06 \x01(\x0b\x32\x14.ParseSettingMessage\"2\n\x16\x46ixedRulesSpiderStatus\x12\x0b\n\x07\x43REATED\x10\x00\x12\x0b\n\x07\x44\x45LETED\x10\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.spider_entity.fixed_rules_spider_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _FixedRulesSpiderMessage._serialized_start=138
  _FixedRulesSpiderMessage._serialized_end=405
  _FixedRulesSpiderMessage_FixedRulesSpiderMessageSTATUS._serialized_start=355
  _FixedRulesSpiderMessage_FixedRulesSpiderMessageSTATUS._serialized_end=405
# @@protoc_insertion_point(module_scope)
