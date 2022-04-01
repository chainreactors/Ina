
class Client:
    # 定义client所需的基本接口
    def check_login(self):
        pass

    def query(self, *args, **kwargs):
        pass

    def request(self, api, param):
        pass
