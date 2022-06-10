import json
import os
import platform
import time
import traceback

from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest

from AliYunConfig import ReadConf

RUNNING_STATUS = 'Running'
CHECK_INTERVAL = 3
CHECK_TIMEOUT = 180


class AliyunRunInstancesExample(object):

    def __init__(self):
        myconf = ReadConf()
        self.access_id = myconf.get_ak()
        self.access_secret = myconf.get_sk()

        # 是否只预检此次请求。true：发送检查请求，不会创建实例，也不会产生费用；false：发送正常请求，通过检查后直接创建实例，并直接产生费用
        self.dry_run = False
        # 实例所属的地域ID
        self.region_id = 'cn-shenzhen'
        # 实例的资源规格
        self.instance_type = 'ecs.hfg7.large'
        # 实例的计费方式
        self.instance_charge_type = 'PostPaid'
        # 镜像ID
        self.image_id = 'centos_7_9_x64_20G_alibase_20220426.vhd'
        # 指定新创建实例所属于的安全组ID
        self.security_group_id = 'sg-wz9hz64mlta3qngv2y86'
        # ecs.api.generator.run_instances_resourceGroupId
        self.resource_group_id = 'rg-acfmziigt5epioa'
        # 购买资源的时长
        self.period = 1
        # 购买资源的时长单位
        self.period_unit = 'Hourly'
        # 实例所属的可用区编号
        self.zone_id = 'cn-shenzhen-f'
        # 网络计费类型
        self.internet_charge_type = 'PayByTraffic'
        # 虚拟交换机ID
        self.vswitch_id = 'vsw-wz9a513gxw037cbkzhkv4'
        # 实例名称
        self.instance_name = 'minecraft'
        # 实例的描述
        self.description = 'Minecraft专用服务器'
        # 指定创建ECS实例的数量
        self.amount = 1
        # 公网出带宽最大值
        self.internet_max_bandwidth_out = 100
        # 云服务器的主机名
        self.host_name = 'minecraft'
        # 是否为I/O优化实例
        self.io_optimized = 'optimized'
        # 实例自定义数据
        self.user_data = 'IyEvYmluL2Jhc2gKCiMgQ29weXJpZ2h0IDIwMjAtMjAyMSBBbGliYWJhIEdyb3VwIEhvbGRpbmcgTGltaXRlZAoKIyBUaGlzIHByb2dyYW0gaXMgZnJlZSBzb2Z0d2FyZTogeW91IGNhbiByZWRpc3RyaWJ1dGUgaXQgYW5kL29yIG1vZGlmeQojIGl0IHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgR05VIEdlbmVyYWwgUHVibGljIExpY2Vuc2UgYXMgcHVibGlzaGVkIGJ5CiMgdGhlIEZyZWUgU29mdHdhcmUgRm91bmRhdGlvbiwgZWl0aGVyIHZlcnNpb24gMyBvZiB0aGUgTGljZW5zZSwgb3IKIyAoYXQgeW91ciBvcHRpb24pIGFueSBsYXRlciB2ZXJzaW9uLgoKIyBUaGlzIHByb2dyYW0gaXMgZGlzdHJpYnV0ZWQgaW4gdGhlIGhvcGUgdGhhdCBpdCB3aWxsIGJlIHVzZWZ1bCwKIyBidXQgV0lUSE9VVCBBTlkgV0FSUkFOVFk7IHdpdGhvdXQgZXZlbiB0aGUgaW1wbGllZCB3YXJyYW50eSBvZgojIE1FUkNIQU5UQUJJTElUWSBvciBGSVRORVNTIEZPUiBBIFBBUlRJQ1VMQVIgUFVSUE9TRS4gIFNlZSB0aGUKIyBHTlUgR2VuZXJhbCBQdWJsaWMgTGljZW5zZSBmb3IgbW9yZSBkZXRhaWxzLgoKIyBZb3Ugc2hvdWxkIGhhdmUgcmVjZWl2ZWQgYSBjb3B5IG9mIHRoZSBHTlUgR2VuZXJhbCBQdWJsaWMgTGljZW5zZQojIGFsb25nIHdpdGggdGhpcyBwcm9ncmFtLiAgSWYgbm90LCBzZWUgPGh0dHBzOi8vd3d3LmdudS5vcmcvbGljZW5zZXMvPi4KCm1vdW50X3RhcmdldHM9KAogICAgMmI4Mzc0OGJjNi1pamM4NS5jbi1zaGVuemhlbi5uYXMuYWxpeXVuY3MuY29tCikKbW91bnRfcG9pbnRzPSgKICAgIC9yb290CikKdXNlX3YzPSgKICAgIDEKKQoKc3VjY2Vzc19pbnN0YWxsX2NsaWVudD0wCgp0eXBlIHl1bQppZiBbICQ/IC1lcSAwIC1hICRzdWNjZXNzX2luc3RhbGxfY2xpZW50IC1lcSAwIF07IHRoZW4KICAgIHl1bSBpbnN0YWxsIC15IG5mcy11dGlscwogICAgaWYgWyAkPyAtZXEgMCBdOyB0aGVuCiAgICAgICAgc3VjY2Vzc19pbnN0YWxsX2NsaWVudD0xCiAgICBmaQpmaQoKdHlwZSBhcHQtZ2V0CmlmIFsgJD8gLWVxIDAgLWEgJHN1Y2Nlc3NfaW5zdGFsbF9jbGllbnQgLWVxIDAgXTsgdGhlbgogICAgYXB0LWdldCBpbnN0YWxsIC15IG5mcy1jb21tb24KICAgIGlmIFsgJD8gLWVxIDAgXTsgdGhlbgogICAgICAgIHN1Y2Nlc3NfaW5zdGFsbF9jbGllbnQ9MQogICAgZWxzZQogICAgICAgIGFwdC1nZXQgdXBkYXRlCiAgICAgICAgYXB0LWdldCBpbnN0YWxsIC15IG5mcy1jb21tb24KICAgICAgICBpZiBbICQ/IC1lcSAwIF07IHRoZW4KICAgICAgICAgICAgc3VjY2Vzc19pbnN0YWxsX2NsaWVudD0xCiAgICAgICAgZmkKICAgIGZpCmZpCgp0eXBlIHp5cHBlcgppZiBbICQ/IC1lcSAwIC1hICRzdWNjZXNzX2luc3RhbGxfY2xpZW50IC1lcSAwIF07IHRoZW4KICAgIHp5cHBlciBpbnN0YWxsIC15IG5mcy1jbGllbnQKICAgIGlmIFsgJD8gLWVxIDAgXTsgdGhlbgogICAgICAgIHN1Y2Nlc3NfaW5zdGFsbF9jbGllbnQ9MQogICAgZWxzZQogICAgICAgIHp5cHBlciByZWZyZXNoCiAgICAgICAgenlwcGVyIGluc3RhbGwgLXkgbmZzLWNsaWVudAogICAgICAgIGlmIFsgJD8gLWVxIDAgXTsgdGhlbgogICAgICAgICAgICBzdWNjZXNzX2luc3RhbGxfY2xpZW50PTEKICAgICAgICBmaQogICAgZmkKZmkKCmlmIFsgJHN1Y2Nlc3NfaW5zdGFsbF9jbGllbnQgLW5lIDEgXTsgdGhlbgogICAgZXhpdCAwCmZpCgppZiAobHNtb2QgfCBncmVwIHN1bnJwYyA+IC9kZXYvbnVsbCk7IHRoZW4KICAgIGlmIChtb2RpbmZvIHN1bnJwYyB8IGdyZXAgdGNwX21heF9zbG90X3RhYmxlX2VudHJpZXMgPiAvZGV2L251bGwpOyB0aGVuCiAgICAgICAgc3lzY3RsIC13IHN1bnJwYy50Y3BfbWF4X3Nsb3RfdGFibGVfZW50cmllcz0xMjgKICAgIGZpCiAgICBpZiAobW9kaW5mbyBzdW5ycGMgfCBncmVwIHRjcF9zbG90X3RhYmxlX2VudHJpZXMgPiAvZGV2L251bGwpOyB0aGVuCiAgICAgICAgc3lzY3RsIC13IHN1bnJwYy50Y3Bfc2xvdF90YWJsZV9lbnRyaWVzPTEyOAogICAgZmkKZmkKCmlmIChtb2RpbmZvIG5mcyB8IGdyZXAgbmZzNF91bmlxdWVfaWQgPiAvZGV2L251bGwpOyB0aGVuCiAgICBwcmludGYgJ2luc3RhbGwgbmZzIC9zYmluL21vZHByb2JlIC0taWdub3JlLWluc3RhbGwgbmZzIG5mczRfdW5pcXVlX2lkPSQoY2F0IC9zeXMvY2xhc3MvZG1pL2lkL3Byb2R1Y3RfdXVpZClcbicgPiAvZXRjL21vZHByb2JlLmQvYWxpbmFzLmNvbmYKZmkKKG1vZGluZm8gc3VucnBjIHwgZ3JlcCB0Y3BfbWF4X3Nsb3RfdGFibGVfZW50cmllcyA+IC9kZXYvbnVsbCkgJiYgZWNobyAib3B0aW9ucyBzdW5ycGMgdGNwX21heF9zbG90X3RhYmxlX2VudHJpZXM9MTI4IiA+PiAvZXRjL21vZHByb2JlLmQvYWxpbmFzLmNvbmYKKG1vZGluZm8gc3VucnBjIHwgZ3JlcCB0Y3Bfc2xvdF90YWJsZV9lbnRyaWVzID4gL2Rldi9udWxsKSAmJiBlY2hvICJvcHRpb25zIHN1bnJwYyB0Y3Bfc2xvdF90YWJsZV9lbnRyaWVzPTEyOCIgPj4gL2V0Yy9tb2Rwcm9iZS5kL2FsaW5hcy5jb25mCgppZiBbICEgLWYgL2V0Yy9yYy5sb2NhbCBdOyB0aGVuCiAgICBlY2hvICcjIS9iaW4vYmFzaCcgPiAvZXRjL3JjLmxvY2FsCmZpCmVjaG8gIm1vdW50IC1hIC10IG5mcyIgPj4gL2V0Yy9yYy5sb2NhbApjaG1vZCAreCAvZXRjL3JjLmxvY2FsCgpmb3IgaSBpbiAiJHshbW91bnRfdGFyZ2V0c1tAXX0iOyBkbwogICAgbW91bnRfdGFyZ2V0PSR7bW91bnRfdGFyZ2V0c1skaV19CiAgICBbIC16ICRtb3VudF90YXJnZXQgXSAmJiBjb250aW51ZQogICAgbW91bnRfcG9pbnQ9JHttb3VudF9wb2ludHNbJGldfQogICAgWyAteiAkbW91bnRfcG9pbnQgXSAmJiBjb250aW51ZQogICAgdjM9JHt1c2VfdjNbJGldfQogICAgWyAteiAkdjMgXSAmJiBjb250aW51ZQoKICAgIG1rZGlyIC1wICIke21vdW50X3BvaW50fSIgfHwgY29udGludWUKCiAgICBhdXRvbW91bnRfcGFyYW09IiIKICAgIGlmIFsgLWYgL2V0Yy9vcy1yZWxlYXNlIF07IHRoZW4KICAgICAgICBvc19uYW1lPWBhd2sgLUY9ICcvXk5BTUUve3ByaW50ICQyfScgL2V0Yy9vcy1yZWxlYXNlYAogICAgICAgIGlmIFtbICR7b3NfbmFtZX0gPT0gIlwiVWJ1bnR1XCIiIF1dOyB0aGVuCiAgICAgICAgICAgIGlmIChtYW4gc3lzdGVtZC1mc3RhYi1nZW5lcmF0b3IgPiAvZGV2L251bGwpOyB0aGVuCiAgICAgICAgICAgICAgICBhdXRvbW91bnRfcGFyYW09Iix4LXN5c3RlbWQuYXV0b21vdW50IgogICAgICAgICAgICBmaQogICAgICAgIGVsaWYgW1sgJHtvc19uYW1lfSA9PSAiXCJBbGl5dW4gTGludXhcIiIgXV07IHRoZW4KICAgICAgICAgICAgaWYgKG1hbiBzeXN0ZW1kLWZzdGFiLWdlbmVyYXRvciA+IC9kZXYvbnVsbCk7IHRoZW4KICAgICAgICAgICAgICAgIGF1dG9tb3VudF9wYXJhbT0iLHgtc3lzdGVtZC5hdXRvbW91bnQseC1zeXN0ZW1kLnJlcXVpcmVzPXN5c3RlbWQtcmVzb2x2ZWQuc2VydmljZSx4LXN5c3RlbWQuYWZ0ZXI9c3lzdGVtZC1yZXNvbHZlZC5zZXJ2aWNlIgogICAgICAgICAgICBmaQogICAgICAgIGZpCiAgICBmaQoKICAgIGlmIFtbICRtb3VudF90YXJnZXQgPT0gKi5leHRyZW1lLm5hcy5hbGl5dW5jcy5jb20gXV07IHRoZW4KICAgICAgICBpZiBbIC1mIC9ldGMvc3lzdGVtZC9zeXN0ZW0vc29ja2V0cy50YXJnZXQud2FudHMvcnBjYmluZC5zb2NrZXQgXTsgdGhlbgogICAgICAgICAgICBzZWQgLWkgJ3MvQmluZElQdjZPbmx5PWlwdjYtb25seS8jQmluZElQdjZPbmx5PWlwdjYtb25seS9nJyAvZXRjL3N5c3RlbWQvc3lzdGVtL3NvY2tldHMudGFyZ2V0LndhbnRzL3JwY2JpbmQuc29ja2V0CiAgICAgICAgICAgIHNlZCAtaSAncy9MaXN0ZW5TdHJlYW09XFs6OlxdOjExMS8jTGlzdGVuU3RyZWFtPVxbOjpcXToxMTEvZycgL2V0Yy9zeXN0ZW1kL3N5c3RlbS9zb2NrZXRzLnRhcmdldC53YW50cy9ycGNiaW5kLnNvY2tldAogICAgICAgICAgICBzZWQgLWkgJ3MvTGlzdGVuRGF0YWdyYW09XFs6OlxdOjExMS8jTGlzdGVuRGF0YWdyYW09XFs6OlxdOjExMS9nJyAvZXRjL3N5c3RlbWQvc3lzdGVtL3NvY2tldHMudGFyZ2V0LndhbnRzL3JwY2JpbmQuc29ja2V0CiAgICAgICAgZmkKICAgICAgICBlY2hvICIke21vdW50X3RhcmdldH06L3NoYXJlICR7bW91bnRfcG9pbnR9IG5mcyB2ZXJzPTMsbm9sb2NrLG5vYWNsLHByb3RvPXRjcCxub3Jlc3Zwb3J0LF9uZXRkZXYke2F1dG9tb3VudF9wYXJhbX0gMCAwIiA+PiAvZXRjL2ZzdGFiCiAgICBlbGlmIFtbICRtb3VudF90YXJnZXQgPT0gKi5uYXMuYWxpeXVuY3MuY29tIF1dOyB0aGVuCiAgICAgICAgaWYgWyAkdjMgLWVxIDEgXTsgdGhlbgogICAgICAgICAgICBlY2hvICIke21vdW50X3RhcmdldH06LyAke21vdW50X3BvaW50fSBuZnMgdmVycz0zLG5vbG9jayxwcm90bz10Y3AscnNpemU9MTA0ODU3Nix3c2l6ZT0xMDQ4NTc2LGhhcmQsdGltZW89NjAwLHJldHJhbnM9MixfbmV0ZGV2LG5vcmVzdnBvcnQke2F1dG9tb3VudF9wYXJhbX0gMCAwIiA+PiAvZXRjL2ZzdGFiCiAgICAgICAgZWxzZQogICAgICAgICAgICBlY2hvICIke21vdW50X3RhcmdldH06LyAke21vdW50X3BvaW50fSBuZnMgdmVycz00LG1pbm9ydmVyc2lvbj0wLHJzaXplPTEwNDg1NzYsd3NpemU9MTA0ODU3NixoYXJkLHRpbWVvPTYwMCxyZXRyYW5zPTIsX25ldGRldixub3Jlc3Zwb3J0JHthdXRvbW91bnRfcGFyYW19IDAgMCIgPj4gL2V0Yy9mc3RhYgogICAgICAgIGZpCiAgICBmaQoKICAgIG1vdW50IC1hIC10IG5mcwpkb25lCgo='
        # 密钥对名称
        self.key_pair_name = 'SSH'
        # 后付费实例的抢占策略
        self.spot_strategy = 'SpotAsPriceGo'
        # 是否开启安全加固
        self.security_enhancement_strategy = 'Active'
        # 系统盘大小
        self.system_disk_size = '20'
        # 系统盘的磁盘种类
        self.system_disk_category = 'cloud_essd'
        # 性能级别
        self.system_disk_performance_level = 'PL1'
        # 实例、安全组、磁盘和主网卡的标签
        self.tags = [
            {
                'Key': 'app',
                'Value': 'minecraft'
            }
        ]

        self.client = AcsClient(self.access_id, self.access_secret, self.region_id)

    def run(self):
        try:
            ids = self.run_instances()
            self._check_instances_status(ids)
        except ClientException as e:
            print('Fail. Something with your connection with Aliyun go incorrect.'
                  ' Code: {code}, Message: {msg}'
                  .format(code=e.error_code, msg=e.message))
        except ServerException as e:
            print('Fail. Business error.'
                  ' Code: {code}, Message: {msg}'
                  .format(code=e.error_code, msg=e.message))
        except Exception:
            print('Unhandled error')
            print(traceback.format_exc())

    def run_instances(self):
        """
        调用创建实例的API，得到实例ID后继续查询实例状态
        :return:instance_ids 需要检查的实例ID
        """
        request = RunInstancesRequest()

        request.set_DryRun(self.dry_run)

        request.set_InstanceType(self.instance_type)
        request.set_InstanceChargeType(self.instance_charge_type)
        request.set_ImageId(self.image_id)
        request.set_SecurityGroupId(self.security_group_id)
        request.set_ResourceGroupId(self.resource_group_id)
        request.set_Period(self.period)
        request.set_PeriodUnit(self.period_unit)
        request.set_ZoneId(self.zone_id)
        # request.set_InternetChargeType(self.internet_charge_type)
        request.set_VSwitchId(self.vswitch_id)
        request.set_InstanceName(self.instance_name)
        request.set_Description(self.description)
        request.set_Amount(self.amount)
        # request.set_InternetMaxBandwidthOut(self.internet_max_bandwidth_out)
        request.set_HostName(self.host_name)
        request.set_IoOptimized(self.io_optimized)
        request.set_UserData(self.user_data)
        request.set_KeyPairName(self.key_pair_name)
        request.set_SpotStrategy(self.spot_strategy)
        request.set_SecurityEnhancementStrategy(self.security_enhancement_strategy)
        request.set_SystemDiskSize(self.system_disk_size)
        request.set_SystemDiskCategory(self.system_disk_category)
        request.set_SystemDiskPerformanceLevel(self.system_disk_performance_level)
        request.set_Tags(self.tags)

        body = self.client.do_action_with_exception(request)
        data = json.loads(body)
        instance_ids = data['InstanceIdSets']['InstanceIdSet']
        print('Success. Instance creation succeed. InstanceIds: {}'.format(', '.join(instance_ids)))
        return instance_ids

    def _check_instances_status(self, instance_ids):
        """
        每3秒中检查一次实例的状态，超时时间设为3分钟。
        :param instance_ids 需要检查的实例ID
        :return:
        """
        start = time.time()
        while True:
            request = DescribeInstancesRequest()
            request.set_InstanceIds(json.dumps(instance_ids))
            body = self.client.do_action_with_exception(request)
            data = json.loads(body)
            for instance in data['Instances']['Instance']:
                if RUNNING_STATUS in instance['Status']:
                    instance_ids.remove(instance['InstanceId'])
                    print('Instance boot successfully: {}'.format(instance['InstanceId']))

            if not instance_ids:
                print('Instances all boot successfully')
                break

            if time.time() - start > CHECK_TIMEOUT:
                print('Instances boot failed within {timeout}s: {ids}'
                      .format(timeout=CHECK_TIMEOUT, ids=', '.join(instance_ids)))
                break

            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    AliyunRunInstancesExample().run()
    if platform.platform().startswith('Windows'):
        os.system("pause")
