import datetime
import random

class Key_Manager:
    change_num = 0
    key_warehouse = {u'高德': ['70de561d24ed370ab68d0434d834d106',
                             '4a8f97b5b29c20bc21e8d58e0122281b',
                             'ceb9aaa9e1692f3ca497b58163e12de7',
                             'd93d6632b7d90134a2d4e949ca69bc1f',
                             '70d06b71c196d7c3e71ed084b6beb014',
                             '95eba7f5e12828d5699e3d19d95659be',
                             'ed15337b525ec9097b1fd35d476b992d',
                             '159e5e70247db21e0884e9fc2cc48a83',
                             '5f97e7fefd2c32d3d888fcc6cfd9f4e4',
                             '8356ea2ff30106feea5eed43b0bbfc06',
                             'c734e835c4b33e6f9ee4e883bd09bfa7',
                             'e35123ff3db6407a8fcf5e3fc66cc8b1'],
                     u"腾讯": [
                         'KKABZ-AMA6Q-3PG5Y-GKAU6-YCSQZ-LLFM7',
                         '2ULBZ-6S5CV-4USPR-ULKBZ-3S3G6-XDFTT',
                         'K7CBZ-JIQC5-ESCIJ-QJOOZ-KID4K-2HF5G',
                         '2ULBZ-6S5CV-4USPR-ULKBZ-3S3G6-XDFTT',
                         'V4BBZ-E7QWX-MFC4R-T4F62-V2JLS-Y7FL5',
                         'KJTBZ-H5IW5-WEUID-QPFBT-QRL4Z-2OFP6',
                         'SKXBZ-FDNKX-KK24G-TBWZW-M3NLT-Y2BI7'
                     ],
                     u'谷歌': ["AIzaSyAqNRDfTrCWqlRiHSs2bpRaR0P85mbhAx0",
                             "AIzaSyBlKDxO7QP8tEZna9vxAPImSoSpf34Q-b8"],
                     u'谷歌逆地址':['AIzaSyDum6Yxm-_V-L94lub8aokJdzYR7CbL1kU'],
                     u'百度': ['3ypIkrvkmwtLzFk8gsieaymv',
                             '33A1NuyBoL5nad86et0qYMHy',
                             'dH4jtQDXWDkGBEBUxOce4QmU',
                             '6LUKfQTvno6ieOgwVyEgV7Xi'
                             ]
                    }
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    def __init__(self, key_name):
        self.key_name = key_name
        self.key_list = self.key_warehouse[key_name]
        if key_name == u'百度':
            self.key_dict = {'ak': self.key_list[self.change_num]}
        else:
            self.key_dict = {'key': self.key_list[self.change_num]}

    def random_choice(self):
        """
        随机返回一个KEY
        :return: 根据不同API需要返回不同的格式的key字典
        """
        a_key = random.choice(self.key_list)
        if self.key_name == u'百度':
            key_dict = {'ak': a_key}
        else:
            key_dict = {'key': a_key}
        return key_dict

    def update(self):
        date_now = datetime.datetime.now().strftime('%Y-%m-%d')
        if date_now != self.date:
            Key_Manager.change_num = 0
            Key_Manager.date = date_now
        elif self.change_num < (len(self.key_list)-1):
            Key_Manager.change_num += 1
        else:
            Key_Manager.change_num = 0
            print("Key is used up")
        self.key_dict['key'] = self.key_list[self.change_num]
        print("========已更新Key %s =========" % self.key_dict['key'])
        return self.key_dict


if __name__ == "__main__":
    kc = Key_Manager("高德")
    print(kc.random_choice())