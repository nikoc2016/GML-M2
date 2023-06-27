# coding: utf-8
import os
import sys
import json
from CGT_PY3.twlib._lib import _lib
try:
    #from websocket import create_connection
    from CGT_PY3.websocket import *

except Exception as e:
    raise Exception("Import module( websocket) fail")


class _con_local:

    @staticmethod
    def send_http(T_module, T_database, T_action,  T_other_data_dict, T_type="send"):
        T_tw_ws = ""
        T_result = ""

        # 修正连接houdini17有问题-----------
        try:
            if _lib.get_os() == "win":
                import socket
                if hasattr(socket, "TCP_KEEPCNT"):
                    DEFAULT_SOCKET_OPTION.pop()
                if hasattr(socket, "TCP_KEEPINTVL"):
                    DEFAULT_SOCKET_OPTION.pop()
        except Exception as e:
            pass
        # 修正连接houdini17有问题-----------

        try:
            T_tw_ws = create_connection("ws://127.0.0.1:64998")
        except Exception as   e:
            raise Exception("_con_local.send_http,  Cgteamwork client is not login \n" + getattr(e, 'message', repr(e)))
        try:
            new_data_dict = dict({"module": T_module, "database": T_database, "action": T_action}.items()+T_other_data_dict.items())
            T_tw_ws.send("#@start@#"+json.dumps({"data": new_data_dict, "name": "python",  "type": T_type})+"#@end@#")
        except Exception as   e:
            raise Exception("_con_local.send_http, send data to cgteamwork fail \n" + getattr(e, 'message', repr(e)))
        else:
            if isinstance(T_type, (unicode, str)) and unicode(T_type).strip().lower() == "get":
                try:
                    T_recv = T_tw_ws.recv()
                    T_tw_ws.close()
                except Exception as   e:
                    raise Exception("_con_local.send_http, get data from (127.0.0.1) fail \n" + getattr(e, 'message', repr(e)))
                else:
                    T_dict_data = json.loads(T_recv)
                    if type(T_dict_data) != dict:
                        raise Exception(T_recv)
                    else:
                        if T_dict_data.has_key('data') == False:
                            raise Exception(T_recv)
                        else:
                            return _lib.decode(T_dict_data["data"])
            else:
                return True

    @staticmethod
    def send_socket(T_sign, T_method, T_data, T_type="get"):
        T_tw_ws = ""
        T_result = ""

        # 修正连接houdini17有问题-----------
        try:
            if _lib.get_os() == "win":
                import socket
                if hasattr(socket, "TCP_KEEPCNT"):
                    DEFAULT_SOCKET_OPTION.pop()
                if hasattr(socket, "TCP_KEEPINTVL"):
                    DEFAULT_SOCKET_OPTION.pop()
        except Exception as e:
            pass
        # 修正连接houdini17有问题-----------

        try:
            T_tw_ws = create_connection("ws://127.0.0.1:64999")
        except Exception as   e:
            raise Exception("_con_local.send_socket, Cgteamwork client is not login, error:"+str(e))
        try:
            T_tw_ws.send(json.dumps(dict({"sign": T_sign, "method": T_method, "type": T_type}.items()+T_data.items())))
        except Exception as   e:
            raise Exception(e)
        else:
            try:
                T_recv = T_tw_ws.recv()
                T_tw_ws.close()
            except Exception as   e:
                raise Exception(e)
            else:
                try:
                    T_dict_data = json.loads(T_recv)
                except Exception as   e:
                    raise Exception(e)
                else:
                    if type(T_dict_data) != dict:
                        raise Exception(T_recv)
                    else:
                        if T_dict_data.has_key('data') == False or T_dict_data.has_key('code') == False:
                            raise Exception(T_recv)
                        else:
                            if T_dict_data['code'] == '0':
                                raise Exception(T_dict_data['data'])
                            return _lib.decode(T_dict_data["data"])
