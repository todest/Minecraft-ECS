import ctypes
import json
import os
import platform
import sys

from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_tea_openapi import models as open_api_models
from cffi.backend_ctypes import unicode

from AliYunConfig import ReadConf
from QueryECS import GetOneECS
from QueryShell import QueryShell


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(e)
        return False


class RunOnECS:
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
    def main(shell="""bash .init.sh"""):
        myconf = ReadConf()
        client = RunOnECS.create_client(myconf.get_ak(), myconf.get_sk())
        run_command_request = ecs_20140526_models.RunCommandRequest(
            region_id=myconf.get_region_id(),
            instance_id=[GetOneECS().get_instance_id()],
            type='RunShellScript',
            command_content=shell,
            working_dir='/root',
            timeout=8
        )
        # 复制代码运行请自行打印 API 的返回值
        return client.run_command(run_command_request)


if __name__ == '__main__':
    if platform.platform().startswith('Windows') and is_admin():
        print('正在等待NAS挂载...')
        while True:
            output = RunOnECS.main("""cat .init.sh""").to_map()
            command_id = output['body']['CommandId']
            status = QueryShell().main(command_id=command_id). \
                to_map()['body']['Invocation']['InvocationResults']['InvocationResult'][0]['InvocationStatus']
            if status == 'Success':
                break
        output = RunOnECS.main().to_map()
        print('命令已下发！')
        print(json.dumps(output, indent=4))
        command_id = output['body']['CommandId']
        output = QueryShell().main(command_id=command_id).to_map()[
            'body']['Invocation']['InvocationResults']['InvocationResult'][0]
        print('命令执行完毕！')
        print(json.dumps(output, indent=4))
        # os.system('pause')
        # out = os.popen("nslookup mc.todest.cn")
        # bef_ip = out.readlines()[-2].strip()[10:]
        # now_ip = bef_ip
        # while now_ip == bef_ip:
        #     os.popen("ipconfig /flushdns")
        #     time.sleep(1)
        #     now_ip = os.popen("nslookup mc.todest.cn").readlines()[-2].strip()[10:]
        #     os.system('cls')
        #     print('当前IP: %s' % now_ip)
        os.system('ssh-keygen -R mc.todest.cn')
        if platform.platform().startswith('Windows'):
            os.system("pause")
    else:
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)
