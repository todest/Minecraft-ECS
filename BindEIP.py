import json
import os
import platform

from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_tea_openapi import models as open_api_models

import QueryECS
from AliYunConfig import ReadConf


class BindEIP:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
    ) -> Ecs20140526Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
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
    def main(instance_id):
        myconf = ReadConf()
        client = BindEIP.create_client(myconf.get_ak(), myconf.get_sk())
        associate_eip_address_request = ecs_20140526_models.AssociateEipAddressRequest(
            allocation_id=myconf.get_eid(),
            instance_id=instance_id
        )
        # 复制代码运行请自行打印 API 的返回值
        return client.associate_eip_address(associate_eip_address_request)


if __name__ == '__main__':
    print(json.dumps(BindEIP.main(QueryECS.GetOneECS.get_instance_id()).to_map(), indent=4))
    os.system('ssh-keygen -R mc.todest.cn')
    os.system('ssh -o StrictHostKeyChecking=no root@mc.todest.cn :')
    if platform.platform().startswith('Windows'):
        os.system('pause')
