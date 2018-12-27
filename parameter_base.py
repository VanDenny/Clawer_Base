from Clawer_Base.key_changer import Key_Manager

class Params(dict):
    """
    参数基类, 所有requests请求参数引用基类
    支持 key 更新
    """

    def __init__(self, std_param, key_type=''):
        super().__init__(self)
        self.update(std_param)
        # 初始化 key 变换器
        if key_type:
            self.key_manager = Key_Manager(key_type)
            self.init_key()

    def init_key(self):
        """
        获取初始KEY
        :return:
        """
        key_dict = self.key_manager.random_choice()
        super(Params, self).update(key_dict)

    def update_key(self):
        """
        当key用完后更新
        :return:
        """
        key_dict = self.key_manager.update()
        super(Params, self).update(key_dict)

