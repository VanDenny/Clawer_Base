import datetime


class Key_Changer:
    change_num = 0
    key_warehouse = {u'高德': ['70de561d24ed370ab68d0434d834d106',
                             '4a8f97b5b29c20bc21e8d58e0122281b',
                             'ceb9aaa9e1692f3ca497b58163e12de7',
                             'd93d6632b7d90134a2d4e949ca69bc1f',
                             '70d06b71c196d7c3e71ed084b6beb014',
                             '95eba7f5e12828d5699e3d19d95659be',
                             'ed15337b525ec9097b1fd35d476b992d',
                             '159e5e70247db21e0884e9fc2cc48a83'],
                     u'谷歌': ["AIzaSyAqNRDfTrCWqlRiHSs2bpRaR0P85mbhAx0",
                             "AIzaSyBlKDxO7QP8tEZna9vxAPImSoSpf34Q-b8"],
                     u'谷歌逆地址':['AIzaSyDum6Yxm-_V-L94lub8aokJdzYR7CbL1kU'],
                     u'百度': []
                    }
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    def __init__(self,key_name):
        self.key_list = self.key_warehouse[key_name]
        self.key_dict = {'key': self.key_list[self.change_num]}

    def process(self):
        date_now = datetime.datetime.now().strftime('%Y-%m-%d')
        if date_now != self.date:
            Key_Changer.change_num = 0
            Key_Changer.date = date_now
        elif self.change_num < (len(self.key_list)-1):
            Key_Changer.change_num += 1
        else:
            Key_Changer.change_num = 0
            print("Key is used up")
        self.key_dict['key'] = self.key_list[self.change_num]
        print("========已更换Key=========")
        return self.key_dict