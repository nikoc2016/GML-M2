#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
2018-06-25 shiming
"""
import os
import sys
import re
import json
import time
import subprocess

G_tw_token = ""
G_tw_account_id = ""
G_tw_account = ""
G_tw_file_key = ""
G_tw_http_ip = ""
G_is_login = False
G_bin_path = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/")
G_cgtw_path = G_bin_path + "/cgtw/"
G_inside_path = G_bin_path + "/lib/inside"

sys.path.append(G_inside_path)
from websocket import create_connection
import requests

from twlib._con import _con
from twlib._con_local import _con_local
from twlib._client import _client
from twlib._module import _module

G_cgtw_session = requests.Session()


class tw:
    __version__ = "5.3.0"  # 当前api版本
    global G_tw_token
    global G_tw_account_id
    global G_tw_account
    global G_tw_file_key
    global G_tw_http_ip  # 用于python上传下载, 格式: ip:port
    global G_is_login  # 用于判断是否有登录
    global G_cgtw_path  # cgtw 路径

    def __init__(self, http_ip='', account='', password=''):
        u"""
         描述: 初始化, 备注:服务器IP,账号,密码都不填写的时候,会连接到客户端获取登陆信息
         调用: __init__(http_ip='', account='', password='')
              ---> http_ip                   服务器IP, (str/unicode)
              ---> account                   账号 (str/unicode)
              ---> password                  密码 (str/unicode)
         """
        global G_tw_token
        global G_tw_http_ip
        global G_is_login
        global G_tw_file_key
        global G_tw_account_id
        global G_tw_account
        global G_cgtw_path
        global G_bin_path

        # 是否使用系统代理---------
        t_is_use_system_proxy = False
        try:
            import ConfigParser
            t_file_path = G_cgtw_path + "config.ini"
            if os.path.exists(t_file_path):
                config = ConfigParser.ConfigParser()
                config.read(t_file_path)
                if config.has_option("General", "system_proxy"):
                    if unicode(config.get("General", "system_proxy")).lower().strip() == "y":
                        t_is_use_system_proxy = True
        except:
            pass

        if not t_is_use_system_proxy:
            G_cgtw_session.trust_env = False  # 禁止系统代理

        if unicode(http_ip).strip() != "" and unicode(account).strip() != "":
            # 设置代理数据---------------
            if t_is_use_system_proxy:
                from twlib._proxy import _proxy
                _proxy.set_proxy(G_cgtw_session, http_ip, G_bin_path)
            # 设置代理数据---------------

            G_tw_http_ip = _con.get_server_ip(G_cgtw_session, http_ip)  # 这个中间有用session去取数据，所以在前面要先设置代理
            t_login_data = tw.send_web("c_token", "login",
                                       {"account": account, "password": password, "client_type": "py"})
            if t_login_data == False:
                raise Exception("tw.Login fail")

            G_is_login = True
            G_tw_token = t_login_data["token"]
            G_tw_account_id = t_login_data["account_id"]
            G_tw_account = t_login_data["account"]
            G_tw_file_key = t_login_data["file_key"]

        else:
            if G_tw_http_ip == "":
                t_tw_http_ip = tw.send_local_socket("main_widget", "get_server_http", {}, "get")
                if isinstance(t_tw_http_ip, bool) != True and t_tw_http_ip != "":
                    G_tw_http_ip = t_tw_http_ip

                    # 设置代理数据---------------
                if t_is_use_system_proxy:
                    from twlib._proxy import _proxy
                    _proxy.set_proxy(G_cgtw_session, G_tw_http_ip, G_bin_path)
                # 设置代理数据---------------

            if G_tw_token == "":
                t_token = tw.send_local_socket("main_widget", "get_token", {}, "get")
                if isinstance(t_token, bool) != True and t_token != "":
                    G_tw_token = t_token
                    G_is_login = True

    def get_version(self):
        u"""
         描述: 获取tw版本
         调用: get_version()   
         返回: 成功返回str
         """
        return self.__version__

    def get_time(self):
        u"""
        描述: 获取服务器时间
        调用: get_time()   
        返回: 成功返回str, 2019-01-01 00:11:22
        """
        global G_tw_account_id
        global G_tw_token
        if tw.login.is_login() == False:
            return ""
        return tw.send_web("c_com", "get_time", {})

    # 发送到web
    @staticmethod
    def send_web(controller, method, data_dict):
        u"""
         描述: post到后台
         调用: send_web(controller, method, data_dict)
               ---> controller              控制器 (str/unicode)
               ---> method                  方法 (str/unicode)
               ---> data_dict               post的数据 (dict)
         返回: 按实际情况
         """
        global G_tw_http_ip
        global G_tw_token

        if not isinstance(controller, (str, unicode)) or not isinstance(method, (str, unicode)) or not isinstance(
                data_dict, dict):
            raise Exception("send_web argv error ,there must be (str/unicode, str/unicode, dict)")

        return _con.send(G_cgtw_session, G_tw_http_ip, G_tw_token, controller, method, data_dict)

    @staticmethod
    def send_local_http(db, module, action, other_data_dict, type="send"):
        u"""
         描述: post到客户端的http server
         调用: send_local_http(db, module, action, other_data_dict, type="send")
               ---> db                      数据库 (str/unicode)
               ---> module                  模块 (str/unicode)
               ---> action                  动作 (str/unicode)
               ---> other_data_dict         post的数据 (dict)
               ---> type                    类型 (str/unicode), send/get
               
         返回: 按实际情况
         """
        if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(action, (
                str, unicode)) or \
                not isinstance(other_data_dict, dict) or not isinstance(type, (
                str, unicode)):  # or type not in ['send','get']:
            raise Exception(
                "send_local_http argv error ,there must be (str/unicode, str/unicode, str/unicode, dict, str/unicode)")

        return _con_local.send_http(module, db, action, other_data_dict, type)

    @staticmethod
    def send_local_socket(sign, method, data, type="get"):
        u"""
         描述: post到客户端的websocket server
         调用: send_local_socket(sign, method, data, type="get")
               ---> sign                    标识 (str/unicode)
               ---> method                  方法 (str/unicode)
               ---> data                    post的数据 (dict)
                ---> type                   类型 (str/unicode), send/get
         返回: 按实际情况
         """
        if not isinstance(sign, (str, unicode)) or not isinstance(method, (str, unicode)) or not isinstance(data,
                                                                                                            dict) or not isinstance(
            type, (str, unicode)):
            raise Exception("send_local_socket argv error, there must be (str/unicode, str/unicode, dict, str/unicode)")
        return _con_local.send_socket(sign, method, data, type)

    @staticmethod
    def send_msg(db, module, module_type, task_id, account_id_list, content=""):
        u"""
         描述: 发送消息到客户端
         调用: send_msg(db, module, module_type, task_id, account_id_list, content="")
               ---> db                      数据库 (str/unicode)
               ---> module                  模块 (str/unicode)
               ---> module_type             模块类型 (str/unicode)
               ---> task_id                 任务ID (str/unicode)
               ---> account_id_list         账号ID列表 (list)
               ---> content                 发送的内容 (unicode)
         返回: 成功返回True
         """
        if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(task_id, (
                str, unicode)) or not isinstance(account_id_list, list) or \
                not isinstance(content, (str, unicode)) or not isinstance(module_type, (str, unicode)):
            raise Exception(
                "send_msg argv error ,there must be (str/unicode, str/unicode, str/unicode, str/unicode, list,  str/unicode)")
        return tw.send_web("c_msg", "send_task",
                           {"db": db, "module": module, "task_id": task_id, "account_id_array": account_id_list,
                            "content": content, "module_type": module_type})

    class client:

        @staticmethod
        def get_argv_key(key):
            u"""
             描述: 获取插件参数
             调用: get_argv_key(key)   
                   ---> key                 插件配置参数中的键 (str/unicode)
             返回: 成功返回str,失败返回False
             """
            if not isinstance(key, (str, unicode)):
                raise Exception("client.get_argv_key argv error, there must be (str/unicode)")

            return _client.get_argv_key(key)

        @staticmethod
        def get_sys_key(key):
            u"""
             描述: 获取系统参数
             调用: get_sys_key(key)   
                  ---> key                   键 (str/unicode)
             返回: 成功返回str/list, 失败返回Falase
             """
            if not isinstance(key, (str, unicode)):
                raise Exception("client.get_sys_key argv error, there must be (str/unicode)")

            return _client.get_sys_key(key)

        @staticmethod
        def get_database():
            u"""
             描述: 获取当前数据库
             调用: get_database()   
             返回: 成功返回str,失败返回False
             """
            return _client.get_database()

        @staticmethod
        def get_id():
            u"""
             描述: 获取界面选择的id列表
             调用: get_id()   
             返回: 成功返回list,失败返回False
             """
            return _client.get_id()

        @staticmethod
        def get_link_id():
            u"""
             描述: 获取link界面选择的id列表
             调用: get_link_id()   
             返回: 成功返回list,失败返回False
            """
            return _client.get_link_id()

        @staticmethod
        def get_module():
            u"""
             描述: 获取当前模块
             调用: get_module()   
             返回: 成功返回str,失败返回False
             """
            return _client.get_module()

        @staticmethod
        def get_module_type():
            u"""
             描述: 获取当前模块类型
             调用: get_module_type()   
             返回: 成功返回str,失败返回False
             """
            return _client.get_module_type()

        @staticmethod
        def get_file():
            u"""
             描述: 获取拖入文件框的源文件路径
             调用: get_file()   
             返回: 成功返回list,失败返回False
             """
            return _client.get_file()

        @staticmethod
        def get_folder():
            u"""
             描述: 获取拖入文件框,文件所在的目录
             调用: get_folder()   
             返回: 成功返回str,失败返回False
             """
            return _client.get_folder()

        @staticmethod
        def send_to_qc_widget(db, module, module_type, task_id, node_data_dict):
            # 发送给qt的界面弹出approve或者retake的界面
            # node_data_dict为里面一堆的节点的数据，用于更改流程
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    module_type, (str, unicode)) or not isinstance(task_id, (str, unicode)) or not isinstance(
                node_data_dict, dict):
                raise Exception(
                    "client.send_to_qc_widget argv error ,there must be (str/unicode, str/unicode, str/unicode, str/unicode, dict)")
            return tw.send_local_http(db, module, "send_to_qc_widget",
                                      {"node_data": [node_data_dict], "task_id": task_id, "module_type": module_type},
                                      "get")

    class login:

        @staticmethod
        def account():
            u"""
            描述: 获取当前登陆账号
            调用: account()   
            返回: 成功返回str
            """
            global G_tw_account
            global G_tw_token
            if tw.login.is_login() == False:
                return ""
            t_account = tw.send_web("c_token", "get_account", {"token": G_tw_token})
            return t_account

        @staticmethod
        def account_id():
            u"""
            描述: 获取当前登陆账号的ID
            调用: account_id()   
            返回: 成功返回str
            """
            global G_tw_account_id
            global G_tw_token
            if tw.login.is_login() == False:
                return ""
            return tw.send_web("c_token", "get_account_id", {"token": G_tw_token})

        @staticmethod
        def token():
            u"""
            描述: 获取验证的token
            调用: token()   
            返回: 成功返回str
            """
            global G_tw_token
            return G_tw_token

        @staticmethod
        def http_server_ip():
            u"""
            描述: 获取server 的IP
            调用: http_server_ip()   
            返回: 成功返回str
            """
            global G_tw_http_ip
            return G_tw_http_ip

        @staticmethod
        def is_login():
            u"""
            描述: 判断是否登录
            调用: is_login()   
            返回: 返回bool
            """
            global G_tw_token
            if G_tw_token == "":
                return False
            return True

    class status:

        @staticmethod
        def get_status_and_color():
            u"""
            描述: 获取状态的名称和颜色
            调用: get_status_and_color()
            返回: 成功返回dict
            """
            return tw.send_web("c_status", "get_status_and_color", {})

    class info:
        __module_type = "info"

        @staticmethod
        def modules(db):
            u"""
            描述: 获取可以调用的信息模块
            调用: modules(db)
                  --> db                      数据库 (str/unicode)
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)):
                raise Exception("info.modules argv error, there must be (str/unicode)")
            return _module.modules(tw.send_web, db, tw.info.__module_type)

        @staticmethod
        def fields(db, module):
            u"""
            描述: 获取字段标识, 用于查找数据
            调用: fields(db)
                  --> db                    数据库 (str/unicode)
                  --> module                模块 (str/unicode)
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)):
                raise Exception("info.fields argv error, there must be(str/unicode, str/unicode)")
            return _module.fields(tw.send_web, db, module, tw.info.__module_type)

        @staticmethod
        def fields_and_str(db, module):
            u"""
            描述: 获取字段标识和中文名, 用于查找数据
            调用: fields(db)
                  --> db                    数据库 (str/unicode)
                  --> module                模块 (str/unicode)
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)):
                raise Exception("info.fields_and_str argv error, there must be(str/unicode, str/unicode)")
            return _module.fields_and_str(tw.send_web, db, module, tw.info.__module_type)

        @staticmethod
        def get_id(db, module, filter_list, limit="5000", start_num=""):
            u"""
            描述: 获取ID列表
            调用: get_id(db, module, filter_list, limit="5000", start_num="")
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> filter_list             过滤语句列表 (list)
                 --> limit                   限制条数 (str/unicode), 默认是5000
                 --> start_num               开始条数 (str/unicode), 默认为""
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    filter_list, list) or \
                    not isinstance(limit, (str, unicode)) or not isinstance(start_num, (str, unicode)):
                raise Exception(
                    "info.get_id argv error, there must be(str/unicode, str/unicode, list, str/unicode, str/unicode)")
            return _module.get_id(tw.send_web, db, module, tw.info.__module_type, filter_list, limit, start_num)

        @staticmethod
        def get(db, module, id_list, field_sign_list, limit="5000", order_sign_list=[]):
            u"""
            描述: 取出相对应的字段信息
            调用: get(db, module, id_list, field_sign_list, limit="5000", order_sign_list=[])
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id_list                ID列表 (list)
                 --> field_sign_list        字段标识列表 (list)
                 --> limit                  限制条数 (str/unicode), 默认是5000
                 --> order_sign_list        顺序的字段标识列表 (list)
                 
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(field_sign_list, list) or not isinstance(limit, (str, unicode)) or not isinstance(
                order_sign_list, list):
                raise Exception(
                    "info.get argv error, there must be(str/unicode, str/unicode, list, list, str/unicode, list)")

            return _module.get(tw.send_web, db, module, tw.info.__module_type, id_list, field_sign_list, limit,
                               order_sign_list)

        @staticmethod
        def get_dir(db, module, id_list, folder_sign_list):
            u"""
            描述: 取出相对应的路径列表
            调用: get_dir(db, module, id_list, folder_sign_list)
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id_list                ID列表 (list)
                 --> folder_sign_list       目录标识列表 (list)

            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(folder_sign_list, list):
                raise Exception("info.get_dir argv error, there must be(str/unicode, str/unicode, list, list)")

            return _module.get_dir(tw.send_web, db, module, tw.info.__module_type, id_list, folder_sign_list)

        @staticmethod
        def get_field_and_dir(db, module, id_list, field_sign_list, folder_sign_list):
            u"""
            描述: 取出相对应的字段和路径
            调用: get_field_and_dir(db, module, id_list, field_sign_list, folder_sign_list)
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id_list                ID列表 (list)
                 --> field_sign_list        字段标识列表 (list)
                 --> folder_sign_list       目录标识列表 (list)

            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(field_sign_list, list) or not isinstance(folder_sign_list, list):
                raise Exception(
                    "info.get_field_and_dir argv error, there must be(str/unicode, str/unicode, list, list, list)")
            return _module.get_field_and_dir(tw.send_web, db, module, tw.info.__module_type, id_list, field_sign_list,
                                             folder_sign_list)

        @staticmethod
        def get_makedirs(db, module, id_list):
            u"""
            描述:获取要创建的目录
            调用:get_makedirs(db, module, id_list)
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id_list                ID列表 (list)
            返回: 成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list):
                raise Exception("info.get_makedirs argv error, there must be(str/unicode, str/unicode, list)")
            return _module.get_makedirs(tw.send_web, db, module, tw.info.__module_type, id_list)

        @staticmethod
        def get_sign_filebox(db, module, id, filebox_sign):
            u"""
            描述: 根据文件框标识获取文件框信息
            调用: get_sign_filebox(db, module, id, filebox_sign)
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id                     ID (str/unicode)
                 --> filebox_sign           文件框标识 (str/unicode)
            返回: 成功返回dict
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id, (
                    str, unicode)) or \
                    not isinstance(filebox_sign, (str, unicode)):
                raise Exception(
                    "info.get_sign_filebox argv error, there must be(str/unicode, str/unicode, str/unicode, str/unicode)")
            return _module.get_sign_filebox(tw.send_web, db, module, tw.info.__module_type, id, filebox_sign)

        @staticmethod
        def get_filebox(db, module, id, filebox_id):
            u"""
            描述: 根据文件框ID获取文件框信息
            调用: get_filebox(db, module, id, filebox_id)
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id                     ID (str/unicode)
                 --> filebox_id             文件框ID (str/unicode)
            返回: 成功返回dict
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id, (
                    str, unicode)) or \
                    not isinstance(filebox_id, (str, unicode)):
                raise Exception(
                    "info.get_filebox argv error, there must be(str/unicode, str/unicode, str/unicode, str/unicode)")
            return _module.get_filebox(tw.send_web, db, module, tw.info.__module_type, id, filebox_id)

        @staticmethod
        def set(db, module, id_list, sign_data_dict):
            u"""
            描述: 修改数据
            调用: set(db, module, id_list, sign_data_dict)
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id_list                ID列表 (list)
                 --> sign_data_dict         更新的数据(dict), 格式:{"字段标识" : "值", "字段标识" : "值" }
            返回: 成功返回True
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(sign_data_dict, dict):
                raise Exception("info.set argv error, there must be(str/unicode, str/unicode, list, dict)")
            return _module.set(tw.send_web, db, module, tw.info.__module_type, id_list, sign_data_dict)

        @staticmethod
        def delete(db, module, id_list):
            u"""
            描述: 删除数据
            调用: delete(db, module, id_list)
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id_list                ID列表 (list)
            返回: 成功返回True
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list):
                raise Exception("info.delete argv error, there must be(str/unicode, str/unicode, list)")
            return _module.delete(tw.send_web, db, module, tw.info.__module_type, id_list)

        @staticmethod
        def create(db, module, sign_data_dict, is_return_id=False):
            u"""
            描述: 创建数据
            调用: create(db, module, sign_data_dict)
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> sign_data_dict         创建的数据 (dict), 格式:{字段标识1: 值1, 字段标识2: 值2, 字段标识3:值3}
                 --> is_return_id           是否返回创建的ID （bool）,  is_return_id=True,返回的是创建的ID
            返回: 成功返回True/str
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    sign_data_dict, dict) or \
                    not isinstance(is_return_id, bool):
                raise Exception("info.create argv error, there must be(str/unicode, str/unicode, dict, bool)")

            return _module.create(tw.send_web, db, module, tw.info.__module_type, sign_data_dict, is_return_id)

        @staticmethod
        def download_image(db, module, id_list, field_sign, is_small=True, local_path=""):
            u"""
            描述: 下载图片
            调用: download_image(db, module, id_list, field_sign, is_small=True, local_path="")
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id_list                ID列表 (list)
                 --> field_sign             图片字段标识 (str/unicode)
                 --> is_small               是否下载小图 (bool), 默认为True
                 --> local_path             指定路径 (unicode), 默认为temp路径
            返回: 成功返回list
            """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(field_sign, (str, unicode)) or not isinstance(is_small, bool) or not isinstance(
                local_path, (str, unicode)):
                raise Exception(
                    "info.download_image argv error, there must be(str/unicode, str/unicode, list,  str/unicode, bool, unicode)")

            return _module.download_image(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, module,
                                          tw.info.__module_type, id_list, field_sign, is_small, local_path)

        @staticmethod
        def set_image(db, module, id_list, field_sign, img_path, compress="1080"):
            u"""
             描述: 修改图片字段的图片
             调用: set_image(db, module, id_list, field_sign, img_path, compress="1080")
                  --> db                    数据库 (str/unicode)
                  --> module                模块 (str/unicode)
                  --> id_list               ID列表 (list)
                  --> field_sign            图片字段标识 (str/unicode)
                  --> img_path              图片路径 (str/unicode/list)
                  --> compress              压缩比例 (str/unicode), 可选值 no_compress(无压), 1080(1920x1080), 720(1280x720), 540(960x540)
             返回: 成功返回True
             """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token

            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(field_sign, (str, unicode)) or not isinstance(img_path, (
                    str, unicode, list)) or not isinstance(compress, (str, unicode)):
                raise Exception(
                    "info.set_image argv error, there must be(str/unicode, str/unicode, list, str/unicode, str/unicode/list, str/unicode)")
            return _module.set_image(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, module,
                                     tw.info.__module_type, id_list, field_sign, img_path, compress)

        @staticmethod
        def count(db, module, filter_list):
            u"""
             描述: 计算数量
             调用: count(db, module, filter_list)
                  --> db                    数据库 (str/unicode)
                  --> module                模块 (str/unicode)
                  --> filter_list           过滤语句列表 (list)
             返回: 成功返回str
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    filter_list, list):
                raise Exception("info.count argv error, there must be(str/unicode, str/unicode, list)")
            return _module.count(tw.send_web, db, module, tw.info.__module_type, filter_list)

        @staticmethod
        def distinct(db, module, filter_list, field_sign, order_sign_list=[]):
            u"""
             描述: 取某列字段消除重复后的结果
             调用: distinct(db, module, filter_list, field_sign, order_sign_list=[])
                  --> db                    数据库 (str/unicode)
                  --> module                模块 (str/unicode)
                  --> filter_list           过滤语句列表 (list)
                  --> field_sign            字段标识 (str/unicode)
                  --> order_sign_list       排序列表 (list)
             返回: 成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    filter_list, list) or \
                    not isinstance(field_sign, (str, unicode)) or not isinstance(order_sign_list, list):
                raise Exception(
                    "info.distinct argv error, there must be(str/unicode, str/unicode, list, str/unicode, list)")
            return _module.distinct(tw.send_web, db, module, tw.info.__module_type, filter_list, field_sign,
                                    order_sign_list)

        @staticmethod
        def group_count(db, module, field_sign_list, filter_list):
            u"""
             描述: 分组计算数量
             调用: group_count(db, module, field_sign_list, filter_list)
                  --> db                    数据库 (str/unicode)
                  --> module                模块 (str/unicode)
                  --> field_sign_list       字段标识列表 (list)
                  --> filter_list           过滤语句列表 (list)
             返回: 成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    field_sign_list, list) or \
                    not isinstance(filter_list, list):
                raise Exception("info.group_count argv error, there must be(str/unicode, str/unicode, list, list)")

            return _module.group_count(tw.send_web, db, module, tw.info.__module_type, field_sign_list, filter_list)

    class task:
        __module_type = "task"

        @staticmethod
        def modules(db):
            u"""
            描述: 获取可以调用的制作模块
            调用: modules(db)
                  --> db                    数据库 (str/unicode)
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)):
                raise Exception("task.modules argv error, there must be (str/unicode)")
            return _module.modules(tw.send_web, db, tw.task.__module_type)

        @staticmethod
        def fields(db, module):
            u"""
            描述: 获取字段标识, 用于查找数据
            调用: fields(db)
                  --> db                    数据库 (str/unicode)
                  --> module                模块 (str/unicode)
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)):
                raise Exception("task.fields argv error, there must be(str/unicode, str/unicode)")
            return _module.fields(tw.send_web, db, module, tw.task.__module_type)

        @staticmethod
        def fields_and_str(db, module):
            u"""
            描述: 获取字段标识和中文名, 用于查找数据
            调用: fields(db)
                  --> db                    数据库 (str/unicode)
                  --> module                模块 (str/unicode)
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)):
                raise Exception("task.fields_and_str argv error, there must be(str/unicode, str/unicode)")
            return _module.fields_and_str(tw.send_web, db, module, tw.task.__module_type)

        @staticmethod
        def get_id(db, module, filter_list, limit="5000", start_num=""):
            u"""
            描述: 获取ID列表
            调用: get_id(db, module, filter_list, limit="5000", start_num="")
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> filter_list            过滤语句列表 (list)
                 --> limit                  限制条数 (str/unicode), 默认是5000
                 --> start_num              起始条数 (str/unicode), 默认为""
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    filter_list, list) or \
                    not isinstance(limit, (str, unicode)) or not isinstance(start_num, (str, unicode)):
                raise Exception(
                    "task.get_id argv error, there must be(str/unicode, str/unicode, list, str/unicode, str/unicode)")
            return _module.get_id(tw.send_web, db, module, tw.task.__module_type, filter_list, limit, start_num)

        @staticmethod
        def get(db, module, id_list, field_sign_list, limit="5000", order_sign_list=[]):
            u"""
            描述: 取出相对应的字段信息
            调用: get(db, module, id_list, field_sign_list, limit="5000", order_sign_list=[])
                 --> db                     数据库 (str/unicode)
                 --> module                 模块 (str/unicode)
                 --> id_list                ID列表 (list)
                 --> field_sign_list        字段标识列表 (list)
                 --> limit                  限制条数 (str/unicode), 默认是5000
                 --> order_sign_list        排序的字段标识列表 (list)
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(field_sign_list, list) or not isinstance(limit, (str, unicode)) or not isinstance(
                order_sign_list, list):
                raise Exception(
                    "task.get argv error, there must be(str/unicode, str/unicode, list, list, str/unicode, list)")

            return _module.get(tw.send_web, db, module, tw.task.__module_type, id_list, field_sign_list, limit,
                               order_sign_list)

        @staticmethod
        def get_dir(db, module, id_list, folder_sign_list):
            u"""
            描述: 取出相对应的路径列表
            调用: get_dir(db, module, id_list, folder_sign_list)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> id_list                 ID列表 (list)
                 --> folder_sign_list        目录标识列表 (list)

            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(folder_sign_list, list):
                raise Exception("task.get_dir argv error, there must be(str/unicode, str/unicode, list, list)")
            return _module.get_dir(tw.send_web, db, module, tw.task.__module_type, id_list, folder_sign_list)

        @staticmethod
        def get_field_and_dir(db, module, id_list, field_sign_list, folder_sign_list):
            u"""
            描述: 取出相对应的字段和路径
            调用: get_field_and_dir(db, module, id_list, field_sign_list, folder_sign_list)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> id_list                 ID列表 (list)
                 --> field_sign_list         字段标识列表 (list)
                 --> folder_sign_list        目录标识列表 (list)

            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(field_sign_list, list) or not isinstance(folder_sign_list, list):
                raise Exception(
                    "task.get_field_and_dir argv error, there must be(str/unicode, str/unicode, list, list, list)")
            return _module.get_field_and_dir(tw.send_web, db, module, tw.task.__module_type, id_list, field_sign_list,
                                             folder_sign_list)

        @staticmethod
        def get_makedirs(db, module, id_list):
            u"""
            描述:获取要创建的目录
            调用:get_makedirs(db, module, id_list)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> id_list                 ID列表 (list)
            返回: 成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list):
                raise Exception("task.get_makedirs argv error, there must be(str/unicode, str/unicode, list)")
            return _module.get_makedirs(tw.send_web, db, module, tw.task.__module_type, id_list)

        @staticmethod
        def get_submit_filebox(db, module, id):
            u"""
            描述: 获取提交文件框信息
            调用: get_submit_filebox(db, module, id)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> id                      ID (str/unicode)
            返回: 成功返回dict
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id, (
                    str, unicode)):
                raise Exception(
                    "task.get_submit_filebox argv error, there must be(str/unicode, str/unicode, str/unicode)")
            return _module.get_submit_filebox(tw.send_web, db, module, tw.task.__module_type, id)

        @staticmethod
        def get_sign_filebox(db, module, id, filebox_sign):
            u"""
            描述: 根据文件框标识获取文件框信息
            调用: get_sign_filebox(db, module, id, filebox_sign)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> id                      ID (str/unicode)
                 --> filebox_sign            文件框标识 (str/unicode)
            返回: 成功返回dict
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id, (
                    str, unicode)) or \
                    not isinstance(filebox_sign, (str, unicode)):
                raise Exception(
                    "task.get_sign_filebox argv error, there must be(str/unicode, str/unicode, str/unicode, str/unicode)")
            return _module.get_sign_filebox(tw.send_web, db, module, tw.task.__module_type, id, filebox_sign)

        @staticmethod
        def get_filebox(db, module, id, filebox_id):
            u"""
            描述: 根据文件框ID获取文件框信息
            调用: get_filebox(db, module, id, filebox_id)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> id                      ID (str/unicode)
                 --> filebox_id              文件框ID (str/unicode)
            返回: 成功返回dict
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id, (
                    str, unicode)) or \
                    not isinstance(filebox_id, (str, unicode)):
                raise Exception(
                    "task.get_filebox argv error, there must be(str/unicode, str/unicode, str/unicode, str/unicode)")
            return _module.get_filebox(tw.send_web, db, module, tw.task.__module_type, id, filebox_id)

        @staticmethod
        def set(db, module, id_list, sign_data_dict):
            u"""
            描述: 修改数据
            调用: set(db, module, id_list, sign_data_dict)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> id_list                 ID (list)
                 --> sign_data_dict          更新数据 (dict), 格式:{"字段标识" : "值", "字段标识" : "值" }
            返回: 成功返回True
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(sign_data_dict, dict):
                raise Exception("task.set argv error, there must be(str/unicode, str/unicode, list, dict)")
            return _module.set(tw.send_web, db, module, tw.task.__module_type, id_list, sign_data_dict)

        @staticmethod
        def delete(db, module, id_list):
            u"""
            描述: 删除数据
            调用: delete(db, module, id_list)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> id_list                 ID列表 (list)
            返回: 成功返回True
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list):
                raise Exception("task.delete argv error, there must be(str/unicode, str/unicode, list)")
            return _module.delete(tw.send_web, db, module, tw.task.__module_type, id_list)

        @staticmethod
        def create(db, module, join_id, pipeline_id, task_name, flow_id):
            u"""
            描述: 创建
            调用: create(db, module, join_id, pipeline_id, task_name, flow_id)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> join_id                 信息表的ID (str/unicode)
                 --> pipeline_id             阶段ID (str/unicode)
                 --> task_name               任务名称 (str/unicode)
                 --> flow_id                 流程ID (str/unicode)
            返回: 成功返回list
            """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(join_id, (
                    str, unicode)) or \
                    not isinstance(pipeline_id, (str, unicode)) or not isinstance(task_name,
                                                                                  (str, unicode)) or not isinstance(
                flow_id, (str, unicode)):
                raise Exception(
                    "task.create argv error, there must be(str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, str/unicode)")
            return _module.create_task(tw.send_web, db, module, tw.task.__module_type, join_id, pipeline_id, task_name,
                                       flow_id)

        @staticmethod
        def download_image(db, module, id_list, field_sign, is_small=True, local_path=""):
            u"""
            描述: 下载图片
            调用: download_image(db, module, id_list, field_sign, is_small=True, local_path="")
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> id_list                 ID列表 (list)
                 --> field_sign              图片字段标识 (str/unicode)
                 --> is_small                是否下载小图 (bool), 默认为True
                 --> local_path              指定路径 (str/unicode), 默认为temp路径
            返回: 成功返回list
            """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(field_sign, (str, unicode)) or not isinstance(is_small, bool) or not isinstance(
                local_path, (str, unicode)):
                raise Exception(
                    "task.download_image argv error, there must be(str/unicode, str/unicode, list,  str/unicode, bool, str/unicode)")
            return _module.download_image(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, module,
                                          tw.task.__module_type, id_list, field_sign, is_small, local_path)

        @staticmethod
        def set_image(db, module, id_list, field_sign, img_path, compress="1080"):
            u"""
             描述: 修改图片字段的图片
             调用: set_image(db, module, id_list, field_sign, img_path, compress="1080")
                  --> db                     数据库 (str/unicode)
                  --> module                 模块 (str/unicode)
                  --> id_list                ID列表 (list)
                  --> field_sign             图片字段标识 (str/unicode)
                  --> img_path               图片路径 (str/unicode/list)
                  --> compress               压缩比例 (str/unicode), 可选值 no_compress(无压), 1080(1920x1080), 720(1280x720), 540(960x540)
             返回: 成功返回True
             """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(field_sign, (str, unicode)) or not isinstance(img_path, (
                    str, unicode, list)) or not isinstance(compress, (str, unicode)):
                raise Exception(
                    "task.set_image argv error, there must be(str/unicode, str/unicode, list, str/unicode, str/unicode/list, str/unicode)")
            return _module.set_image(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, module,
                                     tw.task.__module_type, id_list, field_sign, img_path, compress)

        @staticmethod
        def count(db, module, filter_list):
            u"""
             描述: 计算数量
             调用: count(db, module, filter_list)
                  --> db                     数据库 (str/unicode)
                  --> module                 模块 (str/unicode)
                  --> filter_list            过滤语句列表 (list)
             返回: 成功返回str
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    filter_list, list):
                raise Exception("task.count argv error, there must be(str/unicode, str/unicode, list)")
            return _module.count(tw.send_web, db, module, tw.task.__module_type, filter_list)

        @staticmethod
        def distinct(db, module, filter_list, field_sign, order_sign_list=[]):
            u"""
             描述: 取某列字段消除重复后的结果
             调用: distinct(db, module, filter_list, field_sign, order_sign_list=[])
                  --> db                     数据库 (str/unicode)
                  --> module                 模块 (str/unicode)
                  --> filter_list            过滤语句列表 (list)
                  --> field_sign             字段标识 (str/unicode)
                  --> order_sign_list        排序列表 (list)
             返回: 成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    filter_list, list) or \
                    not isinstance(field_sign, (str, unicode)) or not isinstance(order_sign_list, list):
                raise Exception(
                    "task.distinct argv error, there must be(str/unicode, str/unicode, list, str/unicode, list)")
            return _module.distinct(tw.send_web, db, module, tw.task.__module_type, filter_list, field_sign,
                                    order_sign_list)

        @staticmethod
        def assign(db, module, id_list, assign_account_id, start_date="", end_date=""):
            u"""
             描述: 分配制作人员
             调用: assign(db, module,  id_list, assign_account_id, start_date="", end_date="")
                  --> db                      数据库 (str/unicode)
                  --> module                  模块 (str/unicode)
                  --> id_list                 ID列表 (list)
                  --> assign_account_id       制作者ID (str/unicode)
                  --> start_date              预计开始日期 (str/unicode), 格式:2018-01-01, 默认为""
                  --> end_date                预计完成日期 (str/unicode), 格式:2018-01-01, 默认为""
             返回: 成功返回True
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id_list,
                                                                                                              list) or \
                    not isinstance(assign_account_id, (str, unicode)) or not isinstance(start_date, (
                    str, unicode)) or not isinstance(end_date, (str, unicode)):
                raise Exception(
                    "task.assign argv error, there must be(str/unicode, str/unicode, list, str/unicode, str/unicode, str/unicode)")
            return _module.assign(tw.send_web, db, module, tw.task.__module_type, id_list, assign_account_id,
                                  start_date, end_date)

        @staticmethod
        def submit(db, module, id, file_path_list, note="", path_list=[]):
            u"""
             描述: 提交审核文件
             调用: submit(db, module, id, file_path_list, note="",path_list=[])
                  --> db                      数据库 (str/unicode)
                  --> module                  模块 (str/unicode)
                  --> id                      id (str/unicode)
                  --> file_path_list          文件完整路径列表 (list); 如拖入bb文件夹, 则为[z:/aa/bb/test001.0001.png, z:/aa/bb/test001.0002.png]
                  --> note                    内容 (str/unicode), 默认为""
                  --> path_list               文件路径列表 (list), 默认为[]; 如拖入bb文件夹,[z:/aa/bb], 如果提交的文件,两个是一样的。如果提交的是文件夹。这边记录到文件夹的名称
             返回: 成功返回True
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id, (
                    str, unicode)) or \
                    not isinstance(file_path_list, list) or not isinstance(note, (str, unicode)) or not isinstance(
                path_list, list):
                raise Exception(
                    "task.submit argv error, there must be(str/unicode, str/unicode, str/unicode, list, str/unicode, list)")
            t_account_id = tw.login.account_id()
            return _module.submit(tw.send_web, t_account_id, db, module, tw.task.__module_type, id, file_path_list,
                                  note, path_list)

        @staticmethod
        def update_flow(db, module, id, field_sign, status, note="", image_list=[]):
            u"""
             描述: 更改某环节状态
             调用: update_flow(db, module, id, field_sign, status, note="")
                  --> db                      数据库 (str/unicode)
                  --> module                  模块 (str/unicode)
                  --> id                      id (str/unicode)
                  --> field_sign              字段标识 (str/unicode)
                  --> status                  状态 (str/unicode)
                  --> note                    内容 (str/unicode), 默认为""
                  --> image_list              图片路径列表 (list), 默认为[]
             返回: 成功返回True
             """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(id, (
                    str, unicode)) or \
                    not isinstance(field_sign, (str, unicode)) or not isinstance(status,
                                                                                 (str, unicode)) or not isinstance(note,
                                                                                                                   (str,
                                                                                                                    unicode)) or \
                    not isinstance(image_list, list):
                raise Exception(
                    "task.update_flow argv error, there must be(str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, list)")
            return _module.update_flow(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, module,
                                       tw.task.__module_type, id, field_sign, status, note, image_list)

        @staticmethod
        def group_count(db, module, field_sign_list, filter_list):
            u"""
             描述: 分组计算数量
             调用: group_count(db, module, field_sign_list, filter_list)
                  --> db                    数据库 (str/unicode)
                  --> module                模块 (str/unicode)
                  --> field_sign_list       字段标识列表 (list)
                  --> filter_list           过滤语句列表 (list)
             返回: 成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    field_sign_list, list) or \
                    not isinstance(filter_list, list):
                raise Exception("task.group_count argv error, there must be(str/unicode, str/unicode, list, list)")
            return _module.group_count(tw.send_web, db, module, tw.task.__module_type, field_sign_list, filter_list)

    class note:
        @staticmethod
        def fields():
            u"""
             描述:获取note字段
             调用:fields()
             返回:成功返回list
             """
            from twlib._note import _note
            return _note.fields()

        @staticmethod
        def get_id(db, filter_list, limit="5000"):
            u"""
             描述:获取note ID列表
             调用:get_id(db, filter_list, limit="5000")
                  --> db                      数据库 (str/unicode)
                  --> filter_list             过滤语句列表 (list)
                  --> limit                   限制条数 (str/unicode), 默认是5000
             返回: 成功返回list
             """
            from twlib._note import _note
            if not isinstance(db, (str, unicode)) or not isinstance(filter_list, list) or not isinstance(limit, (
                    str, unicode)):
                raise Exception("note.get_id argv error, there must be(str/unicode, list, str/unicode)")

            return _note.get_id(tw.send_web, db, filter_list, limit)

        @staticmethod
        def get(db, id_list, field_list, limit="5000", order_list=[]):
            u"""
             描述:获取note信息
             调用:get(db, id_list, field_list, limit="5000", order_list=[])
                  --> db                      数据库 (str/unicode)
                  --> id_list                 ID列表 (list)
                  --> field_list              字段列表 (list)
                  --> limit                   限制条数 (str/unicode), 默认是5000
                  --> order_list              排序列表 (list)
             返回: 成功返回list
             """
            from twlib._note import _note
            if not isinstance(db, (str, unicode)) or not isinstance(id_list, list) or not isinstance(field_list,
                                                                                                     list) or \
                    not isinstance(limit, (str, unicode)) or not isinstance(order_list, list):
                raise Exception("note.get argv error, there must be(str/unicode, list, list, str/unicode, list)")

            return _note.get(tw.send_web, db, id_list, field_list, limit, order_list)

        @staticmethod
        def create(db, module, module_type, task_id_list, text, cc_acount_id="", image_list=[], is_return_id=False):
            u"""
             描述:创建
             调用:create(db, module, module_type, task_id_list, text, cc_acount_id="", image_list=[], is_return_id=False)
                  --> db                      数据库 (str/unicode)
                  --> module                  模块 (str/unicode)
                  --> module_type             模块类型 (str/unicode)
                  --> task_id_list            任务的ID列表 (list)
                  --> text                    内容 (str/unicode)
                  --> cc_acount_id            抄送账号ID (str/unicode), 默认为""
                  --> image_list              图片路径列表 (list), 默认为[]
                  --> is_return_id            是否返回创建的note ID
             返回:成功返回True
             """
            from twlib._note import _note
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            t_account_id = tw.login.account_id()

            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    module_type, (str, unicode)) or \
                    not isinstance(task_id_list, list) or not isinstance(text, (str, unicode)) or not isinstance(
                cc_acount_id, (str, unicode)) or \
                    not isinstance(image_list, list) or not isinstance(is_return_id, bool):
                raise Exception(
                    "note.create argv error, there must be(str/unicode, str/unicode, str/unicode, list, str/unicode, str/unicode, list, bool)")
            return _note.create(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, t_account_id, db, module,
                                module_type, task_id_list, text, cc_acount_id, image_list, is_return_id)

    class filebox:
        @staticmethod
        def fields():
            u"""
             描述:获取文件框字段
             调用:fields()
             返回:成功返回list
             """
            from twlib._filebox import _filebox
            return _filebox.fields()

        @staticmethod
        def get_id(db, filter_list):
            u"""
             描述:获取文件框ID列表
             调用:get_id(db, filter_list)
                  --> db                      数据库 (str/unicode)
                  --> filter_list             过滤语句列表 (list)
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(filter_list, list):
                raise Exception("filebox.get_id argv error ,there must be (str/unicode, list)")

            from twlib._filebox import _filebox
            return _filebox.get_id(tw.send_web, db, filter_list)

        @staticmethod
        def get(db, id_list, field_list):
            u"""
             描述:获取文件框信息
             调用:get(db, id_list, field_list)
                  --> db                      数据库(str/unicode)
                  --> id_list                 文件框ID列表 (list)
                  --> field_list              字段列表 (list)
             返回:成功返回list
             """
            from twlib._filebox import _filebox
            if not isinstance(db, (str, unicode)) or not isinstance(id_list, list) or not isinstance(field_list, list):
                raise Exception("filebox.get argv error ,there must be (str/unicode, list, list)")

            return _filebox.get(tw.send_web, db, id_list, field_list)

    class field:
        @staticmethod
        def type():
            u"""
             描述:获取字段类型
             调用:type()
             返回:成功返回list
             """
            from twlib._field import _field
            return _field.type()

        @staticmethod
        def create(db, module, module_type, chinese_name, english_name, sign, type, field_name=""):
            u"""
             描述:创建字段
             调用:create(db, module, module_type, chinese_name, english_name, sign, type, field_name="")
                  --> db                      数据库 (str/unicode)
                  --> module                  模块 (str/unicode)
                  --> module_type             模块类型 (str/unicode)
                  --> chinese_name            中文名 (str/unicode)
                  --> english_name            英文名 (str/unicode)
                  --> sign                    字段标识 (str/unicode)
                  --> type                    类型 (str/unicode)
                  --> field_name              字段名 (str/unicode), 默认为"",为空时,默认和sign一样
             返回:成功返回True
             """
            from twlib._field import _field
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    module_type, (str, unicode)) or \
                    not isinstance(chinese_name, (str, unicode)) or not isinstance(english_name,
                                                                                   (str, unicode)) or not isinstance(
                sign, (str, unicode)) or \
                    not isinstance(type, (str, unicode)) or not isinstance(field_name, (str, unicode)):
                raise Exception(
                    "field.create argv error ,there must be (str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, str/unicode)")
            return _field.create(tw.send_web, db, module, module_type, chinese_name, english_name, sign, type,
                                 field_name)

    class plugin:

        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """
            from twlib._plugin import _plugin
            return _plugin.fields()

        @staticmethod
        def get_id(filter_list):
            u"""
             描述:获取插件ID
             调用:get_id（filter_list）
                  --> filter_list            过滤语句列表 (list)
             返回:成功返回list
             """
            if not isinstance(filter_list, list):
                raise Exception("plugin.get_id argv error ,there must be (list)")

            from twlib._plugin import _plugin
            return _plugin.get_id(tw.send_web, filter_list)

        @staticmethod
        def get(id_list, field_list):
            u"""
             描述:获取插件信息
             调用:get(id_list, field_list)
                  --> id_list                ID列表 (list)
                  --> field_list             字段列表 (list)
             返回:成功返回list
             """
            if not isinstance(id_list, list) or not isinstance(field_list, list):
                raise Exception("plugin.get argv error ,there must be (list, list)")
            from twlib._plugin import _plugin
            return _plugin.get(tw.send_web, id_list, field_list)

        @staticmethod
        def get_argvs(id):
            u"""
             描述:获取插件配置参数
             调用:get_argvs(id):  
                  --> id                    插件ID (str/unicode)
             返回:成功返回dict
             """
            if not isinstance(id, (str, unicode)):
                raise Exception("plugin.get_argvs argv error ,there must be (str/unicode)")
            from twlib._plugin import _plugin
            return _plugin.get_argvs(tw.send_web, id)

        @staticmethod
        def set_argvs(id, argvs_dict):
            u"""
             描述:设置插件参数
             调用:set_argvs(id, argvs_dict):  
                  --> id                    插件ID (str/unicode)
                  --> argvs_dict            更新参数 (dict), 格式{'key':'value'}
             返回:成功返回True
             """
            if not isinstance(id, (str, unicode)) or not isinstance(argvs_dict, dict):
                raise Exception("plugin.set_argvs argv error ,there must be (str/unicode, dict)")
            from twlib._plugin import _plugin
            return _plugin.set_argvs(tw.send_web, id, argvs_dict)

    class pipeline:

        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """
            from twlib._pipeline import _pipeline
            return _pipeline.fields()

        @staticmethod
        def get_id(db, filter_list):
            u"""
             描述:获得阶段ID
             调用:get_id(db, filter_list)
                  --> db                    数据库 (str/unicode)
                  --> filter_list           过滤语句列表 (list)
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(filter_list, list):
                raise Exception("pipeline.get_id argv error ,there must be (str/unicode, list)")
            from twlib._pipeline import _pipeline
            return _pipeline.get_id(tw.send_web, db, filter_list)

        @staticmethod
        def get(db, id_list, field_list):
            u"""
             描述:获取阶段信息
             调用:get(db, id_list, field_list)
                  --> db                   数据库 (str/unicode)
                  --> id_list              ID列表 (list)
                  --> field_list           字段列表 (list)
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(id_list, list) or not isinstance(field_list, list):
                raise Exception("pipeline.get argv error ,there must be (str/unicode, list, list)")
            from twlib._pipeline import _pipeline
            return _pipeline.get(tw.send_web, db, id_list, field_list)

    class history:

        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """
            from twlib._history import _history
            return _history.fields()

        @staticmethod
        def get_id(db, filter_list, limit="5000"):
            u"""
             描述:获取历史id列表
             调用:get_id(db, filter_list, limit="5000")
                 --> db                    数据库 (str/unicode)
                 ---filter_list            过滤语句列表 (list)
                 --> limit                 限制条数 (str/unicode), 默认是5000
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(filter_list, list) or not isinstance(limit, (
                    str, unicode)):
                raise Exception("history.get_id argv error, there must be (str/unicode, list, str/unicode)")
            from twlib._history import _history
            return _history.get_id(tw.send_web, db, filter_list, limit)

        @staticmethod
        def get(db, id_list, field_list, limit="5000", order_list=[]):
            u"""
             描述:获取信息
             调用:get(db, id_list, field_list, limit="5000", order_list=[])
                 --> db                    数据库 (str/unicode)
                 --> id_list               id列表 (list)
                 --> field_list            字段列表 (list)
                 --> limit                 限制条数 (str/unicode), 默认是5000
                 --> order_list            排序列表 (list), 默认为[]
             返回: 成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(id_list, list) or not isinstance(field_list,
                                                                                                     list) or \
                    not isinstance(limit, (str, unicode)) or not isinstance(order_list, list):
                raise Exception("history.get argv error, there must be (str/unicode, list, list, str/unicode, list)")
            from twlib._history import _history
            return _history.get(tw.send_web, db, id_list, field_list, limit, order_list)

        @staticmethod
        def count(db, filter_list):
            u"""
             描述:获取数量
             调用:count(db, filter_list)
                  --> db                   数据库 (str/unicode)
                  --> filter_list          过滤语句列表 (list)
             返回:成功返回str
             """
            if not isinstance(db, (str, unicode)) or not isinstance(filter_list, list):
                raise Exception("history.count argv error, there must be (str/unicode, list)")
            from twlib._history import _history
            return _history.count(tw.send_web, db, filter_list)

    class link:
        @staticmethod
        def link_asset(db, module, module_type, id_list, link_id_list):
            u"""
             描述:关联资产
             调用:link_asset(db, module, module_type, id_list, link_id_list)
                 --> db                   数据库 (str/unicode)
                 --> module               模块 (str/unicode)
                 --> module_type          模块类型 (str/unicode)
                 --> id_list              任务ID列表 (list)
                 --> link_id_list         资产ID列表 (list)
             返回:成功返回True
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    module_type, (str, unicode)) or \
                    not isinstance(id_list, list) or not isinstance(link_id_list, list):
                raise Exception(
                    "link.link_asset argv error, there must be (str/unicode, str/unicode, str/unicode, list, list)")
            from twlib._link import _link
            return _link.link_asset(tw.send_web, db, module, module_type, id_list, link_id_list)

        @staticmethod
        def unlink_asset(db, module, module_type, id_list, link_id_list):
            u"""
             描述:取消关联资产
             调用:unlink_asset(db, module, module_type, id_list, link_id_list)
                 --> db                  数据库 (str/unicode)
                 --> module              模块 (str/unicode)
                 --> module_type         模块类型 (str/unicode)
                 --> id_list             任务ID列表 (list)
                 --> link_id_list        资产ID列表 (list)
             返回:成功返回True
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    module_type, (str, unicode)) or \
                    not isinstance(id_list, list) or not isinstance(link_id_list, list):
                raise Exception(
                    "link.unlink_asset argv error, there must be (str/unicode, str/unicode, str/unicode, list, list)")

            from twlib._link import _link
            return _link.unlink_asset(tw.send_web, db, module, module_type, id_list, link_id_list)

        @staticmethod
        def get_asset(db, module, module_type, id):
            u"""
             描述:获取关联资产ID
             调用:get_asset(db, module, module_type, id)
                 --> db                 数据库 (str/unicode)
                 --> module             模块 (str/unicode)
                 --> module_type        模块类型 (str/unicode)
                 --> id                 任务ID (str/unicode)
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    module_type, (str, unicode)) or \
                    not isinstance(id, (str, unicode)):
                raise Exception(
                    "link.get_asset argv error, there must be (str/unicode, str/unicode, str/unicode, str/unicode)")
            from twlib._link import _link
            return _link.get_asset(tw.send_web, db, module, module_type, id)

    class software:

        @staticmethod
        def types():
            u"""
             描述:获取软件类型
             调用:types()
             返回:成功返回list
             """
            from twlib._software import _software
            return _software.types(tw.send_web)

        @staticmethod
        def get_path(db, name):
            u"""
             描述:获取软件路径
             调用:get_path(db, name):
                  --> db                数据库 (str/unicode)
                  --> name              软件名称 (str/unicode)
             返回:成功返回str
             """
            if not isinstance(db, (str, unicode)) or not isinstance(name, (str, unicode)):
                raise Exception("software.get_path argv error, there must be (str/unicode, str/unicode)")
            from twlib._software import _software
            return _software.get_path(tw.send_web, db, name)

        @staticmethod
        def get_with_type(db, type):
            u"""
             描述: 根据类型获取软件信息
             调用: get_with_type(db, type):
                  --> db                数据库 (str/unicode)
                  --> type              软件类型 (str/unicode)
             返回: 成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(type, (str, unicode)):
                raise Exception("software.get_with_type argv error, there must be (str/unicode, str/unicode)")
            from twlib._software import _software
            return _software.get_with_type(tw.send_web, db, type)

    class api_data:

        @staticmethod
        def get(db, key, is_user=True):
            u"""
             描述:获取python存储信息
             调用:get(db, key, is_user=True)
                  --> db                数据库 (str/unicode)
                  --> key               键 (str/unicode)
                  --> is_user           是否为个人 (bool), 默认为True
                  
             返回:成功返回str
             """
            if not isinstance(db, (str, unicode)) or not isinstance(key, (str, unicode)) or not isinstance(is_user,
                                                                                                           bool):
                raise Exception("api_data.get argv error, there must be (str/unicode, str/unicode, bool)")
            from twlib._api_data import _api_data
            return _api_data.get(tw.send_web, db, key, is_user)

        @staticmethod
        def set(db, key, value, is_user=True):
            u"""
             描述:设置python存储信息
             调用:set(db, key, value, is_user=True)
                  --> db                数据库 (str/unicode)
                  --> key               键 (str/unicode)
                  --> value             值 (str/unicode)
                  --> is_user           是否为个人 (bool), 默认为True
                  
             返回:成功返回True
             """
            if not isinstance(db, (str, unicode)) or not isinstance(key, (str, unicode)) or not isinstance(value, (
                    str, unicode)) or \
                    not isinstance(is_user, bool):
                raise Exception("api_data.set argv error, there must be (str/unicode, str/unicode, str/unicode, bool)")
            from twlib._api_data import _api_data
            return _api_data.set(tw.send_web, db, key, value, is_user)

    class version:

        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """
            from twlib._version import _version
            return _version.fields()

        @staticmethod
        def get_id(db, filter_list, limit="5000"):
            u"""
             描述:获取版本ID列表
             调用:get_id(db, filter_list, limit="5000")
                  --> db                数据库 (str/unicode)
                  --> filter_list       过滤列表 (list)
                  --> limit             限制条数 (str/unicode), 默认是5000
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(filter_list, list) or not isinstance(limit, (
                    str, unicode)):
                raise Exception("version.get_id argv error, there must be (str/unicode, list, str/unicode)")
            from twlib._version import _version
            return _version.get_id(tw.send_web, db, filter_list, limit)

        @staticmethod
        def get(db, id_list, field_list, limit="5000"):
            u"""
             描述:获取版本信息
             调用:get(db, id_list, field_list, limit="5000")
                  --> db                数据库 (str/unicode)
                  --> id_list           ID列表 (list)
                  --> field_list        字段列表 (list)
                  --> limit             限制条数 (str/unicode), 默认是5000
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(id_list, list) or not isinstance(field_list,
                                                                                                     list) or \
                    not isinstance(limit, (str, unicode)):
                raise Exception("version.get argv error, there must be (str/unicode, list, list, str/unicode)")
            from twlib._version import _version
            return _version.get(tw.send_web, db, id_list, field_list, limit)

        @staticmethod
        def create(db, link_id, version, local_path_list=[], web_path_list=[], sign="", image_list=[], from_version=""):
            u"""
             描述:创建版本
             调用:create(db, link_id,  version, local_path_list=[], web_path_list=[], sign="", image_list=[], from_version="")
                  --> db                数据库 (str/unicode)
                  --> link_id           关联的任务ID (str/unicode)
                  --> version           版本 (str/unicode)
                  --> local_path_list   本地路径列表 (list), 默认为[]
                  --> web_path_list     web路径列表 (list), 默认为[]
                  --> sign              标识 (str/unicode),默认为""
                  --> image_list        图片列表 (list),默认为""
                  --> from_version      从版本更改 (str/unicode), 默认为""
             返回:成功返回True
             """
            if not isinstance(db, (str, unicode)) or not isinstance(link_id, (str, unicode)) or not isinstance(version,
                                                                                                               (str,
                                                                                                                unicode)) or \
                    not isinstance(local_path_list, list) or not isinstance(web_path_list, list) or not isinstance(sign,
                                                                                                                   (str,
                                                                                                                    unicode)) or \
                    not isinstance(image_list, list) or not isinstance(from_version, (str, unicode)):
                raise Exception(
                    "version.create argv error, there must be (str/unicode, str/unicode, str/unicode, list, list, str/unicode, list, str/unicode)")

            from twlib._version import _version
            return _version.create(tw.send_web, db, link_id, version, local_path_list, web_path_list, sign, image_list,
                                   from_version)

    class link_entity:

        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """
            from twlib._link_entity import _link_entity
            return _link_entity.fields()

        @staticmethod
        def get_name(db, link_id):
            u"""
             描述:获取关联实体名称
             调用:get_name(db, link_id)
                  --> db                数据库 (str/unicode)
                  --> link_id           关联任务的ID (str/unicode)
             返回:成功返回str
             """
            if not isinstance(db, (str, unicode)) or not isinstance(link_id, (str, unicode)):
                raise Exception("link_entity.get_name argv error, there must be (str/unicode, str/unicode)")
            from twlib._link_entity import _link_entity
            return _link_entity.get_name(tw.send_web, db, link_id)

        @staticmethod
        def get(db, filter_list=[]):
            u"""
             描述:获取关联实体名称列表
             调用:get(db, filter_list=[])
                  --> db                数据库 (str/unicode)
                  --> filter_list       过滤语句列表 (list)
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(filter_list, list):
                raise Exception("link_entity.get argv error, there must be (str/unicode, list)")
            from twlib._link_entity import _link_entity
            return _link_entity.get(tw.send_web, db, filter_list)

    class timelog:

        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """
            from twlib._timelog import _timelog
            return _timelog.fields()

        @staticmethod
        def get_id(db, filter_list, limit="5000"):
            u"""
             描述:获取版本ID列表
             调用:get_id(db, filter_list, limit="5000")
                  --> db               数据库 (str/unicode)
                  --> filter_list      过滤语句 (list)
                  --> limit            限制条数 (str/unicode), 默认是5000
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(filter_list, list) or not isinstance(limit, (
                    str, unicode)):
                raise Exception("timelog.get_id argv error, there must be (str/unicode, list, str/unicode)")
            from twlib._timelog import _timelog
            return _timelog.get_id(tw.send_web, db, filter_list, limit)

        @staticmethod
        def get(db, id_list, field_list, limit="5000", order_list=[]):
            u"""
             描述:获取版本信息
             调用:get(db, id_list, field_list, limit="5000", order_list=[])
                  --> db               数据库 (str/unicode)
                  --> id_list          ID列表  (list)
                  --> field_list       字段列表 (list)
                  --> limit            限制条数 (str/unicode), 默认是5000
                  --> order_list       排序列表 (list),默认为空
             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(id_list, list) or not isinstance(field_list,
                                                                                                     list) or \
                    not isinstance(limit, (str, unicode)) or not isinstance(order_list, list):
                raise Exception("timelog.get argv error, there must be (str/unicode, list, list, str/unicode, list)")
            from twlib._timelog import _timelog
            return _timelog.get(tw.send_web, db, id_list, field_list, limit, order_list)

        @staticmethod
        def create(db, task_id, module, module_type, use_time, date, text):
            u"""
             描述:创建
             调用:create(db, task_id, module, module_type, use_time, date, text)
                  --> db                数据库 (str/unicode)
                  --> task_id           关联的任务ID (str/unicode)
                  --> module            模块 (str/unicode)
                  --> module_type       模块类型 (str/unicode)
                  --> use_time          用时 (str/unicode)
                  --> date              日期 (str/unicode)
                  --> text              内容 (unicode)
             返回:成功返回True
             """
            if not isinstance(db, (str, unicode)) or not isinstance(task_id, (str, unicode)) or not isinstance(module, (
                    str, unicode)) or \
                    not isinstance(module_type, (str, unicode)) or not isinstance(use_time,
                                                                                  (str, unicode)) or not isinstance(
                date, (str, unicode)) or \
                    not isinstance(text, unicode):
                raise Exception(
                    "timelog.create argv error, there must be (str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, unicode)")
            from twlib._timelog import _timelog
            return _timelog.create(tw.send_web, db, task_id, module, module_type, use_time, date, text)

        @staticmethod
        def set_one(db, id, data_dict):
            u"""
             描述:更新单个
             调用:set_one(db, id, data_dict)
                  --> db                数据库 (str/unicode)
                  --> id                ID (str/unicode)
                  --> data_dict         更新的数据 (dict)
             返回:成功返回True
             """
            if not isinstance(db, (str, unicode)) or not isinstance(id, (str, unicode)) or not isinstance(data_dict,
                                                                                                          dict):
                raise Exception("timelog.set_one argv error, there must be (str/unicode, str/unicode, dict)")
            from twlib._timelog import _timelog
            return _timelog.set_one(tw.send_web, db, id, data_dict)

    class flow:
        @staticmethod
        def get_data(db, pipeline_id_list):
            u"""
             描述:获取流程数据
             调用:get_data(db, pipeline_id_list)
                  --> db                 数据库 (str/unicode)
                  --> pipeline_id_list   阶段D列表  (list)

             返回:成功返回list
             """
            if not isinstance(db, (str, unicode)) or not isinstance(pipeline_id_list, list):
                raise Exception("flow.get_data argv error, there must be (str/unicode, list)")
            from twlib._flow import _flow
            return _flow.get_data(tw.send_web, db, pipeline_id_list)

    class media_file:

        @staticmethod
        def download(db, module, module_type, task_id, filebox_id, is_download_all=True, is_show_exist=False,
                     call_back=None, des_dir=""):  # --20190122 des_dir
            u"""
            描述: 下载在线文件
            调用: download(db, module, module_type, task_id, filebox_id, is_download_all=True, is_show_exist=True, call_back=None, des_dir="")              #--20190122 des_dir
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> module_type             模块类型 (str/unicode)
                 --> task_id                 任务ID (str/unicode)
                 --> filebox_id              文件框ID (str/unicode)
                 --> is_download_all         是否下载所有(bool), 默认为True, 为False下载最大版本
                 --> is_show_exist           是否显示已经下载过的, 默认为False
                --> call_back                回调函数,用于计算进度, 默认为None
                 --> des_dir                 下载存放的目标路径(保存目录结构)                                                                               #--20190122 des_dir
                
            返回: 成功返回list
            """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            from twlib._media_file import _media_file

            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    module_type, (str, unicode)) or not isinstance(task_id, (str, unicode)) or \
                    not isinstance(filebox_id, (str, unicode)) or not isinstance(is_download_all,
                                                                                 bool) or not isinstance(is_show_exist,
                                                                                                         bool) or not isinstance(
                des_dir, (str, unicode)):  # --20190122 des_dir
                raise Exception(
                    "media_file.download argv error(str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, bool, bool, str/unicode)")  # --20190122 des_dir
            return _media_file.download(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, module, module_type,
                                        task_id, filebox_id, is_download_all, is_show_exist, des_dir,
                                        call_back)  # --20190122 des_dir

        @staticmethod
        def upload(db, module, module_type, task_id, filebox_id, sou_path_list, call_back=None):
            u"""
            描述: 上传到在线文件,不会进行转码
            调用: upload(db, module, module_type, task_id, filebox_id, sou_path_list)
                 --> db                      数据库 (str/unicode)
                 --> module                  模块 (str/unicode)
                 --> module_type             模块类型 (str/unicode)
                 --> task_id                 任务ID (str/unicode)
                 --> filebox_id              文件框ID (str/unicode)
                 --> sou_path_list           源文件列表 (list)
                 --> call_back               回调函数,用于计算进度, 默认为None
            返回: 成功返回True
            """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            from twlib._media_file import _media_file
            if not isinstance(db, (str, unicode)) or not isinstance(module, (str, unicode)) or not isinstance(
                    module_type, (str, unicode)) or not isinstance(task_id, (str, unicode)) or \
                    not isinstance(filebox_id, (str, unicode)) or not isinstance(sou_path_list, list):
                raise Exception(
                    "media_file.upload argv error(str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, list)")
            return _media_file.upload(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, module, module_type,
                                      task_id, filebox_id, sou_path_list, "", call_back)

        @staticmethod
        def download_path(db, online_path_list, des_path_list, call_back=None):
            u"""
            描述: 下载在线文件,只支持下载文件,暂不支持下载目录
            调用: download_path(db, online_path_list,  des_path_list="", call_back=None)              #--20190122 des_dir
                 --> db                       数据库 (str/unicode)
                 --> online_path_list         在线文件列表
                 --> des_path_list            下载存放的目标路径列表（个数和des_path_list对应）
                --> call_back                 回调函数,用于计算进度, 默认为None
            返回: 成功返回True
            """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            from twlib._media_file import _media_file

            if not isinstance(db, (str, unicode)) or not isinstance(online_path_list, list) or not isinstance(
                    des_path_list, list):  # --20190122 des_dir
                raise Exception("media_file.download_path argv error(str/unicode, list, list)")

            if len(online_path_list) != len(des_path_list):
                raise Exception("media_file.download_path the number of source and destination paths does not match")

            return _media_file.download_path(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, online_path_list,
                                             des_path_list, call_back)

        @staticmethod
        def upload_path(db, sou_path_list, online_path_list, call_back=None, metadata={}):
            u"""
            描述: 上传到在线文件,不会进行转码,只支持上传文件,暂不支持上传目录
            调用: upload(db, sou_path_list, online_path_list, call_back=None)
                 --> db                       数据库 (str/unicode)
                 --> sou_path_list            源文件列表 (list)
                 --> online_path_list         目标件列表 (list)
                 --> call_back                回调函数,用于计算进度, 默认为None
            返回: 成功返回True
            """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            from twlib._media_file import _media_file

            if not isinstance(db, (str, unicode)) or not isinstance(sou_path_list, list) or not isinstance(
                    online_path_list, list) or not isinstance(metadata, dict):
                raise Exception("media_file.upload_path argv error(str/unicode, list, list, dict)")

            if len(sou_path_list) != len(online_path_list):
                raise Exception("media_file.upload_path the number of source and destination paths does not match")

            return _media_file.upload_path(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, sou_path_list,
                                           online_path_list, call_back, metadata)

        @staticmethod
        def download_lastest(db, online_dir, des_dir, time, call_back=None):
            u"""
            描述: 根据在线文件的目录, 下载指定时间后的文件
            调用: download_lastest(db, online_dir, des_dir, time, call_back=None)
                 --> db                       数据库 (str/unicode)
                 --> online_dir               在线文件的目录(str/unicode)   如: /big/shot/ep01
                 --> des_dir                  保存的目录(str/unicode) 
                 --> time                     下载的起始时间(str/unicode)   格式为: 2019-01-02 00:00:22
                 --> call_back                回调函数,用于计算进度, 默认为None
            返回: 成功返回List
            """
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            from twlib._media_file import _media_file

            if not isinstance(db, (str, unicode)) or not isinstance(online_dir, (str, unicode)) or not isinstance(
                    des_dir, (str, unicode)) or not isinstance(time, (str, unicode)):
                raise Exception(
                    "media_file.download_lastest argv error(str/unicode, str/unicode, str/unicode, str/unicode)")

            return _media_file.download_lastest(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, db, online_dir,
                                                des_dir, time, call_back)


if __name__ == "__main__":
    t_tw = tw("192.168.199.77", "admin", "shiming123")
    # print t_tw.get_version()
    # print t_tw.get_time()

    # ---------------client-----------------
    # 系统执行插件的读取的

    # ---------------login-----------------
    # print t_tw.login.account()
    # print t_tw.login.account_id()
    # print t_tw.login.token()
    # print t_tw.login.http_server_ip()
    # print t_tw.login.is_login()

    # ---------------status-----------------
    # print tw.status.get_status_and_color()

    # ---------------info-----------------
    # print t_tw.info.modules("proj_xiaoying")
    # print t_tw.info.fields("proj_xiaoying", "shot")
    # print t_tw.info.fields_and_str("proj_xiaoying", "shot")
    # t_id_list=t_tw.info.get_id("proj_xiaoying", "shot", [ ["eps.eps_name", "=", "e08"],["shot.shot", "=", "sc002"]])
    # print t_id_list
    # print t_tw.info.get("proj_xiaoying", "shot", t_id_list,  ["eps.eps_name", "shot.shot"])
    # print t_tw.info.get_dir("proj_xiaoying", "shot", t_id_list,  ["layout_work", "layout_approve"])
    # print t_tw.info.get_field_and_dir("proj_xiaoying", "shot",  t_id_list,  ["eps.eps_name", "shot.shot"], ["layout_work", "layout_approve"])
    # print t_tw.info.get_makedirs("proj_xiaoying", "shot", t_id_list)
    # print t_tw.info.get_sign_filebox("proj_xiaoying", "shot", t_id_list[0], "test_filebox_sign")
    # print t_tw.info.get_filebox("proj_xiaoying", "shot", t_id_list[0], u"2118B732-3D78-51F5-48CB-854AFC2C198F")
    # print t_tw.info.set("proj_xiaoying", "shot",  t_id_list,  {"shot.frame":"33"})
    # print t_tw.info.delete("proj_xiaoying", "shot", t_id_list)
    # print t_tw.info.create("proj_xiaoying", "shot", {"shot.shot":"sc003", "eps.eps_name":"e08"})
    # print t_tw.info.download_image("proj_xiaoying", "shot", t_id_list, "shot.image")
    # print t_tw.info.set_image("proj_xiaoying", "shot", t_id_list, "shot.image", u"g:/Sc08.gif")
    # print t_tw.info.count("proj_xiaoying", "shot", [  ["eps.eps_name", "=", "EP01"] ])
    # print t_tw.info.distinct("proj_xiaoying", "shot", [], "eps.eps_name", ["eps.eps_name"])
    # print t_tw.info.group_count("proj_xiaoying", "shot", ["eps.eps_name"], [ ["eps.eps_name", "in", ["EP01", "EP02"]  ] ])

    # ---------------task-----------------
    # print t_tw.task.modules("proj_xiaoying")
    # print t_tw.task.fields("proj_xiaoying", "shot")
    # print t_tw.task.fields_and_str("proj_xiaoying", "shot")
    # t_id_list=t_tw.task.get_id("proj_xiaoying", "shot", [ ["eps.eps_name", "=", "e08"],["shot.shot", "=", "sc002"]])
    # print t_id_list
    # print t_tw.task.get("proj_xiaoying", "shot", t_id_list,  ["eps.eps_name", "shot.shot"])
    # print t_tw.task.get_dir("proj_xiaoying", "shot", t_id_list,  ["layout_work", "layout_approve"])
    # print t_tw.task.get_field_and_dir("proj_xiaoying", "shot",  t_id_list,  ["eps.eps_name", "shot.shot"], ["layout_work", "layout_approve"])
    # print t_tw.task.get_makedirs("proj_xiaoying", "shot", t_id_list)
    # print t_tw.task.get_submit_filebox("proj_xiaoying", "shot", t_id_list[0])
    # print t_tw.task.get_sign_filebox("proj_xiaoying", "shot", t_id_list[0], "maya_playblast")
    # print t_tw.task.get_filebox("proj_xiaoying", "shot", t_id_list[0], u"67B9A8CF-9DAE-8E05-342E-9E44C69976C2")
    # print t_tw.task.set("proj_xiaoying", "shot",  t_id_list,  {"task.start_date":"2018-02-02"})
    # print t_tw.task.delete("proj_xiaoying", "shot", t_id_list)
    # print t_tw.task.create("proj_xiaoying", "shot", "4E027BE9-2FEA-B65B-1EA2-B0E126BD9A3E", "3429200E-6801-4FD8-A742-8F2767674FB2", "Layout", "1110c3da-3444-4f37-a7fa-04846da3c879")
    # print t_tw.task.download_image("proj_xiaoying", "shot", t_id_list, "task.image")
    # print t_tw.task.set_image("proj_xiaoying", "shot", t_id_list, "task.image", u"g:/Sc07.gif")
    # print t_tw.task.count("proj_xiaoying", "shot", [  ["eps.eps_name", "=", "EP01"] ])
    # print t_tw.task.distinct("proj_xiaoying", "shot", [], "eps.eps_name", ["eps.eps_name"])
    # print t_tw.task.assign("proj_xiaoying", "shot", t_id_list, "87db8934-e479-4f00-89a7-5a59df0d9130")
    # print t_tw.task.submit("proj_xiaoying", "shot", t_id_list[0], [u"g:/Sc07.gif"], u"submit png")
    # print t_tw.task.update_flow("proj_xiaoying", "shot", t_id_list[0], "task.director_status","Approve", u"Retake note data", [r"g:/Sc07.gif"])
    # print t_tw.task.group_count("proj_xiaoying", "shot", ["task.pipeline"], [ ["task.status", "=", "Approve" ] ])

    # ---------------note-----------------
    # print t_tw.note.fields()
    # t_id_list=t_tw.note.get_id("proj_xiaoying", [ ["module","=", "shot"], ["module_type","=", "task"] ])
    # print t_id_list
    # print t_tw.note.get("proj_xiaoying", t_id_list, ["#id", "text"])
    # print t_tw.note.create("proj_xiaoying", "shot", "task", ["45FAD4C7-1FBE-E4A1-45F1-472F08183D43"], "test note", "",[r"g:/Sc07.gif"])

    # --------------filebox---------------
    # print t_tw.filebox.fields()
    # t_id_list=t_tw.filebox.get_id("proj_xiaoying", [ ["#pipeline_id", "=", "3429200E-6801-4FD8-A742-8F2767674FB2"] ])
    # print t_id_list
    # print t_tw.filebox.get("proj_xiaoying", t_id_list, ["title", "#id"])

    # --------------field---------------
    # print t_tw.field.type()
    # print t_tw.field.create("proj_xiaoying", "shot", "info", u"测数据", u"test_data_a", "test_data_a", "int")

    # ---------------plugin------------------
    # print t_tw.plugin.fields()
    # t_id_list=t_tw.plugin.get_id([ ["type","=","menu"]])
    # print t_id_list
    # print t_tw.plugin.get(t_id_list, ["name", "argv"])
    # print t_tw.plugin.get_argvs(t_id_list[0])
    # print t_tw.plugin.set_argvs(t_id_list[0], {"ss" :"dd"})

    # ---------------pipeline------------------
    # print t_tw.pipeline.fields()
    # t_id_list=t_tw.pipeline.get_id("proj_xiaoying", [ ["module", "=", "shot"], ["module_type","=", "task"] ])
    # print t_id_list
    # print t_tw.pipeline.get("proj_xiaoying", t_id_list, ["entity_name"])

    # ---------------history------------------
    # print t_tw.history.fields()
    # t_id_list=t_tw.history.get_id("proj_xiaoying", [ ["module","=", "shot"], ["module_type", "=", "task"] ])
    # print t_id_list
    # print t_tw.history.get("proj_xiaoying", t_id_list, ["status", "text"])
    # print t_tw.history.count("proj_xiaoying", [ ["module","=", "shot"], ["module_type", "=", "task"] ])

    # ---------------link------------------
    # t_link_id_list=t_tw.info.get_id("proj_xiaoying", "asset", [["asset.asset_name", "has", "%"]])
    # t_id_list=t_tw.task.get_id("proj_xiaoying", "shot", [ ["eps.eps_name", "has", "e08"]])
    # print t_tw.link.get_asset("proj_xiaoying", "shot", "task", t_id_list[0])
    # print t_tw.link.link_asset("proj_xiaoying", "shot", "task", t_id_list, t_link_id_list)
    # print t_tw.link.unlink_asset("proj_xiaoying", "shot", "task", t_id_list, t_link_id_list)

    # ---------------software------------------
    # print t_tw.software.types()
    # print t_tw.software.get_path("proj_xiaoying", "hiero")
    # print t_tw.software.get_with_type("proj_xiaoying", "nuke")

    # ---------------api_data------------------
    # print t_tw.api_data.set("proj_xiaoying", "test", "data")
    # print t_tw.api_data.get("proj_xiaoying", "test")

    # ---------------version------------------
    # print t_tw.version.fields()
    # t_id_list=t_tw.version.get_id("proj_xiaoying", [])
    # print t_id_list
    # print t_tw.version.get("proj_xiaoying", t_id_list, ["#id", "filename"])
    # print t_tw.version.create("proj_xiaoying", u"E2083F3E-BF64-C3BA-79CE-DB5734A7BFB9", "v1", [u"z:/test.png"], ["/web/test.png"], "work")

    # ---------------link_entity------------------
    # print t_tw.link_entity.fields()
    # print t_tw.link_entity.get_name("proj_xiaoying", u"E2083F3E-BF64-C3BA-79CE-DB5734A7BFB9")
    # print t_tw.link_entity.get("proj_xiaoying", [ ["module", "=", "shot"], ["module_type", "=", "task"] ])

    # ---------------timelog------------------
    # print t_tw.timelog.fields()
    # t_id_list=t_tw.timelog.get_id("proj_xiaoying", [ ["module", "=", "shot"], ["module_type", "=", "task"] ])
    # print t_id_list
    # print t_tw.timelog.get("proj_xiaoying", t_id_list, ["#id", "use_time", "date", "create_by"], "5000",["date"])
    # print t_tw.timelog.create("proj_xiaoying", "E2083F3E-BF64-C3BA-79CE-DB5734A7BFB9", "shot", "task", "01:20", "2018-06-20", u"test data")
    # print t_tw.timelog.set_one("proj_xiaoying", "FCF07F64-26E7-9360-0BBD-6F25E71F652E", {"text": "test again data2"})

    # -------------------flow---------------------
    # t_pipeline_id_list=t_tw.pipeline.get_id("proj_xiaoying", [ ["module", "=", "shot"], ["module_type","=", "task"] ])
    # print t_tw.flow.get_data("proj_xiaoying", t_pipeline_id_list)

    # ------------------media_file---------------
    # t_id_list=t_tw.task.get_id("proj_xiaoying", "shot", [ ["eps.eps_name", "=", "e08"],["shot.shot", "=", "sc002"], ["task.task_name", "=", "Animation"]])
    # t_filebox_dict=t_tw.task.get_sign_filebox("proj_xiaoying", "shot", t_id_list[0], "maya_work")
    # print t_id_list
    # print t_filebox_dict
    # t_filebox_id=t_filebox_dict["#id"]
    # print t_filebox_id
    # print t_tw.media_file.download("proj_xiaoying", "shot", "task", t_id_list[0], t_filebox_id, True)
    # print t_tw.media_file.upload("proj_xiaoying", "shot", "task", t_id_list[0], t_filebox_id , [u'g:/Sc07.gif'])
    # print t_tw.media_file.download_path("proj_xiaoying", ["/xiaoying/Shot_work/Animation/e08/sc002/work/v003.mov"], ["d:/v003.mov"])
    # print t_tw.media_file.upload_path("proj_xiaoying", ["g:/Sc07.gif"], ["/xiaoying/Shot_work/Animation/e08/sc002/work/v003.mov"])
    # print t_tw.media_file.download_lastest("proj_shiming", "/ShiMing/Shot_work/Layout/EP01", "F:/test", "2019-05-31 00:00:00")
