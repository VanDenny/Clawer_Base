import shapefile
import os
from Clawer_Base.geo_lab import Rectangle
import Clawer_Base.transCoordinateSystem as tcs
from Clawer_Base.progress_bar import view_bar
import pandas as pd



class Shapefile_Write:
    filetype_dict = {'point': shapefile.POINT,
                     'line': shapefile.POLYLINE,
                     'ploygon': shapefile.POLYGON
                     }
    def __init__(self, filetype_str, field_list=[]):
        self.filetype_str = filetype_str
        filetype = self.filetype_dict[filetype_str]
        self.writer = shapefile.Writer(filetype)
        self.field_list = field_list
        if field_list:
            for i in field_list:
                self.writer.field(*i)

    def plot(self, points_list, record_tuple=()):
        if self.filetype_str == 'point':
                point_geo = tuple(points_list)
                self.writer.point(*point_geo)
        elif self.filetype_str == 'line':
            self.writer.poly(parts=[points_list], shapeType=shapefile.POLYLINE)
        else:
            self.writer.poly(parts=[points_list])

        if record_tuple:
            # record_dict = {}
            # keys = [i[0] for i in self.field_list]
            # for zip_tuple in zip(keys, record_tuple):
            #     record_dict[zip_tuple[0]] = zip_tuple[1]
            # print(record_dict)
            # self.writer.record(**record_dict)
            self.writer.record(*record_tuple)

    def save(self, file_path):
        dirname, filename = os.path.split(file_path)
        if os.path.exists(dirname):
            pass
        else:
            os.makedirs(dirname)
        self.writer.save(file_path)

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
            point_list.append([i['gcj_lng'], i['gcj_lat']])
            record_list.append([i['count']])
        return point_list, record_list

    def process(self):
        sw = Shapefile_Write('point', [["count", "N"]])
        point_list, record_list = self.excel_reader()
        for i in zip(point_list, record_list):
            sw.plot(i[0], tuple(i[1]))
        path_parts = os.path.splitext(self.file_path)
        sw.save(path_parts[0])



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
    # ct = Coor_ransfor(r'D:\GIS_workspace\仑头村\建筑_单部件', 'ploygon', 'wgs84_to_gcj02')
    # ct.write()
    dir_path = r'D:\GIS_workspace\仑头村1\20180604\海珠区'
    file_list = os.listdir(dir_path)
    for i in file_list:
        if '.xlsx' in i:
            file_path = os.path.join(dir_path, i)
            print(file_path)
            ets = Excel_to_shp(file_path)
            ets.process()






