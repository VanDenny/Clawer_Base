from lxml import etree
import requests
import requests.exceptions as req_e
from Clawer_Base.logger import logger
import pandas as pd
import os



class Fetch_proxy:
    local_ip = ''
    proxy_pool = []
    def __init__(self):
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

    def cinit(self):
        Fetch_proxy.local_ip = self.get_ip()
        if os.path.exists('proxy.csv'):
            local_proxyes = self.read_proxy_file('proxy.csv')
            for proxy in local_proxyes:
                valid_res = self.proxy_vaild(proxy)
                if valid_res[0] and (valid_res[1] not in Fetch_proxy.proxy_pool):
                    Fetch_proxy.proxy_pool.append(valid_res[1])


    def get_ip(self):
        url = "http://ip.chinaz.com/getip.aspx"
        r = requests.get(url, allow_redirects=False)
        if r.status_code == 200:
            ip = r.text
            return ip
        else:
            raise Exception('无法获取当前ip')

    def proxy_vaild(self, proxy_dict):
        url = "http://ip.chinaz.com/getip.aspx"  #用来测试IP是否可用的url
        try:
            r = requests.get(url, proxies=proxy_dict, headers=self.headers, timeout=3, allow_redirects = False)
            if r.status_code == 200 and r.text != Fetch_proxy.local_ip:
                print(r.text)
                return (True, proxy_dict)
            else:
                logger.info('_______%s 无效代理________'%r.status_code)
                return (False, )
        except (req_e.ReadTimeout, req_e.ConnectTimeout, req_e.ProxyError,req_e.ConnectionError,req_e.ChunkedEncodingError):
            logger.info('_______连接超时 无效代理________')
            return (False, )


    def fetch_ip181(self, num):
        """抓取http://www.ip181.com/，10分钟更新100个，质量55%"""
        proxyes = []
        url = 'http://www.ip181.com/'
        req = requests.get(url, headers=self.headers)
        html = req.text
        selector = etree.HTML(html)
        tbody = selector.xpath('//tr')
        for line in tbody[1:]:
            tds = line.xpath('td/text()')
            ip = tds[0]
            port = tds[1]
            latency = tds[4].split(' ')[0]
            if float(latency) < 0.5:
                proxy = "%s:%s"%(ip, port)
                proxy_dict = {'http':proxy, 'https':proxy}
                valid_res = self.proxy_vaild(proxy_dict)
                if valid_res[0]:
                    proxyes.append(valid_res[1])
                if len(proxyes) >= num:
                    break
        logger.info('抓取 ip181，有效代理 %d 个'%(len(proxyes)))
        return proxyes

    def fetch_66ip(self, num):
        """抓取http://www.66ip.cn/，质量25%"""
        proxyes = []
        url = "http://www.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip"
        req = requests.get(url, headers=self.headers)
        html = req.text
        urls = html.split("</script>")[1].split("<br />")
        for u in urls[:-1]:
            if u.strip():
                proxy = u.strip()
                proxy_dict = {'http':proxy, 'https':proxy}
                valid_res = self.proxy_vaild(proxy_dict)
                if valid_res[0]:
                        proxyes.append(valid_res[1])
                if len(proxyes) >= num:
                    break
                else:
                    continue
        logger.info('抓取 66ip，有效代理 %d 个'%(len(proxyes)))
        return proxyes

    def fetch_xici(self, num):
        """抓取http://www.xicidaili.com/，质量10%"""
        page = 1
        proxyes = []
        while len(proxyes) <= num and page <= 2:
            url = "http://www.xicidaili.com/nn/%s" %page
            req = requests.get(url, headers=self.headers)
            html = req.text
            selector = etree.HTML(html)
            tbody = selector.xpath('//tr[@class]')
            for line in tbody:
                tds = line.xpath('td/text()')
                ip = tds[0]
                port = tds[1]
                speed = line.xpath('td[7]/div/@title')[0][:-1]
                latency = line.xpath('td[8]/div/@title')[0][:-1]
    #             print('%s,%s,%s,%s'%(ip, port, speed, latency))
                if float(speed) < 3 and float(latency) < 1:
                    proxy = "%s:%s"%(ip, port)
                    proxy_dict = {'http':proxy, 'https':proxy}
                    valid_res = self.proxy_vaild(proxy_dict)
                    if valid_res[0]:
                        proxyes.append(valid_res[1])
            logger.info('抓取 xicidaili 第 %d 页，有效代理 %d 个'%(page, len(proxyes)))
            page += 1
        return proxyes

    def fetch_kxdaili(self, num):
        """抓取http://www.kxdaili.com/，质量 5%"""
        page = 1
        proxyes = []
        while len(proxyes) <= num and page <= 10:
            url = "http://www.kxdaili.com/dailiip/1/%d.html" % page
            req = requests.get(url,headers=self.headers)
            html = req.text
            selector = etree.HTML(html)
            tbody = selector.xpath('//tr')
            for line in tbody:
                tds = line.xpath('td/text()')
                ip = tds[0]
                port = tds[1]
                latency = tds[4].split(' ')[0]
                if float(latency) < 0.5:
                    proxy = "%s:%s"%(ip, port)
                    proxy_dict = {'http':proxy, 'https':proxy}
                    valid_res = self.proxy_vaild(proxy_dict)
                    if valid_res[0]:
                        proxyes.append(valid_res[1])
            logger.info('抓取 kxdaili 第 %d 页，有效代理 %d 个'%(page, len(proxyes)))
            page += 1
        return proxyes

    def save_proxy(self, res_list):
        df = pd.DataFrame(res_list)
        df.to_csv('proxy.csv')
        logger.info('_______代理已储存________')

    def read_proxy_file(self, csv_path):
        df = pd.read_csv(csv_path)[['http','https']]
        read_dict = df.to_dict(orient='records')
        return read_dict

    def fetch_new_proxyes(self, num):
        crawls = [self.fetch_ip181, self.fetch_66ip, self.fetch_xici, self.fetch_kxdaili]
        valid_proxyes = []
        demand_num = num
        for crawl in crawls:
            new_proxyes = crawl(demand_num)
            logger.info('_______抓取新代理%s________'%len(new_proxyes))
            valid_proxyes += new_proxyes
            demand_num -= len(new_proxyes)
            if demand_num <= 0:
                logger.info('_______代理抓取完毕，共%s________'%len(valid_proxyes))
                # self.save_proxy(valid_proxyes)
                break
            else:
                continue
        return valid_proxyes


    def get_proxy(self):
        if len(self.proxys) == 0:
            self.proxys = self.fetch_new_proxyes(5)
            return self.proxys.pop()
        else:
            return self.proxys.pop()






if __name__ == "__main__":
    proxy_clawer = Fetch_proxy()
    for i in range(11):
        print(i)
        print(proxy_clawer.process())



