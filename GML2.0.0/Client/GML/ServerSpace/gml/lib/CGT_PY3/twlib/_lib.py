# coding: utf-8
import os, sys, json
import platform
import uuid
import time
import hashlib

from past.types import unicode


class _lib:

    @staticmethod
    def is_json(value):
        try:
            eval(value)
        except Exception as e:
            pass
            return False
        else:
            return True

    @staticmethod
    def decode(value):  # json_decode
        if _lib.is_json(value):
            return json.loads(value)
        else:
            return value

    @staticmethod
    def encode(value):  # json_encode
        if isinstance(value, dict):
            try:
                json_str = json.dumps(value)
                return json_str
            except Exception as e:
                raise Exception(e)
        else:
            return False

    @staticmethod
    def format_data_to_dict(a_data_list, a_sign_list):  # 返回值为单层array, 用于get_one
        if isinstance(a_data_list, list) == False or isinstance(a_sign_list, list) == False:
            raise Exception("_lib.format_data_to_dict argv error, format_data_to_dict(list, list)")
        if len(a_data_list) != len(a_sign_list):
            raise Exception(
                "_lib.format_data_to_dict data error , (a_data_list's length is not equal to a_sign_list's)")
        t_result_dict = {}
        n = len(a_data_list) - 1
        for i in range(len(a_data_list)):
            t_sign = a_sign_list[i].replace("#", "")
            if i == n and ".id" in a_sign_list[i]:
                t_sign = a_sign_list[i].split(".")[-1].strip()
            t_result_dict[t_sign] = a_data_list[i]
        return t_result_dict

    @staticmethod
    def format_data(a_data_list, a_sign_list):  # 多层
        if isinstance(a_data_list, list) == False or isinstance(a_sign_list, list) == False:
            raise Exception("_lib.format_data argv error, format_data(list, list)")
        t_result_array = []
        for data in a_data_list:
            t_tmp_dict = _lib.format_data_to_dict(data, a_sign_list)
            if t_tmp_dict == False:
                raise Exception("_lib.format_data data error")
            t_result_array.append(t_tmp_dict)
        return t_result_array

    @staticmethod
    def get_os():
        t_os = platform.system().lower()
        if t_os == "windows":
            return "win"
        elif t_os == "linux":
            return "linux"
        elif t_os == "darwin":
            return "mac"
        else:
            return ""

    @staticmethod
    def uuid():
        return unicode(uuid.uuid4())

    @staticmethod
    def now(a_format='%Y-%m-%d %H:%M:%S'):
        '''
	描述: 取当前时间
	返回: 字符串
	'''
        t_time = ""
        try:
            t_time = time.strftime(a_format, time.localtime(time.time()))
        except Exception as e:
            pass
        return t_time

    @staticmethod
    def get_tmp_path():
        '''
	描述: 取temp路径
	返回: 字符串
	'''
        if _lib.get_os() == 'win':
            return os.environ["TMP"]
        else:
            return "/tmp"

    @staticmethod
    def get_text_md5(a_text):
        '''
	描述: 取文本md5
	调用: get_text_md5(a_text)
	      --> a_string为str/unicode
	返回: 字符串
	'''

        if not isinstance(a_text, (str, unicode)):
            raise Exception("a_text is str/unicode")
        md5 = hashlib.md5()
        if _lib.__is_utf8(a_text):
            a_text = a_text.encode('unicode-escape').decode('string_escape')  # unicode转str
        else:
            try:
                a_text = a_text.encode('unicode-escape').decode('string_escape')  # unicode转str
            except:
                pass

        md5.update(a_text)
        return md5.hexdigest()

        # --------------------------私有----------------------------------

    @staticmethod
    def __is_utf8(a_data):
        try:
            unicode(a_data).encode('gb2312')  # 执行失败为带有中文的str
        except:
            return False
        else:
            return True
