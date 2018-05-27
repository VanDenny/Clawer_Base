from Clawer_Base.user_agents import User_agents
from Clawer_Base.logger import logger
from Clawer_Base.proxy_clawers import Fetch_proxy
from Clawer_Base.key_changer import Key_Changer
from Clawer_Base.ioput import Res_saver
import requests
from requests.exceptions import ReadTimeout, ConnectionError
import datetime
import time
import os
import pandas as pd

class Clawer:
    """定义爬虫基类，普遍包含采集、解析、储存三个功能"""
    # cookie预存入类参，避免多次读入
    _cookies = ''
    # 请求统计
    req_info = {}
    def __init__(self, params):
        self.url = ''
        self.headers = User_agents().get_headers()
        self.params = params
        self.proxys = {'proxies': ''}
        self.cookies = self._cookies
        self.key_type = ''
        self.req_id = ''
        self.repeat_times = 0

    def requestor(self):
        """请求并处理超时请求"""
        try:
            self.req = requests.get(self.url, headers=self.headers,
                                    params=self.params, timeout=5,
                                    allow_redirects=False, cookies=self.cookies, **self.proxys)
            # print(self.req.url)
            if self.req_id == '':
                self.req_id = self.req.url
            status_code = self.req.status_code
            # print(status_code)
            self.req_stat(status_code)
            self.scheduler_by_statuscode(status_code)

        except (ReadTimeout, ConnectionError) as e:
            self.repeat_times += 1
            print('======%s_休息3秒=======' % e)
            time.sleep(3)
            # 避免错误代理带来的死循环，有代理先去代理试一下，没代理加代理
            if self.repeat_times >= 6:
                if self.proxys['proxies']:
                    self.proxys['proxies'] = ''
                else:
                    self.status_change_proxy()
            else:
                self.status_change_user_agent()

    def scheduler_by_statuscode(self, status_code):
        """根据网络状态码进行调度"""
        if status_code == 200:
            try:
                self.respond = self.req.json()
                if self.proxys['proxies']:
                    # 回收未用完的代理
                    Fetch_proxy.proxy_pool.append(self.proxys['proxies'])

            except:
                content = self.req.text
                while ",," in content:
                    content = content.replace(',,', ',"",')
                while "[," in content:
                    content = content.replace("[,", '["",')
                content = eval(content)
                if isinstance(content, list):
                    self.respond = content
                else:
                    logger.info(self.respond)
                    self.respond = None

        elif status_code in [301, 302, 429, 302, 502]:
            self.status_change_proxy()

        elif status_code in [400, 401, 402, 403, 404]:
            logger.info('%s_%s 没有信息' % (self.req_url, status_code))
            self.respond = None

        elif status_code in [202, 204]:
            print(status_code)
            time.sleep(2)
            self.status_change_user_agent()

        elif status_code in [500]:
            print(status_code)
            self.status_change_user_agent()

        else:
            print(status_code)
            self.status_change_user_agent()

    def scheduler(self):
        """调度功能,根据api不同需要自定义"""
        pass

    def status_ok(self):
        """请求成功的处理步骤,根据api不同需要自定义self.respond的处理过程"""
        pass

    def status_pass(self):
        logger.info('已跳过 %s' % self.req_url)

    def status_invalid_request(self):
        logger.info('请求错误 %s' % self.req_url)

    def status_unknown_error(self):
        logger.info('未知错误 %s' % self.req_url)

    def status_change_key(self):
        logger.info('更换密钥 %s' % self.req_url)
        key_dict = Key_Changer(self.key_type).process()
        self.params.update_key(key_dict)
        self.requestor()

    def status_change_user_agent(self):
        self.headers = User_agents().get_headers()
        self.requestor()

    def status_change_proxy(self):
        if Fetch_proxy.proxy_pool:
            self.proxys['proxies'] = Fetch_proxy.proxy_pool.pop()
        else:
            Fetch_proxy.proxy_pool = Fetch_proxy().fetch_new_proxyes(15)
            self.proxys['proxies'] = Fetch_proxy.proxy_pool.pop()
        self.requestor()

    def cookie_init(self):
        cookies={}
        if os.path.exists('cookie.txt'):
            with open('cookie.txt', 'r') as f:
                for line in f.read().split(';'):
                    #其设置为1就会把字符串拆分成2份
                    name, value=line.strip().split('=', 1)
                    cookies[name]=value
            Clawer._cookies = cookies
        else:
            raise Exception('缺少cookie')

    def stat_init(self):
        """初始化类统计"""
        date_now = datetime.datetime.now().strftime("%Y%m%d")
        file_name = 'stat_%s.csv'% (date_now)
        req_info = {}
        if os.path.exists('Req_stat/%s/%s' % (date_now, file_name)):
            df = pd.read_csv('Req_stat/%s/%s' % (date_now, file_name))
            info_list = df.to_dict(orient='records')
            for info in info_list:
                req_info[info['id']] = info
            Clawer.req_info = req_info
        else:
            Clawer.req_info = req_info

    def req_stat(self, status_code):
        """统计重复访问次数,故障代码次数"""
        if self.req_id in self.req_info:
            if str(status_code) in self.req_info[self.req_id]:
                Clawer.req_info[self.req_id][str(status_code)] += 1
            else:
                Clawer.req_info[self.req_id][str(status_code)] = 1
        else:
            Clawer.req_info[self.req_id] = {'id': self.req_id, str(status_code): 1}

    def stat_save(self):
        info_list = list(self.req_info.values())
        res_saver = Res_saver(info_list, 'stat', floder_path='Req_stat')
        res_saver.save_as_file()

    def stat_controller(self):
        pass


    def parser(self):
        """解析有效信息功能，根据api不同需要自定义"""
        pass

    def process(self):
        """爬虫运行总过程，根据api不同需要自定义"""
        self.requestor()
        return self.scheduler()


    def __str__(self):
        """描述信息"""
        return Clawer.__name__