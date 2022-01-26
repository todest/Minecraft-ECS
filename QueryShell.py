import json
import time

from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_tea_openapi import models as open_api_models

from AliYunConfig import ReadConf


class QueryShell:
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
    def main(command_id=None):
        myconf = ReadConf()
        client = QueryShell.create_client(myconf.get_ak(), myconf.get_sk())
        describe_invocation_results_request = ecs_20140526_models.DescribeInvocationResultsRequest(
            region_id=myconf.get_region_id(),
            command_id=command_id
        )
        if command_id is not None:
            while True:
                output = client.describe_invocation_results(describe_invocation_results_request)
                status = output.to_map()['body']['Invocation']['InvocationResults'][
                    'InvocationResult'][0]['InvokeRecordStatus']
                if status == 'Finished':
                    return output
                time.sleep(1)
        # 复制代码运行请自行打印 API 的返回值
        return client.describe_invocation_results(describe_invocation_results_request)


if __name__ == '__main__':
    print(json.dumps(QueryShell.main().to_map(), indent=4))
