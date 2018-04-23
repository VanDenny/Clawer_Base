import pymongo
import sys
import traceback
import pandas as pd
import os
from Clawer_Base.g_geocode import G_Geocoding, G_Params
from Clawer_Base.progress_bar import view_bar
import json



# class MongoConn:
#     def __init__(self, dbname):
#         self.client = pymongo.MongoClient("127.0.0.1:27017")
#         self.db = self.client[dbname]
#
#
#     def pct_indb(self, cllection, ):


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




if __name__ == "__main__":
    pct_indb = PCT_indb(r'D:\program_lib\PCT_Tool\PCT_result\detail\JP\JP_PCT_detail_merge_applicant_add1.csv')
    pct_indb.geocoding()


