import pandas as pd
import os
import time
from Clawer_Base.logger import logger

class Form_IO:
    """
    表格数据处理v1.0 20181226
    """
    def __init__(self, path):
        self.filepath_list = self.get_filepath(path)
        self.root_path = ''
        self.core_name = ''
        self.fextension = ''

    def get_filepath(self, path):
        if os.path.isfile(path):
            self.root_path, self.core_name, self.fextension = self.filepath_decompass(path)
            filepath_list = [path]
        else:
            self.root_path = path
            filename_list = os.listdir(path)
            filepath_list = [os.path.join(path, i) for i in filename_list]
        return filepath_list

    def filepath_decompass(self, filepath):
        root_path, file_name = os.path.split(filepath)
        core_name, fextension = os.path.splitext(file_name)
        return root_path, core_name, fextension

    def read_to_df(self, filepath):
        if ('.xlsx' in filepath) or ('.xls' in filepath):
            xl = pd.ExcelFile(filepath)
            sheetnames = xl.sheet_names
            if len(sheetnames) > 1:
                raise Exception("%s 工作簿存在多个工作表" % filepath)
            else:
                df = xl.parse(sheetnames[0])
                df = df.fillna('')
            # del df['Unnamed: 0']
            return df
        elif '.csv' in filepath:
            with open(filepath) as f:
                df = pd.read_csv(f)
                df = df.fillna('')
                del df['Unnamed: 0']
            return df
        else:
            print('%s 不是指定格式文件')


    def read_to_itemlist(self, filepath):
        df = self.read_to_df(filepath)
        item_list = df.to_dict("records")
        return item_list

    def to_df(self, res):
        if isinstance(res, list):
            df = pd.DataFrame(res)
            return df
        else:
            return res

    def saver(self, res, folder='', header='', tail='', timestamp=True):
        """
        :param res: 需要保存的结果，可以为DateFrame 和 list 类型
        :param folder: 需要将结果保存到的结果文件夹名字
        :param header: 结果文件名前缀
        :param tail: 结果文件名后缀
        :param timestamp: 结果文件生成时间
        :return:
        """
        res = self.to_df(res)
        lines = res.shape[0]
        # 结果保存在新文件夹
        if folder:
            folder_path = os.path.join(self.root_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        else:
            folder_path = self.root_path

        # 文件名加前缀
        if header:
            filename = '_'.join([header, self.core_name])
        else:
            filename = self.core_name

        # 文件名加后缀
        if tail:
            filename = '_'.join([filename, tail])

        # 文件名加时间
        if timestamp:
            timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
            filename = "_".join([filename, timestamp])

        # 根据文件长度选择合适的文件格式
        if lines <= 1048576:
            filename += '.xlsx'
            out_path = os.path.join(folder_path, filename)
            res.to_excel(out_path)
        else:
            filename += '.csv'
            out_path = os.path.join(folder_path, filename)
            res.to_csv(out_path)
        print("结果已保存在 %s" % out_path)



if __name__ == "__main__":
    f_io = Form_IO(r'F:\文件保存测试\黄海北路_驾车120_2018_12_21_17_07_31_2018_12_21_17_44_24.csv')
    df = f_io.read_to_df()
    f_io.saver(df, "result", 'TEST')



