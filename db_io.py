import pymongo
import pandas as pd
import datetime
import os
import time
from Clawer_Base.progress_bar import view_bar


date_today = datetime.datetime.now()


class Mongo_input:
    def __init__(self, db_name):
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client[db_name]

    def get_collection_names(self):
        return self.db.collection_names()

    def data_reader(self, path):
        print('读取 %s' % path)
        size = os.path.getsize(path)
        if size >= 10:
            if '.xlsx' in path or '.xls' in path:
                df = pd.read_excel(path)
                adict_list = df.to_dict('records')
                return adict_list
            elif '.csv' in path:
                df = pd.read_csv(path, engine='python')
                df = df.fillna('')
                del df['Unnamed: 0']
                adict_list = df.to_dict('records')
                return adict_list
            else:
                print('类型文件必须是excel 或 csv 文件')
        else:
            print('文件为空')



    def base_input(self, file_path, collection_name, unique_id,gene_date=date_today):
        collection = self.db[collection_name]
        adict_list = self.data_reader(file_path)
        if adict_list:
            length = len(adict_list)
            for order, items in enumerate(adict_list):
                view_bar(order, length)
                items_id = items[unique_id]
                res_list = collection.find({unique_id: items_id})
                res_num = res_list.count()
                if res_num == 0:
                    collection.insert(items)
                elif res_num == 1:
                    collection.update({unique_id: items_id}, {"$set": {"upDate": date_today}})
                else:
                    for i in range(length-1):
                        collection.remove({unique_id: items_id})
        else:
            print('文件为空')

    def input_many(self, file_path, collection_name):
        collection = self.db[collection_name]
        adict_list = self.data_reader(file_path)
        collection.insert(adict_list)

    def gdpoi_input(self, res_floder, collection_name):
        son_floders = os.listdir(res_floder)
        for son_floder in son_floders:
            gene_date = datetime.datetime.strptime(son_floder, "%Y%m%d")
            son_floder_path = os.path.join(res_floder, son_floder)
            files = os.listdir(son_floder_path)
            for file in files:
                print('%s %s 开始入库'% (file, son_floder))
                file_path = os.path.join(son_floder_path, file)
                self.base_input(file_path, collection_name, 'id', gene_date)


class Excel_merger:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def reader(self, path):
        mtime = os.path.getatime(path)
        gene_date = datetime.datetime.fromtimestamp(mtime)
        size = os.path.getsize(path)
        if size >= 10:
            if '.xlsx' in path or '.xls' in path:
                df = pd.read_excel(path)
                df['geneDate'] = gene_date
                # del df['Unnamed: 0']
                return df
            elif '.csv' in path:
                df = pd.read_csv(path, engine='python',)
                df['geneDate'] = gene_date
                del df['Unnamed: 0']
                return df
            else:
                print('类型文件必须是excel 或 csv 文件')
        else:
            print('文件为空')

    def merge(self):
        file_list = get_filepath(self.folder_path)
        df_list = []
        for file_path in file_list:
            print('开始读取 %s' % file_path)
            res = self.reader(file_path)
            if isinstance(res, pd.core.frame.DataFrame):
                df_list.append(res)
            else:
                pass
        all_df = pd.concat(df_list)
        print('合并完成')
        return all_df

    def dropduplicates(self, df, dup_col, sort_col):
        df = df.sort_values(by=sort_col)
        df.drop_duplicates(dup_col, inplace=True)
        print('去重完成')
        return df

    def split(self, df, col_name):
        splitdf = df[col_name].str.split(',', expand=True)
        df['lng'] = splitdf[0]
        df['lat'] = splitdf[0]
        del df[col_name]
        return df

    def saver(self, df):
        outfile = os.path.join(self.folder_path, 'merged.csv')
        df.to_csv(outfile)
        print('结果已保存')


    def process(self):
        # 根据具体需求组合
        df = self.merge()
        df = self.dropduplicates(df, 'id', 'geneDate')
        df = self.split(df, 'location')
        self.saver(df)

def get_filepath(folder_path):
    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        if files:
            for filename in files:
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)
    return file_paths


if __name__ == "__main__":
    # gdpoi_merger = Gdpoi_merger(r'D:\program_lib\GDPOI\GD_poi_result')
    # gdpoi_merger.process()
    # 修改
    mongo_input = Mongo_input('GD_POI')
    mongo_input.input_many(r'D:\program_lib\GDPOI\GD_poi_result\merged.csv', 'dataPool')


