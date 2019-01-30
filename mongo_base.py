import pymongo
from pprint import pprint
from Clawer_Base.io_base import Form_IO
import datetime
from tqdm import tqdm
from Clawer_Base.res_extractor import Res_Extractor

class Mongo_Base:

    def __init__(self, host, port, dbname, username, password):
        self.db = self.connect(host, port, dbname)
        if username:
            self.auth(username, password)

    def connect(self, host, port, dbname):
        """
        数据库连接
        :param host: 服务器地址
        :param port: 服务器端口
        :param dbname: 数据库名称
        :return: 数据库实例
        """
        print('开始连接数据库')
        client = pymongo.MongoClient(host=host, port=port)
        db = client[dbname]
        return db

    def auth(self, username, password):
        """
        数据库身份认证
        :param username: 用户名
        :param password: 密码
        :return:
        """
        print('开始身份认证')
        try:
            self.db.authenticate(username, password)
            print("身份认证成功")
        except:
            print("身份认证失败")

    def remove(self, collectionname, rule):
        """
        数据删除
        :param collectionname: 数据集名称
        :param rule: 查询语句{'statistic_num': ''}
        :return:
        """
        collection = self.db[collectionname]
        result = collection.remove(rule)
        print("已删除 %s " % result)

    def insert_many(self, collectionname, items):
        collection = self.db[collectionname]
        for i in tqdm(range(len(items))):
            time_now = datetime.datetime.now()
            items[i]['insert_time'] = time_now
            items[i]['update_time'] = time_now
        collection.insert_many(items)

    def delete_one(self, collectionname, rule):
        collection = self.db[collectionname]
        result = collection.delete_one(rule)
        # print("已删除 %s " % result)

    def delete_many(self, collectionname, rule):
        """
        数据删除
        :param collectionname: 数据集名称
        :param rule: 查询语句{'age': {'$lt': 25}}
        :return:
        """
        collection = self.db[collectionname]
        result = collection.delete_many(rule)
        count = result.deleted_count
        print("已删除 %s 条数据" % count)

    def update_by_id(self, collection, item):
        """
        更新数据
        :param collection: 数据集名称
        :param item: 要更新的内容
        :return:
        """
        update_time = datetime.datetime.now()
        item.update({'update_time': update_time})
        self.db[collection].update({'id': item['id']}, {"$set": item})

    def query(self, collectionname, rule):
        res = self.db[collectionname].find(rule)
        count = res.count()
        print("查询到结果 %s " % count)
        return res

    def group_stat(self, collection):
        """分组统计"""
        res = self.db[collection].aggregate([{'$group': {
            "_id": {"index_name": "$index_name", "year": "$year"},
            # "unit": "$unit",
            "count": {"$sum": 1}
        }}])
        res_extend = Res_Extractor()
        res_list = []
        for item in res:
            new_item = res_extend.json_flatten(item)
            res_list.append(new_item)
        return res_list



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


    def update_many(self, collectionname, items):
        new_items = []
        update_ids = []
        for item in tqdm(items):
            new_item = self.item_process(item)
            update_ids.append(new_item['_id'])
            del new_item['_id']
            new_items.append(new_item)
        print("开始插入新数据")
        self.insert_many(collectionname, new_items)
        print("删除旧数据")
        for _id in tqdm(update_ids):
            rule = {"_id": _id}
            self.delete_one(collectionname, rule)


    def item_process(self, item):
        """具体数据处理过程，根据需要改写"""
        pass

    def generate_index(self):
        pass

    def process(self):
        pass

    def output(self, path, res, filename):
        if not isinstance(res, list):
            res = list(res)
        f_io = Form_IO(path)
        f_io.saver(res, 'output', header=filename)

