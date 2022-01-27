import json
import os
import platform

from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_tea_openapi import models as open_api_models

from AliYunConfig import ReadConf
from QueryECS import GetOneECS


class DeleteOneECS:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
    ) -> Ecs20140526Client:
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id=access_key_id,
            # 您的AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = 'ecs-cn-hangzhou.aliyuncs.com'
        return Ecs20140526Client(config)

    @staticmethod
    def main():
        myconf = ReadConf()
        client = DeleteOneECS.create_client(myconf.get_ak(), myconf.get_sk())
        delete_instance_request = ecs_20140526_models.DeleteInstanceRequest(
            instance_id=GetOneECS().get_instance_id(),
            force=True,
            terminate_subscription=True
        )
        # 复制代码运行请自行打印 API 的返回值
        return client.delete_instance(delete_instance_request)


if __name__ == '__main__':
    print(json.dumps(DeleteOneECS.main().to_map(), indent=4, ensure_ascii=False))
    if platform.platform().startswith('Windows'):
        os.system("pause")
