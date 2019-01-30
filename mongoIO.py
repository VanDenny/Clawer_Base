import pymongo
from tqdm import tqdm
from pprint import pprint
from Clawer_Base.io_base import Form_IO
import datetime
import pandas as pd
import os
from Clawer_Base.g_geocode import G_Geocoding, G_Params
from Clawer_Base.progress_bar import view_bar
from math import isnan
from yearbook.get_hash import Generate_ID
import json

class OutDB:
    def __init__(self):
        self.client = pymongo.MongoClient(host='192.168.2.91', port=27017)
        self.res_list = []

    def finder(self, db, collection, dict):
        self.collection = self.client[db][collection]
        self.res_list = self.collection.find(dict)
        print('查询到结果 %s 条' % self.res_list.count())
        return self.res_list


class PCT_indb:
    def __init__(self, file_path):
        self.file_path = file_path
        self.folder_path, self.file_name = os.path.split(file_path)
        if '.csv' in self.file_path:
            f = open(file_path)
            self.df = pd.read_csv(f, na_values='')
        elif '.xls' in self.file_path or '.xlsx' in self.file_path:
            self.df = pd.read_excel(file_path, na_values='')
        else:
            print('出错啦')

    def extract_agent_info(self, item):
        print(type(item['Agent']))
        if item['Agent'] and isinstance(item['Agent'], str):
            agents = eval(item['Agent'])
            pub_No = item['Pub.No.']
            new_info_list = []
            for name, add_info in agents.items():
                info_dict = {}
                info_dict['Pub_No'] = pub_No
                info_dict['Name'] = name
                info_dict['Nation'], info_dict['Post_code'], info_dict['Address'] = add_info
                new_info_list.append(info_dict)
            return new_info_list
        else:
            pass

    def extract_applicant_info(self, item):
        print(type(item['Applicants']))
        if item['Applicants'] and isinstance(item['Applicants'], str):
            applicants = eval(item['Applicants'])
            pub_No = item['Pub.No.']
            new_info_list = []
            for name, add_info in applicants.items():
                info_dict = {}
                info_dict['Pub_No'] = pub_No
                info_dict['Name'] = name
                info_dict['Nation'], info_dict['Post_code'], info_dict['Address'] = add_info
                new_info_list.append(info_dict)
            return new_info_list
        else:
            pass

    def form_split(self):
        items = self.df.to_dict(orient='records')
        applicant_list = []
        agent_list = []
        for item in items:
            print(item)
            app_res = self.extract_applicant_info(item)
            agent_res = self.extract_agent_info(item)
            if app_res:
                applicant_list += self.extract_applicant_info(item)
            if agent_res:
                agent_list += self.extract_agent_info(item)
        app_df = pd.DataFrame(applicant_list)
        agent_df = pd.DataFrame(agent_list)
        applicant_file_name = self.file_name.split('.')[0] + '_applicant.csv'
        agent_file_name = self.file_name.split('.')[0] + '_agent.csv'
        app_df.to_csv(self.folder_path + '/' + applicant_file_name)
        agent_df.to_csv(self.folder_path + '/' + agent_file_name)

    def geocoding(self):
        items = self.df.to_dict(orient='records')
        new_items = []
        for order, item in enumerate(items):
            view_bar(order, len(items))
            address = item['Address']
            print(address)
            if address and isinstance(address, str):
                param = G_Params({
                    'address': address,
                    'key': 'AIzaSyDum6Yxm-_V-L94lub8aokJdzYR7CbL1kU'
                })
                geocode_dict = G_Geocoding(param).process()
                if geocode_dict:
                    item.update(geocode_dict[0])
            new_items.append(item)
        with_add_df = pd.DataFrame(new_items)
        with_add_file_name = self.file_name.split('.')[0] + '_geocode.csv'
        with_add_df.to_csv(self.folder_path + '/' + with_add_file_name)

class Excel_Reader:
    def __init__(self, filepath):
        self.filepath = filepath

    def reader(self):
        """读取表格数据"""
        fextension = os.path.splitext(self.filepath)[1]
        if fextension in ['.xls', '.xlsx']:
            xl = pd.ExcelFile(self.filepath)
            sheetnames = xl.sheet_names
            if len(sheetnames) > 1:
                raise Exception('%s 工作簿存在多个工作表' % self.filepath)
            else:
                df = xl.parse(sheetnames[0])
                # df = df.set_index(index_name)
        elif fextension in ['.csv']:
            with open(self.filepath) as f:
                df = pd.read_csv(f)
        else:
            print('%s 不是表格数据，跳过读取' % self.filepath)
            df = ''
        df.fillna('', inplace=True)
        return df

    def del_col(self, df, col_list):
        """删除字段"""
        for col in col_list:
            del df[col]
        return df


    def to_dictlist(self, df):
        """将读取的表格数据转为字典列表"""

        dictlist = df.to_dict('records')
        return dictlist




