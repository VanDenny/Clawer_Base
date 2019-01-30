from Clawer_Base.clawer_frame import Clawer
from Clawer_Base.logger import logger

class G_Params(dict):
    def __init__(self, a_dict):
        super(G_Params, self).update(a_dict)

    def update_proxys(self, proxys):
        if isinstance(proxys, dict) and proxys.__contains__('proxys'):
            super(G_Params, self).update(proxys)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'proxys'")


    def update_address(self, address):
        if isinstance(address, dict) and address.__contains__('address'):
            super(G_Params, self).update(address)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'address'")

    def update_key(self, keys):
        if isinstance(keys, dict) and keys.__contains__('key'):
            super(G_Params, self).update(keys)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'key'")

class G_Geocoding(Clawer):
    def __init__(self, params):
        super(G_Geocoding, self).__init__(params)
        self.url = 'https://maps.googleapis.com/maps/api/geocode/json?'
        self.key_type = u'谷歌逆地址'

    def scheduler(self):
        status_dict = {
            "OK": self.status_ok,
            "ZERO_RESULTS": self.status_pass,
            "OVER_QUERY_LIMIT": self.status_change_key,
            "REQUEST_DENIED": self.status_change_proxy,
            "INVALID_REQUEST": self.status_invalid_request,
            "UNKNOWN_ERROR": self.status_unknown_error
        }
        if self.respond != None :
            status = self.respond.get('status')
            if status:
                return status_dict[status]()
            else:
                self.status_change_user_agent()
        else:
            pass

    def status_ok(self):
        results = self.respond.get('results')
        if results:
            res_list = []
            for i in results:
                res_list.append(self.parser(i))
            print('%s 地址获取成功' % self.params['address'])
            return res_list
        else:
            logger.info('结果为空 %s' % self.req.url)

    def parser(self, json_dict):
        res_dict = {}
        geometry = json_dict.get('geometry')
        location = geometry.get('location')
        address_components = json_dict.get('address_components')
        res_dict['place_id'] = json_dict.get('place_id')
        if json_dict.get('types'):
            res_dict['types'] = json_dict.get('types')[0]
        else:
            res_dict['types'] = ''
        res_dict['location_type'] = geometry.get('location_type')
        res_dict['lng'] = location.get('lng')
        res_dict['lat'] = location.get('lat')
        res_dict['formatted_address'] = json_dict.get('formatted_address')
        for i in address_components:
            if i.get('types'):
                key_name = i.get('types')[0]
            else:
                key_name = ''
            long_name = i.get('long_name')
            res_dict[key_name] = long_name
        return res_dict


if __name__ == "__main__":
    param = G_Params({
        'address': '1600 Amphitheatre Parkway, Mountain View, CA',
        'key': 'AIzaSyDum6Yxm-_V-L94lub8aokJdzYR7CbL1kU'
    })
    g_geocode = G_Geocoding(param)
    print(g_geocode.process())
