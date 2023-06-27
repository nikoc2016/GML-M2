# coding: utf-8

import os
import sys
import json


# try:
# import requests

# except Exception, e:
# raise Exception("Import module( requests) fail")

class _con:

    @staticmethod
    def get_server_ip(a_request_session, a_http_server):
        # 说明填写时cgtw的二级域名
        if a_http_server.find(".cgteamwork.com") != -1:
            try:
                res = a_request_session.get(
                    "http://update.cgteamwork.com:60000/index.php?controller=c_lic&method=get_ddns_ip&ddns_name=" + a_http_server,
                    timeout=20)
                ip = res.text
                if ip != "":
                    if unicode(a_http_server).find(":") == -1:
                        return ip
                    else:
                        lis = unicode(a_http_server).split(":")
                        return ip + ":" + lis[1]
            except Exception, e:
                pass
        return a_http_server

    @staticmethod
    def send(a_request_session, a_http_server, a_token, a_controller, a_method, a_data_dict):
        try:
            a_data_dict["controller"] = a_controller
            a_data_dict["method"] = a_method
            t_post_data = {"data": json.dumps(a_data_dict)}
            req_headers = {"cookie": "token=" + a_token}
            res = a_request_session.post("http://" + a_http_server + "/api.php", data=t_post_data, headers=req_headers)
        except Exception, e:
            raise Exception("_con.send, post data timeout")
        else:
            try:
                T_dict_data = json.loads(res.text)
            except Exception, e:
                raise Exception(e)
            else:
                if type(T_dict_data) != dict:
                    raise Exception(res)
                else:
                    if T_dict_data.has_key('data') == False or T_dict_data.has_key(
                            'code') == False or T_dict_data.has_key('type') == False:
                        raise Exception(res)
                    else:
                        if T_dict_data['code'] == '0' and T_dict_data['type'] == 'msg':
                            raise Exception(T_dict_data['data'])
                        return T_dict_data["data"]
