import pymongo
import pandas as pd
import datetime


class Mongo_input:
    def __init__(self, db_name):
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client[db_name]

    def get_cllection_names(self):
        return self.db.collection_names()

    def data_reader(self, path, index_col):
        if '.xlsx' in path or '.xls' in path:
            df = pd.read_excel(path, index_col=index_col)
            adict_list = df.to_dict('records')
            return adict_list
        elif '.csv' in path:
            df = pd.read_csv(path, index_col=index_col)
            adict_list = df.to_dict('records')
            return adict_list
        else:
            print('类型文件必须是excel 或 csv 文件')


    def gdpoi_input(self, file_path):
        adict_list = self.data_reader(file_path, 'id')
        new_list = []
        while adict_list:
            adict = adict_list.pop()
            location = adict.pop('location')
            lng_lat = location.split(',')
            adict['lng'] = float(lng_lat[0])
            adict['lat'] = float(lng_lat[1])
            typecodes = adict['typecode'].split('|')
            for typecode in typecodes:
                adict['typecode'] = int(typecode)
                new_list.append(adict)





        adict['geneDate'] = datetime.datetime.now()





if __name__ == "__main__":
    mongo_input = Mongo_input('Google_POI')
    mongo_input.get_cllection_names()