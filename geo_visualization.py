from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import os
import threading
import shapefile
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class Geo_Visual:
    def __init__(self, pic_name, sf_path, figsize):
        self.fig = plt.figure(figsize=figsize)
        sf = shapefile.Reader(sf_path)
        boundry = sf.bbox
        self.map = Basemap(llcrnrlon=boundry[0],
                           llcrnrlat=boundry[1],
                           urcrnrlon=boundry[2],
                           urcrnrlat=boundry[3],
                           resolution='f',
                           projection='cass',
                           lat_0=boundry[1],
                           lon_0=boundry[0])
        self.shapefile_basemap = self.map.readshapefile(sf_path, 'states', drawbounds=True,color='#ffffff')
        self.map.drawmapboundary(fill_color='aqua', linewidth=0.5)
        self.map.fillcontinents(color='#ababab', lake_color='#5e8fb9')
        self.map.drawcoastlines(linewidth=0.5)
        self.pic_name = pic_name
        plt.title(self.pic_name)


    def add_patch(self, lng1, lat1, lng2, lat2):
        x1, y1 = self.map(lng1, lat1)
        x2, y2 = self.map(lng2, lat2)
        heigh = y2 - y1
        width = x2 - x1
        plt.gca().add_patch(plt.Rectangle((x1, y1), width, heigh, lw=0.5, edgecolor='r', facecolor='none', alpha=0.5))
        # self.pause(1)

    def add_patch_thread(self, lng1, lat1, lng2, lat2):
        th = threading.Thread(target=Geo_Visual.add_patch, args=(self, lng1, lat1, lng2, lat2))
        th.start()
        th.join()

    def pause(self, second):
        plt.pause(second)

    def savefig(self, file_name, dpi=300, bbox_inches='tight'):
        folder_path = 'stat_raster'
        if os.path.exists(folder_path):
            pass
        else:
            os.makedirs(folder_path)
        plt.savefig('%s/%s' %(folder_path, file_name), dpi=dpi, bbox_inches=bbox_inches)

if __name__ == "__main__":
    boundry = [112.954052, 22.562273, 114.056561, 23.936955]
    shapefile = r"D:\program_lib\GDPOI\guangzhou\广州shapefile"
    a_pic = Geo_Visual('测试图片', boundry, shapefile, figsize=[20, 15])
    lng_list = np.linspace(112.954052, 114.056561, 20)
    lat_list = np.linspace(22.562273, 23.936955, 20)
    for i in range(20):
        x1 = np.random.choice(lng_list)
        x2 = np.random.choice(lng_list)
        y1 = np.random.choice(lat_list)
        y2 = np.random.choice(lat_list)
        lng1 = min([x1, x2])
        lng2 = max([x1, x2])
        lat1 = min([y1, y2])
        lat2 = max([y1, y2])
        a_pic.add_patch(lng1, lat1, lng2, lat2)
    a_pic.savefig('pic.png')

        # print('%s_%s_%s_%s' % (lng1, lat1, lng2, lat2))