class Insertor:
    def __init__(self, db):
        self.db = db

    def insert_many(self, item_list, collection_name):
        collection = self.db[collection_name]
        if item_list:
            print('增加insert_time字段，检查tag类型')
            for i in tqdm(len(item_list)):
                item_list[i]['tag'] = eval(item_list[i]['tag'])
                item_list[i]['insert_time'] = datetime.datetime.now()
            collection.insert_many(item_list)
        else:
            print('没有条目，跳过插入')

    def list_insert(self, item_list, collection_name):
        collection = self.db[collection_name]
        for item in tqdm(item_list):
            collection.insert(item)

    def item_insert(self, item, collection_name):
        collection = self.db[collection_name]
        result = collection.insert(item)
        print(result)

    def drop_dup(self, item_list, collection_name):
        """根据数据库是否存在条目去重"""
        print('开始去重')
        unique_list = []
        for item in tqdm(item_list):
            count = self.db[collection_name].count({'id': item['id']})
            if count == 0:
                unique_list.append(item)
        unique_list = list(set(unique_list))
        print('数据： %s, 唯一数据： %s' % (len(item_list), len(unique_list)))
        return unique_list

    def insert_unique(self, item_list, collection_name):
        unique_list = self.drop_dup(item_list, collection_name)
        self.insert_many(unique_list, collection_name)


class Data_Audit:
    """审查录入数据,将不合格数据输出成表格"""
    def __init__(self, audit_keys, id_keys, file_path):
        self.file_path = file_path
        self.audit_keys = audit_keys
        self.id_keys = id_keys
        self.disorder_res = []
        self.generate_md5 = Generate_ID.generate_md5

    def check(self, item):
        """检查关键字段是否缺失"""
        is_valid = 1
        for key in self.audit_keys:
            value = item.get(key)
            if bool(value)==False or isnan(value):
                is_valid = 0
                self.disorder_res.append(item)
                break
            else:
                continue
        if is_valid:
            return item
        else:
            return

    def stat_id(self, stat_item):
        """给每条统计数据生成唯一识别码，便于去重"""
        id_str = '-'.join([str(stat_item[i]) for i in self.id_keys])
        # print(id_str)
        id_code = self.generate_md5(id_str)
        # print(id_code)
        return id_code


    def audit(self, item_list):
        valid_list = []
        for item in item_list:
            if self.check(item):
                item['id'] = self.stat_id(item)
                valid_list.append(item)
        print("审查数据条数： %s, 合格数据条数：%s" % (len(item_list), len(valid_list)))
        return valid_list


    def saver(self, base_df):
        """在现有文件夹中，根据结果条数生成相应的表格形式"""
        file_name = os.path.splitext(self.file_path)[0]
        max_line = base_df.shape[0]
        if max_line < 1048576:
            outpath = file_name + '_irregular.xlsx'
            base_df.to_excel(outpath)
        else:
            outpath = file_name + '_irregular.csv'
            base_df.to_csv(outpath)

class Generate_Index:
    """生成日期、城市、指标、标签索引表"""
    def __init__(self, item_list, cols=[]):
        self.item_list = item_list
        self.cols = cols
        self.tag_list = []
        self.tag_items = {}
        for col in cols:
            self.tag_items[col] = []
        self.map_list = []


    def collector(self, item):
        for col in self.cols:
            if col != 'tag':
                tag_name = item[col]
                link = {}
                tag_id = Generate_ID().generate_md5(tag_name)
                link['t_id'] = tag_id
                link['d_id'] = item['id']
                link['update_time'] = datetime.datetime.now()
                self.map_list.append(link)
                if tag_name not in self.tag_list:
                    self.tag_list.append(tag_name)
                    tag_item = {}
                    tag_item['id'] = tag_id
                    tag_item['name'] = tag_name
                    tag_item['update_time'] = datetime.datetime.now()
                    self.tag_items[col].append(tag_item)
                    # print(self.tag_items[col])
            else:
                tags = eval(item[col])
                if tags:
                    for tag_name in tags:
                        link = {}
                        tag_id = Generate_ID().generate_md5(tag_name)
                        link['t_id'] = tag_id
                        link['d_id'] = item['id']
                        link['update_time'] = datetime.datetime.now()
                        self.map_list.append(link)
                        if tag_name not in self.tag_list:
                            self.tag_list.append(tag_name)
                            if col in self.tag_items:
                                tag_item = {}
                                tag_item['id'] = tag_id
                                tag_item['name'] = tag_name
                                self.tag_items[col].append(tag_item)
                            else:
                                self.tag_items[col] = []

    def process(self):
        for item in tqdm(self.item_list):
            self.collector(item)

