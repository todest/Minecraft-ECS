import configparser


class ReadConf:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("conf/config.ini", encoding="utf-8")

    def get_ak(self):
        return self.config.get('auth', 'AccessKeyId')

    def get_sk(self):
        return self.config.get('auth', 'AccessKeySecret')

    def get_region_id(self):
        return self.config.get('id', 'RegionID')

    def get_record_id(self):
        return self.config.get('id', 'RecordId')

    def get_eid(self):
        return self.config.get('id', 'EIP')


if __name__ == '__main__':
    print(ReadConf().get_ak())
