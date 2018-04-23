from math import radians, cos, sin, asin, sqrt, hypot
import shapefile

class Geo_Point:
    def __init__(self, lng, lat):
        self.lng = lng
        self.lat = lat

    def calc_distance(self,another_point):
        # 将十进制度转化为弧度
        lng1, lat1, lng2, lat2 = map(radians, [self.lng, self.lat, another_point.lng, another_point.lat])
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        h = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        earth_radius = 6371000
        distance = 2 * asin(sqrt(h)) * earth_radius
        return distance

class Rectangle:
    def __init__(self, lng1=0, lat1=0, lng2=0, lat2=0):
        self.lng1 = lng1
        self.lat1 = lat1
        self.lng2 = lng2
        self.lat2 = lat2
        self.left_up = Geo_Point(lng1, lat2)
        self.left_down = Geo_Point(lng1, lat1)
        self.right_up = Geo_Point(lng2, lat2)
        self.right_down = Geo_Point(lng2, lat1)
        self.center = Geo_Point((lng1+lng2)/2,(lat1+lat2)/2)
        self.wide = self.calc_wide()
        self.high = self.calc_high()
        self.radius = self.out_circle_radius()

    def calc_wide(self):
        return self.left_up.calc_distance(self.right_up)

    def calc_high(self):
        return self.left_up.calc_distance(self.left_down)

    def out_circle_radius(self):
        radius = hypot(self.wide, self.high)/2
        return radius

    def convert_to_outline_square(self):
        deg_per_meter = (self.lng2 - self.lng1)/self.wide
        new_lng1 = self.center.lng - (0.5 * deg_per_meter * self.high)
        new_lng2 = self.center.lng + (0.5 * deg_per_meter * self.high)
        return Rectangle(new_lng1, self.lat1, new_lng2, self.lat2)

    def read_from_shp(self, file_path):
        sf = shapefile.Reader(file_path)
        self.bbox = sf.bbox
        return Rectangle(*tuple(self.bbox))


    def divided_into_four(self):
        rect_left_down = Rectangle(self.left_down.lng,
                                   self.left_down.lat,
                                   self.center.lng,
                                   self.center.lat)
        rect_right_up = Rectangle(self.center.lng,
                                  self.center.lat,
                                  self.right_up.lng,
                                  self.right_up.lat)
        rect_left_up = Rectangle(self.left_down.lng,
                                 self.center.lat,
                                 self.center.lng,
                                 self.right_up.lat)
        rect_right_down = Rectangle(self.center.lng,
                                  self.left_down.lat,
                                  self.right_up.lng,
                                  self.center.lat)
        return [rect_left_down, rect_right_up, rect_left_up, rect_right_down]

    def convert_to_param_dict(self):
        a_dict = {}
        a_dict['location'] = str(self.center.lat) + ',' + str(self.center.lng)
        a_dict['radius'] = str(self.radius)
        return a_dict

    def convert_to_df_dict(self):
        a_dict = {}
        a_dict['lng'] = self.center.lng
        a_dict['lat'] = self.center.lat
        a_dict['radius'] = self.radius
        return a_dict

if __name__ == "__main__":
    a_rect = Rectangle().read_from_shp(r'D:\program_lib\GDPOI\guangzhou\广州shapefile')
    square = a_rect.convert_to_outline_square()
    print(square.lng1)
    print(square.lng2)
    print(square.lat1)
    print(square.lat2)