class Logger_Form:
    """记录插入数量，表更新情况"""
    def __init__(self):
        self.records = []

    def collect(self, collection_name, action, count, user_name):
        a_record = {}
        a_record['collection_name'] = collection_name
        a_record['action'] = action
        a_record['count'] = count
        a_record['user_name'] = user_name
        self.records.append(a_record)

class Authenticator:
    """数据库用户验证器"""
    def __init__(self, db, username, password):
        self.db = db
        self.username = username
        self.password = password

    def auth(self):
        self.db.authenticate(self.username, self.password)

class Connector:
    """数据库连接器"""
    def __init__(self, host, port, dbname):
        self.host = host
        self.port = port
        self.dbname = dbname

    def connect(self):
        client = pymongo.MongoClient(host=self.host, port=self.port)
        db = client[self.dbname]
        return db


class Uploader:
    """上传数据"""
    def __init__(self, config_dict):
        self.config_dict = config_dict

    def process(self):
        print("=============连接数据库=============")
        self.db = Connector(self.config_dict['host'], self.config_dict['port'], self.config_dict['db_name']).connect()
        Authenticator(self.db, self.config_dict['user'], self.config_dict['password']).auth()

        print("=============读取数据===============")
        excel_reader = Form_IO(self.config_dict['file_path'])
        item_list = excel_reader.read_to_itemlist(self.config_dict['file_path'])

        print("========审查数据,生成数据id==========")
        data_audit = Data_Audit(self.config_dict['audit_keys'], self.config_dict['id_keys'], self.config_dict['file_path'])
        item_list = data_audit.audit(item_list)

        print("=============数据去重===============")
        insertor = Insertor(self.db)
        unique_items = insertor.drop_dup(item_list, self.config_dict['main_collection_name'])

        print("=============提取索引===============")
        generate_index = Generate_Index(unique_items, self.config_dict['index_collection'])
        generate_index.process()

        print("============开始数据入库=============")
        print("=============插入数据===============")
        insertor = Insertor(self.db)
        insertor.insert_many(unique_items, self.config_dict['main_collection_name'])

        print('开始插入tag_map')
        insertor.insert_many(generate_index.map_list, 'tag_map')

        for col in tqdm(self.config_dict['index_collection']):
            collection_name = self.config_dict['index_collection'][col]
            print('开始插入 %s' % (collection_name))
            insertor.insert_unique(generate_index.tag_items.get(col), collection_name)

        print('数据库上传完毕')

class Update:
    """更新数据"""
    def __init__(self, config_dict):
        self.config_dict = config_dict
        print("=============连接数据库=============")
        self.db = Connector(config_dict['host'], config_dict['port'], config_dict['db_name']).connect()
        Authenticator(self.db, config_dict['user'], config_dict['password']).auth()

    def update_tag(self, collection, item_id, tag_list):
        update_time = datetime.datetime.now()
        self.db[collection].update({'id': item_id}, {"$set":{'tag': tag_list, 'update_time': update_time}})

    def process(self):
        """将字符标签改为列表"""
        res = self.db[self.config_dict['main_collection_name']].find({}, {'id': 1, 'tag': 1})
        print('开始更新tag')
        for item in tqdm(res):
            item_id = item['id']
            tag_list = item['tag']
            if isinstance(tag_list, str):
                tag_list = eval(item['tag'])
                self.update_tag('yearbook', item_id, tag_list)
            else:
                continue

class Remove:
    """删除数据"""
    def __init__(self, config_dict):
        print("=============连接数据库=============")
        self.db = Connector(config_dict['host'], config_dict['port'], config_dict['db_name']).connect()
        Authenticator(self.db, config_dict['user'], config_dict['password']).auth()

    def remove(self, rule):
        self.db['yearbook'].remove(rule)


