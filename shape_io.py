# pyshp 2.0.1
import shapefile
import os
from Clawer_Base.geo_lab import Rectangle
import Clawer_Base.transCoordinateSystem as tcs
from Clawer_Base.progress_bar import view_bar
from file_pkg.file_path import generate_outpath
import pandas as pd
import json
from pprint import pprint
from tqdm import tqdm



class Shapefile_Write:
    featuretype_dict = {'point': shapefile.POINT,
                     'line': shapefile.POLYLINE,
                     'ploygon': shapefile.POLYGON
                     }
    def __init__(self, featuretype_str, out_path, field_list=[]):
        """
        :param featuretype_str: point line ploygon
        :param field_list: [('Build', "C"),]
        :param out_path: 输出文件地址
        """
        self.filetype_str = featuretype_str
        featuretype = self.featuretype_dict[featuretype_str]
        # print(featuretype)
        self.writer = shapefile.Writer(out_path, shapeType=featuretype)
        self.field_list = field_list
        if field_list:
            for i in field_list:
                self.writer.field(*i)

    def plot(self, points_list, record_tuple=()):
        """
        绘制一个图形
        :param points_list: 几何点列表
        :param record_tuple: 属性列表
        :return:
        """
        if self.filetype_str == 'point':
            # print(points_list)
            point_geo = tuple(points_list)
            if point_geo:
                # print(point_geo)
                self.writer.point(*point_geo)
            else:
                print('无法读取点几何属性')
        elif self.filetype_str == 'line':
            self.writer.line([points_list])
        else:
            self.writer.poly([points_list])

        # 添加属性
        if record_tuple:
            # record_dict = {}
            # keys = [i[0] for i in self.field_list]
            # for zip_tuple in zip(keys, record_tuple):
            #     record_dict[zip_tuple[0]] = zip_tuple[1]
            # print(record_dict)
            # self.writer.record(**record_dict)
            self.writer.record(*record_tuple)

    def save(self):
        self.writer.close()

class Shapefile_Reader:
    def __init__(self, file_path):
        self.sf = shapefile.Reader(file_path)

    def convert_to_rect(self, name_col):
        shapes = self.sf.shapes()
        records = self.sf.records()
        rect_list = []
        for i in zip(shapes, records):
            rect = Rectangle(*tuple(i[0].bbox))
            name = i[1][name_col]
            rect_list.append([name, rect])
        return rect_list

class Coor_ransfor:
    def __init__(self, file_path, filetype_str, mode):
        self.mode = mode
        self.file_path = file_path
        self.sf = shapefile.Reader(file_path)
        self.filetype_str = filetype_str

    def transfor(self):
        shapes = self.sf.shapes()
        parts = []
        for i in shapes:
            point_list = i.points
            print(point_list)
            for ord, point in enumerate(point_list):
                # print(point)
                point_list[ord] = self.point_transfor(point[0], point[1], self.mode)
            parts.append(point_list)
        return parts

    def write(self):
        parts = self.transfor()
        records = self.sf.records()
        field_list = self.sf.fields[1:]
        print(field_list)
        sw = Shapefile_Write(self.filetype_str, field_list)
        for i in zip(parts, records):
            # print(len(i[1]))
            sw.plot(i[0], tuple(i[1]))
        path_parts = os.path.splitext(self.file_path)
        print(path_parts)
        tail = self.mode.split('_')[-1]
        out_path = path_parts[0] + '_%s' % tail
        print(out_path)
        sw.save(out_path)



    def point_transfor(self, lon, lat, mode='wgs84_to_gcj02'):
        mode_dict = {
            'wgs84_to_gcj02': tcs.wgs84_to_gcj02,
            'gcj02_to_bd09': tcs.gcj02_to_bd09,
            'bd09_to_gcj02': tcs.bd09_to_gcj02,
            'gcj02_to_wgs84': tcs.gcj02_to_wgs84,
            'bd09_to_wgs84': tcs.bd09_to_wgs84,
            'wgs84_to_bd09': tcs.wgs84_to_bd09
        }
        if mode in mode_dict:
            print('%s_%s' % (lon, lat))
            return mode_dict[mode](lon, lat)
        else:
            print(
                    'plese input mode in (wgs84_to_gcj02, gcj02_to_wgs84, '
                    'gcj02_to_bd09, bd09_to_gcj02, bd09_to_wgs84, wgs84_to_bd09)'
            )


class Excel_to_shp:
    def __init__(self,file_path):
        self.file_path = file_path

    def excel_reader(self):
        df = pd.read_excel(self.file_path)
        records = df.to_dict(orient='records')
        point_list = []
        record_list = []
        for i in records:
            point_list.append([i['lng'], i['lat']])
            record_list.append([i['duration']])
        return point_list, record_list

    def process(self):
        sw = Shapefile_Write('point', [["duration", "N"]])
        point_list, record_list = self.excel_reader()
        for i in zip(point_list, record_list):
            sw.plot(i[0], tuple(i[1]))
        path_parts = os.path.splitext(self.file_path)
        sw.save(path_parts[0])


