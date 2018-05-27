import shapefile
import os
from Clawer_Base.geo_lab import Rectangle
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
        if field_list:
            for i in field_list:
                self.writer.field(*i)

    def plot(self, points_list, record_tuple=()):
        if self.filetype_str == 'point':
            for point in points_list:
                x, y = point
                self.writer.point(x, y)
        elif self.filetype_str == 'line':
            self.writer.poly(parts=[points_list], shapeType=shapefile.POLYLINE)
        else:
            self.writer.poly(parts=[points_list])

        if record_tuple:
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


if __name__ == "__main__":
    # 文件输入
    df = pd.read_csv('shape.csv', index_col='Buid')
    build = list(set(df.index))
    num = len(build)
    print(num)
    shape_writer = Shapefile_Write('ploygon', [('Build', "C"),])
    for order, i in enumerate(build):
        view_bar(order, num)
        build_df = df[['CX', 'DY']][df.index == i]
        build_dict = build_df.to_dict('split')
        points = build_dict['data']
        shape_writer.plot(points, (i,))
    shape_writer.save('D:\program_lib\Clawer_Base\pg_shape')
    #
    # sf_reader = Shapefile_Reader(r'D:\GIS_workspace\东莞\东莞')
    # print(sf_reader.convert_to_rect(16))