class Query:
    """查询数据"""
    def __init__(self, config_dict):
        print("=============连接数据库=============")
        self.db = Connector(config_dict['host'], config_dict['port'], config_dict['db_name']).connect()
        Authenticator(self.db, config_dict['user'], config_dict['password']).auth()

    def general_query(self, year, province, city, county, indexname):
        """按照层级查询"""
        def to_list(keyword, obj):
            if isinstance(keyword, list):
                return keyword
            elif isinstance(keyword, obj):
                return [keyword]
            else:
                raise Exception("%s 必须为 %s 或 %s 列表形式" % (keyword, obj, obj))

        # 处理关键词，实现多年份查询，
        year_list = to_list(year, int)
        province_list = to_list(province, str)
        city_list = to_list(city, str)
        county_list = to_list(county, str)
        res = self.db['yearbook'].find({'year': {'$in': year_list},
                                            'provincetr': {'$in': province_list},
                                            'citytr': {'$in': city_list},
                                            'countytr': {'$in': county_list},
                                            'index_name': indexname
            })
        return res

    def aggregate_search(self, year, province, city, county, indexname):
        """按照层级查询"""
        def to_list(keyword, obj):
            if isinstance(keyword, list):
                return keyword
            elif isinstance(keyword, obj):
                return [keyword]
            else:
                raise Exception("%s 必须为 %s 或 %s 列表形式" % (keyword, obj, obj))

        # 处理关键词，实现多年份查询，
        year_list = to_list(year, int)
        province_list = to_list(province, str)
        city_list = to_list(city, str)
        county_list = to_list(county, str)
        res = self.db['yearbook'].aggregate([{"$match": {'year': {'$in': year_list},
                                            'provincetr': {'$in': province_list},
                                            'citytr': {'$in': city_list},
                                            'countytr': {'$in': county_list},
                                            'index_name': indexname
            }}, {'$project': {"_id": 0,
                              "year": 1,
                              "province": "$provincetr",
                              "city": "$citytr",
                              "distinct": 1,
                              "county": "$countytr",
                              "index_name": 1,
                              "statistic_num": 1,
                              "unit": 1
                              }}])
        return res

    def by_year(self, year):
        """按年查找，支持整形、字符串单年查找，支持元组范围查找"""
        if isinstance(year, int):
            ids = self.db['date'].find({'name': year})
        elif isinstance(year, str):
            year = int(year)
            ids = self.db['date'].find({'name': year})
        elif isinstance(year, tuple):
            date1 = int(year[0])
            date2 = int(year[1])
            ids = self.db['date'].find({'name': {'$gte': date1, '$lte': date2}})
        elif isinstance(year, list):
            date1 = int(year[0])
            date2 = int(year[1])
            ids = self.db['date'].find({'name': {'$in': [date1, date2]}})
        else:
            print('输入year不合法')
            ids = []
        map_list = []
        for year_item in tqdm(ids):
            print(year_item)
            map_list += self.db['tag_map'].find({'t_id': year_item['id']})
        res_list = [map_item['d_id'] for map_item in tqdm(map_list)]
        return res_list

    def by_year1(self, year):
        """按年查找，支持整形、字符串单年查找，支持元组范围查找"""
        if isinstance(year, int):
            ids = self.db['yearbook'].find({'year': year}, {'id': 1}).explain()
        elif isinstance(year, str):
            year = int(year)
            ids = self.db['yearbook'].find({'year': year}, {'id': 1})
        elif isinstance(year, tuple):
            date1 = int(year[0])
            date2 = int(year[1])
            ids = self.db['yearbook'].find({'year': {'$gte': date1, '$lte': date2}}, {'id': 1})
        elif isinstance(year, list):
            date1 = int(year[0])
            date2 = int(year[1])
            ids = self.db['yearbook'].find({'year': {'$in': [date1, date2]}}, {'id': 1})
        else:
            print('输入year不合法')
            ids = []
        # ids = [i['id'] for i in tqdm(ids)]
        return ids



    def by_city(self,city):
        pass

    def by_tag(self,tag):
        pass




if __name__ == "__main__":
    config_dict = {
        'host': '134.175.231.29',
        'port': 27017,
        'db_name': 'test',
        'main_collection_name': 'yearbook',
        'map_collection_name': 'tag_map',
        'user': 'Van_Denny',
        'password': 'denglifan1989',
        'file_path': '',
        'del_keys': ['Unnamed: 0'],
        'audit_keys': ['year', 'provincetr', 'citytr', 'countytr', 'distinct', 'index_name', 'statistic_num', 'from'],
        'id_keys': ['year', 'provincetr', 'citytr', 'countytr', 'distinct', 'index_name', 'statistic_num'],
        'index_collection': {'year': 'date',
                             'provincetr': 'province',
                             'citytr': 'city',
                             'countytr': 'county',
                             'index_name': 'index',
                             'tag': 'tag'}
    }
    # 更新标签
    # update_tag = Update(config_dict)
    # update_tag.process()

    # # 查询数据
    query = Query(config_dict)
    res = query.aggregate_search(2016, ['广东省'], ['广州市'], '', '第二产业从业人员')
    # res_list = [i for i in res]
    # df = pd.DataFrame(res_list)
    # df.to_excel("")
    for i in res:
        pprint(i)

    # 删除数据
    # remove = Remove(config_dict)
    # remove.remove({'statistic_num': ''})

    # 上传数据
    # print(res)
    # upload_data = Uploader(config_dict)
    # upload_data.process()