class Json_to_shp:
    """
    实现http://datav.aliyun.com/tools/atlas/#&lat=37.24782120155428&lng=109.05029296875&zoom=5
    网站行政边界转换
    创建日期：20181217
    """
    def __init__(self, file_path, feature_type, field_list):
        """
        :param file_path: json 文件路径
        :param feature_type: 要转换的shpfile文件类型
        :param field_list: 字段名称及属性
        """
        self.file_path = file_path
        self.field_list = field_list
        folder_path, filename = os.path.split(self.file_path)
        filename = filename.replace('.json', '')
        outpath = generate_outpath(folder_path, 'shpfile', filename)
        self.shp_writer = Shapefile_Write(feature_type, outpath, field_list)

    def json_reader(self):
        with open(self.file_path, encoding='UTF-8') as f:
            load_dict = json.load(f)
            # pprint(load_dict)
            return load_dict

    def saver(self):
        self.shp_writer.save()


    def transform(self):
        feature_json = self.json_reader()
        for feature in tqdm(feature_json['features']):
            f_properties = feature['properties']
            # f_type = feature['type']
            record_list = [str(f_properties.get(i[0])) for i in self.field_list]
            record_tuple = tuple(record_list)
            f_geomotry = feature['geometry']
            for part in f_geomotry['coordinates']:
                self.shp_writer.plot(part[0], record_tuple)
            # print(len(f_geomotry['coordinates']))
        self.saver()

class Shp_to_Csv:
    def __init__(self, file_path):
        self.file_path = file_path
        self.out_path = '.'.join([file_path, "csv"])

    def reader(self):
        self.sf = shapefile.Reader(self.file_path)

    def transform(self):
        self.reader()
        # field = self.sf.fields
        # pprint(field)
        records_num = len(self.sf.records())
        res_list = []
        for i in tqdm(range(records_num)):
            record = self.sf.record(i)
            record_dict = record.as_dict()
            res_list.append(record_dict)
            # pprint(records_dict)
        df = pd.DataFrame(res_list)
        df.rename(columns={'Field2': 'slng', 'Field3': 'slat',
                           'Field5': 'tlng', 'Field6': 'tlat'}, inplace=True)

        df.to_csv(self.out_path)





if __name__ == "__main__":
    # 文件输入
    # df = pd.read_csv('shape.csv', index_col='Buid')
    # build = list(set(df.index))
    # num = len(build)
    # print(num)
    # shape_writer = Shapefile_Write('ploygon', [('Build', "C"),])
    # for order, i in enumerate(build):
    #     view_bar(order, num)
    #     print(order)
    #     build_df = df[['CX', 'DY']][df.index == i]
    #     build_dict = build_df.to_dict('split')
    #     points = build_dict['data']
    #     shape_writer.plot(points, (i,))
    # shape_writer.save('D:\program_lib\Clawer_Base\pg_shape')
    #
    # sf_reader = Shapefile_Reader(r'D:\GIS_workspace\东莞\东莞')
    # print(sf_reader.convert_to_rect(16))

    # 图形坐标转换
    # ct = Coor_ransfor(r'F:\GIS_workspace\河源轨迹\驾车轨迹wgc84', 'line', 'wgs84_to_gcj02')
    # ct.write()

    # excel转点
    # dir_path = r'D:\program_lib\GD_Tool\Time_line_result\常平镇\常平镇'
    # file_list = os.listdir(dir_path)
    # for i in file_list:
    #     if '.xlsx' in i:
    #         file_path = os.path.join(dir_path, i)
    #         print(file_path)
    #         ets = Excel_to_shp(file_path)
    #         ets.process()

    # json 转 shp
    root_path = 'F:\GIS_workspace\新版行政边界\json\行政区json'
    file_list = os.listdir(root_path)
    for file in file_list:
        file_path = os.path.join(root_path, file)
        field_list = [('acroutes', 'C'),
                      ('adcode', 'C'),
                      ('center', 'C'),
                      ('centroid', 'C'),
                      ('childrenNum', 'C'),
                      ('level', 'C'),
                      ('name', 'C'),
                      ('parent', 'C'),
                      ('subFeatureIndex', 'C')
                      ]
        json2shp = Json_to_shp(file_path, 'ploygon', field_list)
        json2shp.transform()

    # # shp 转 csv
    # file_path = r"F:\GIS_workspace\OD Line\东莞od"
    # shp2csv = Shp_to_Csv(file_path)
    # shp2csv.transform()







