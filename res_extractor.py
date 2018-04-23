
class Res_Extractor:
    """展平抓取的Json数据，重命名"""
    def __init__(self, rename_dict={}):
        self.rename_dict = rename_dict

    def json_flatten(self, a_json, fa_key=''):
        if isinstance(a_json, dict):
            res_dict = {}
            for dict_key, dict_value in a_json.items():
                if fa_key:
                    son_key = '_'.join([str(fa_key), str(dict_key)])
                else:
                    son_key = dict_key
                res_dict.update(self.json_flatten(dict_value, son_key))
            return res_dict
        elif isinstance(a_json, list):
            res_dict = {}
            for i, list_value in enumerate(a_json):
                if fa_key:
                    son_key = '_'.join([str(fa_key), str(i)])
                else:
                    son_key = str(i)
                res_dict.update(self.json_flatten(list_value, son_key))
            return res_dict
        elif isinstance(a_json, (str, int, float)):
            a_dict = {}
            a_dict[fa_key] = a_json
            return a_dict
        else:
            print(type(a_json))


if __name__ == "__main__":
    a_cict = [{1:2, 3:5, 4:[1,2,3,4,5]},{1:4, 4:8}]
    res_extractor = Res_Extractor()
    print(res_extractor.json_flatten(a_cict))






