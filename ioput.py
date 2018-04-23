import pandas as pd
import os
import datetime
from Clawer_Base.logger import logger

class Type_Input:
    def __init__(self,type_file_path, col_name, res_floder, method=''):
        if '.xlsx' in  type_file_path or '.xls' in type_file_path:
            self.df = pd.read_excel(type_file_path, index_col= col_name)
        elif '.csv' in type_file_path:
            self.df = pd.read_csv(type_file_path, index_col= col_name)
        else:
            print('类型文件必须是excel 或 csv 文件')
        self.method = method
        self.res_floder = res_floder
        self.type_list = self.filter_by_method()
        self.type = ''

    def check_result(self):
        if os.path.exists(self.res_floder):
            file_list = []
            for (root,dirs,files) in os.walk(self.res_floder):
                file_list += files
            type_list = [i.split('.')[0].split('_')[0] for i in set(file_list)]
            return type_list
        else:
            return

    def filter_by_method(self):
        existing = self.check_result()
        if self.method == 'add' and existing:
            input_type = list(set(self.df.index) - set(existing))
        else:
            input_type = list(self.df.index)
        return input_type


    # def get_type(self):
    #     if self.type_list:
    #         self.type = self.type_list.pop()
    #         return self.type
    #     else:
    #         return
    #
    # def get_cname(self):
    #     return self.df.loc[self.type, 'cname']

    def convert_to_param_dict(self):
        a_dict = {}
        a_dict['types'] = self.type
        return a_dict

    def save_path_dict(self,floder_path):
        self.result_path = floder_path + '/' + '%s_result.csv'%(self.type)
        self.point_by_radius = floder_path + '/' + '%s_point_by_radius.csv'%(self.type)
        self.point_by_result = floder_path + '/' + '%s_point_by_results.csv'%(self.type)
        return self.result_path, self.point_by_radius, self.point_by_result


class Res_saver:
    """抓取结果保存器"""
    def __init__(self, res_list, file_name, floder_path='result', file_type='csv', duplicates_key=''):
        self.res_list = res_list
        self.file_name = file_name
        self.floder_path = floder_path
        self.date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.file_type = file_type
        self.duplicates_key = duplicates_key

    def save_as_file(self):
        if self.floder_path:
            if os.path.exists('%s/%s' %(self.floder_path, self.date_str[:8])):
                pass
            else:
                os.makedirs('%s/%s' %(self.floder_path, self.date_str[:8]))
        df = pd.DataFrame(self.res_list)
        if self.res_list:
            if self.duplicates_key:
                df.drop_duplicates(self.duplicates_key, inplace=True)
        else:
            print('%s 结果为空'% self.file_name)
            logger.info('%s 结果为空'% self.file_name)
        if self.file_type == 'csv':
            df.to_csv('%s/%s/%s_%s.csv' % (self.floder_path, self.date_str[:8], self.file_name, self.date_str[8:]))
        elif self.file_type == 'excel':
            df.to_excel('%s/%s/%s_%s.xlsx' % (self.floder_path, self.date_str[:8], self.file_name, self.date_str[8:]))
        else:
            """预留以后的数据库格式"""
            pass
        print('%s 结果已保存' % self.file_name)

# class Mongo_dumper:
#     def __init__(self,dbname):


