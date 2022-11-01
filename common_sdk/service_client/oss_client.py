# -*- coding: utf-8 -*-

import oss2

from ..base_class.singleton import SingletonMetaThreadSafe as SingletonMetaclass
from ..system import sys_env

OSS_ACCESS_KEY_ENV_NAME = 'ALIYUN_OSS_ACCESS_KEY'
ALIYUN_OSS_ACCESS_KEY_SECRET_ENV_NAME = 'ALIYUN_OSS_ACCESS_KEY_SECRET'
ALIYUN_OSS_ACCESS_DOMAIN_ENV_NAME = 'ALIYUN_OSS_ACCESS_DOMAIN'
ALIYUN_OSS_UPLOAD_URL_ENV_NAME = 'ALIYUN_OSS_UPLOAD_URL'
ALIYUN_OSS_BUCKET_ENV_NAME = 'ALIYUN_OSS_BUCKET'


class AliyunOssClient(metaclass=SingletonMetaclass):

    def __init__(self, access_key=None, access_key_secret=None, access_domain=None, 
                    upload_url=None, bucket_name=None):
        self.access_key = access_key
        if access_key is None:
            self.access_key = sys_env.get_env(OSS_ACCESS_KEY_ENV_NAME)
        self.access_key_secret = access_key_secret
        if access_key_secret is None:
            self.access_key_secret = sys_env.get_env(ALIYUN_OSS_ACCESS_KEY_SECRET_ENV_NAME)
        self.access_domain = access_domain
        if access_domain is None:
            self.access_domain = sys_env.get_env(ALIYUN_OSS_ACCESS_DOMAIN_ENV_NAME)
        self.upload_url = upload_url
        if upload_url is None:
            self.upload_url = sys_env.get_env(ALIYUN_OSS_UPLOAD_URL_ENV_NAME)
        self.bucket_name = bucket_name
        if bucket_name is None:
            self.bucket_name = sys_env.get_env(ALIYUN_OSS_BUCKET_ENV_NAME)

        auth = oss2.Auth(self.access_key, self.access_key_secret)
        self.service = oss2.Service(auth, self.upload_url)
        self.bucket = oss2.Bucket(auth, self.upload_url, self.bucket_name)
    
    def list_buckets(self):
        buckets = oss2.BucketIterator(self.service)
        return [bucket.name for bucket in buckets]
    
    def upload_file(self, filename, file_obj):
        result = self.bucket.put_object(filename, file_obj.read())
        return '{}/{}'.format(self.access_domain, filename)
    
    def download_file(self):
        pass


oss_client = AliyunOssClient()