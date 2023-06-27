# coding: utf-8
import os,sys,json
from _lib import _lib
import types
class _media_file:
    
    

    @staticmethod    
    def download(a_fun, a_http_ip, a_cgtw_path, a_token, a_db, a_module, a_module_type, a_task_id, a_filebox_id, a_is_download_all, a_is_show_exist, a_des_dir="", a_call_back=None): #--20190122 a_des_dir
        if not isinstance(a_http_ip, (str, unicode)) or not isinstance(a_cgtw_path, (str, unicode)) or not isinstance(a_token, (str, unicode)) \
           or not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode))  or not isinstance(a_module_type, (str, unicode)) \
           or not isinstance(a_task_id, (str, unicode)) or not isinstance(a_filebox_id, (str, unicode)) or not isinstance(a_task_id, (str, unicode)) \
           or not isinstance(a_filebox_id, (str, unicode)) or not isinstance(a_is_download_all, bool) or not isinstance(a_is_show_exist, bool) or not isinstance(a_des_dir,(str,unicode)): #--20190122 a_des_dir
            raise Exception("media_file.download argv error(str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, bool, bool, str/unicode)") #--20190122 a_des_dir
        

        t_operation_files = operation_files(a_cgtw_path, a_http_ip, a_token)
        return t_operation_files.download(a_fun, a_db, a_module, a_module_type, a_task_id, a_filebox_id, a_is_download_all, a_is_show_exist, a_des_dir,  a_call_back)

   

    @staticmethod    
    def upload(a_fun, a_http_ip, a_cgtw_path, a_token, a_db, a_module, a_module_type, a_task_id, a_filebox_id, a_sou_path_list, a_version_id="", a_call_back=None):
        if not isinstance(a_http_ip, (str, unicode)) or not isinstance(a_cgtw_path, (str, unicode)) or not isinstance(a_token, (str, unicode)) \
           or not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode))  or not isinstance(a_module_type, (str, unicode)) \
           or not isinstance(a_task_id, (str, unicode)) or not isinstance(a_filebox_id, (str, unicode)) or not isinstance(a_task_id, (str, unicode)) \
           or not isinstance(a_filebox_id, (str, unicode)) or not isinstance(a_sou_path_list, list) or not isinstance(a_version_id, (str, unicode)):
            raise Exception("media_file.upload argv error(str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, list, str/unicode)")
        

        t_operation_files = operation_files(a_cgtw_path, a_http_ip, a_token)
        return t_operation_files.upload(a_fun, a_db, a_module, a_module_type, a_task_id, a_filebox_id, a_sou_path_list, a_version_id, a_call_back)


    
    @staticmethod
    def download_path(a_fun, a_http_ip, a_cgtw_path, a_token, a_db, a_online_path_list, a_des_path_list, a_call_back=None):
        if not isinstance(a_http_ip, (str, unicode)) or not isinstance(a_cgtw_path, (str, unicode)) or not isinstance(a_token, (str, unicode)) \
                or not isinstance(a_db, (str, unicode)) or not isinstance(a_online_path_list, list) or not isinstance(a_des_path_list, list):  # --20190122 a_des_dir
            raise Exception("media_file.download_path argv error(str/unicode, str/unicode, str/unicode, str/unicode, list, list)")  # --20190122 a_des_dir

        if len(a_online_path_list) != len(a_des_path_list):
            raise Exception("media_file.download_path the number of source and destination paths does not match")  # --20190122 a_des_dir

        

        t_operation_files = operation_files(a_cgtw_path, a_http_ip, a_token)
        return t_operation_files.download_path(a_fun, a_db, a_online_path_list, a_des_path_list, a_call_back)




    @staticmethod
    def upload_path(a_fun, a_http_ip, a_cgtw_path, a_token, a_db, a_sou_path_list, a_online_path_list, a_call_back=None, a_metadata = {}):
        if not isinstance(a_http_ip, (str, unicode)) or not isinstance(a_cgtw_path, (str, unicode)) or not isinstance(a_token, (str, unicode)) \
                or not isinstance(a_db, (str, unicode)) or not isinstance(a_sou_path_list, list) or not isinstance(a_online_path_list, list) \
                or not isinstance(a_metadata,dict):
            raise Exception("media_file.upload_path argv error(str/unicode, str/unicode, str/unicode, str/unicode, list, list, dict)")

        if len(a_sou_path_list) != len(a_online_path_list):
            raise Exception("media_file.upload_path the number of source and destination paths does not match)")  # --20190122 a_des_dir


        t_operation_files = operation_files(a_cgtw_path, a_http_ip, a_token)
        return t_operation_files.upload_path(a_fun,a_db, a_sou_path_list, a_online_path_list, a_metadata, a_call_back)

    
    @staticmethod
    def download_lastest(a_fun, a_http_ip, a_cgtw_path, a_token, a_db,  a_online_dir, a_des_dir, a_time, a_call_back=None):
        if not isinstance(a_http_ip, (str, unicode)) or not isinstance(a_cgtw_path, (str, unicode)) or not isinstance(a_token, (str, unicode)) \
                or not isinstance(a_db, (str, unicode)) or not isinstance(a_online_dir, (str, unicode)) or not isinstance(a_des_dir, (str, unicode)) or not isinstance(a_time, (str, unicode)) :  
            raise Exception("media_file.download_lastest argv error(str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, str/unicode, str/unicode)") 

        t_operation_files = operation_files(a_cgtw_path, a_http_ip, a_token)
        return t_operation_files.download_lastest(a_fun, a_db, a_online_dir, a_des_dir, a_time, a_call_back)        
    
    #------------------------------私有-----------------------------------


class operation_files(object):
    m_total_size           = 0 #总大小
    m_already_perform_size = 0 #已执行大小
    def __init__(self, a_cgtw_path, a_http_ip, a_token):
        super(operation_files, self).__init__()
        t_ct_path=a_cgtw_path+"/ct"
        t_ct_path in sys.path or sys.path.append(t_ct_path)
        from ct_http import media_http 
        from ct_file import ct_file

        self.m_ct_file = ct_file()
        self.m_http    = media_http(a_http_ip, a_token)        
        self.m_os      = _lib.get_os()

    def download(self,a_fun, a_db, a_module, a_module_type, a_task_id, a_filebox_id, a_is_download_all, a_is_show_exist, a_des_dir="", a_call_back=None):
        self.m_call_back = a_call_back
        t_fail_list      = [] 
        t_all_list       = []
        t_download_list  = [] 
        t_is_all         = "Y"
        if not a_is_download_all:
            t_is_all = "N"
            
        #--计算文件总大小
        res = a_fun("c_media_file","get_filebox_bulk_download_data", {"db":a_db, "module":a_module, "module_type":a_module_type, "os":self.m_os, "is_all":t_is_all, "filebox_id":a_filebox_id, "task_id_array":[a_task_id]})
        for dic in res:
            t_current_folder_id = dic["current_folder_id"]
            t_data_list    = dic["data_list"]
            t_filebox_data = dic["filebox_data"]
            t_des_dir      = dic["des_dir"]
            t_server       = dic['server']   

            if a_des_dir.strip() != "":
                #--判断a_des_dir是否存在
                if not os.path.exists(a_des_dir):
                    try:
                        os.makedirs(a_des_dir)
                    except Exception,e:
                        raise Exception("media_file.download, makedirs fail:(%s)"%e.message)
                #--判断是否是目录
                if not os.path.isdir(a_des_dir):
                    raise Exception("media_file.download, des_dir is not dir")
                    
                #--替换目标路径
                if a_des_dir[-1] !='/': #--结尾必须是'/'      
                    a_des_dir += '/'
                t_des_dir = t_des_dir.replace(t_server, a_des_dir)                

            if isinstance(t_data_list, list):
                for t_dict_data in t_data_list:
                    if isinstance(t_dict_data, dict) and t_dict_data.has_key("id") and t_dict_data.has_key("name") and t_dict_data.has_key("is_folder"):                        
                        t_folder_id_list = []
                        t_file_id_list   = []               
                             
                        t_name = t_dict_data["name"]
                        t_uuid = _lib.uuid()
                        if unicode(t_dict_data["is_folder"]).strip().lower()=="y":
                            t_folder_id_list.append(t_dict_data["id"])
                        else:
                            t_file_id_list.append(t_dict_data["id"])
                        #再取详细的在线的数据
                        if len(t_folder_id_list)>0 or len(t_file_id_list)>0:

                            is_folder=False
                            if len(t_folder_id_list)>0:
                                is_folder=True

                            t_res=a_fun("c_media_file", "bulk_download", {"db":a_db, "id_array":t_file_id_list, "folder_id_array":t_folder_id_list, "current_folder_id":t_current_folder_id })
                            if isinstance(t_res, list):
                                for temp_dict in t_res:
                                    if isinstance(temp_dict, dict):
                                        if temp_dict.has_key("path") and temp_dict.has_key("id"):
                                            self.m_total_size += int(temp_dict['file_size'])
                                            t_download_list.append({"media_file_id":temp_dict["id"], "des":t_des_dir+"/"+unicode(temp_dict["path"]).strip("/"),'size':temp_dict['file_size'],'web_path':temp_dict['web_path'],'filebox_data':t_filebox_data,'is_folder':is_folder,'name':t_name,'uuid':t_uuid  })

        #开始下载
        if len(t_download_list)>0:
            t_last_uuid = "" #--
            for t_dic in t_download_list:
                t_media_file_id = t_dic["media_file_id"]
                t_des           = t_dic["des"]
                t_size          = t_dic['size']
                t_web_path      = t_dic['web_path'] #用于失败列表
                t_name          = t_dic['name']
                t_uuid          = t_dic['uuid']
                if t_uuid != t_last_uuid: #用于序列的文件夹备份,保证在同一个版本文件夹下
                    t_last_uuid = t_uuid
                    t_backup_replace_dir = ""
                    
                t_is_folder     = t_dic['is_folder']
                t_filebox_data  = t_dic['filebox_data']
                if not t_is_folder:
                    t_download_backup_path=self.__download_backup_path(t_des, t_filebox_data, t_name, _lib.now('%Y-%m-%d-%H-%M-%S'))
                else:
                    if t_backup_replace_dir=="":
                        t_download_backup_path=self.__download_backup_path(t_des, t_filebox_data, t_name, _lib.now('%Y-%m-%d-%H-%M-%S'))
                        t_backup_replace_dir=os.path.dirname(t_download_backup_path)
                    else:
                        t_download_backup_path=self.__download_backup_path(t_des, t_filebox_data, t_name, _lib.now('%Y-%m-%d-%H-%M-%S'), t_backup_replace_dir)
                t_temp_dict={}

                if self.m_http.download(a_db, t_media_file_id, t_des, self.__call_back, t_download_backup_path, t_temp_dict,):
                    self.m_already_perform_size += int(t_size) #-成功才计入 已下载大小
                    if a_is_show_exist:
                        t_all_list.append(t_des)
                    else:
                        #不显示已经存在的
                        if isinstance(t_temp_dict, dict) and t_temp_dict.has_key("exist") and t_temp_dict["exist"]:
                            continue
                        else:
                            t_all_list.append(t_des)
                else:#新的有返回false
                    t_fail_list.append(t_web_path)
                                                


        if t_fail_list != []:
            raise Exception("media_file.download download fail,"+json.dumps(t_fail_list))
        
        return t_all_list        
    
    def upload(self, a_fun, a_db, a_module, a_module_type, a_task_id, a_filebox_id, a_sou_path_list, a_version_id="", a_call_back=None):

        self.m_call_back = a_call_back
        filebox_dict=a_fun("c_file","filebox_get_one_with_id",{"db":a_db, "module":a_module,"module_type":a_module_type, "task_id":a_task_id, "os":self.m_os, "filebox_id":a_filebox_id})
        if not isinstance(filebox_dict, dict):
            raise Exception("media_file.upload get filebox data fail")
        else:
            if not filebox_dict.has_key("path") or not filebox_dict.has_key("server"):
                raise Exception("media_file.upload get filebox data fail")
        
        t_upload_dir=unicode(filebox_dict["path"]).replace(filebox_dict["server"], "/")
        t_new_upload_list=[]
        #遍历出所有的源文件
        for n in range(len(a_sou_path_list)):
            t_sou_path=a_sou_path_list[n]
            t_des_path=t_upload_dir+"/"+os.path.basename(t_sou_path)
            if os.path.isdir(t_sou_path):
                for i in self.m_ct_file.get_file_with_walk_folder(t_sou_path):
                    t_file_size=self.m_ct_file.get_size(i)
                    self.m_total_size += t_file_size
                    t_new_des_path=i.replace(t_sou_path, t_des_path)
                    t_new_des_path=unicode(t_new_des_path).replace("\\", "/")
                    t_new_upload_list.append({"sou":unicode(i).replace("\\", "/"), "des":t_new_des_path, "size":t_file_size})
            else:
                t_file_size=self.m_ct_file.get_size(t_sou_path)
                self.m_total_size += t_file_size
                t_new_upload_list.append({"sou":t_sou_path, "des":t_des_path, "size":t_file_size})
                
        #开始上传
        for i in range( len(t_new_upload_list) ):
            t_sou=t_new_upload_list[i]["sou"]
            t_des=t_new_upload_list[i]["des"]
            #检查文件是否在服务器
            t_md5=self.m_ct_file.get_md5(t_sou)            
            #t_session_id=_lib.uuid()
            t_session_id=t_md5
            
            t_file_size=t_new_upload_list[i]["size"]
            t_file_name=os.path.basename(t_des)
            t_file_modify_time=self.m_ct_file.get_modify_time(t_sou)        
            #再media_folder中创建记录,并取回folder_id
            try:
                t_folder_id=a_fun("c_media_file", "create_path_and_get_folder_id", {"db":a_db, "path":os.path.dirname(t_des)})                
            except:
                raise Exception("media_file.upload, create path and get folder id fail")
            

            try:
                exist_file_res=a_fun("c_media_file", "exist_file", {"db":a_db, "file_name":t_file_name, "folder_id":t_folder_id, "md5":t_md5})   
            except:
                raise Exception("media_file.upload, get exist file fail")
                     
            exist_file_dic=dict(exist_file_res)
            if not exist_file_dic.has_key("md5_path") and not exist_file_dic.has_key("is_exist_data"):
                raise Exception("media_file.upload, get exist file fail, not key (md5_path, is_exist_data)")
            
            is_exist_data=unicode(exist_file_dic["is_exist_data"]).strip().lower()#数据库是否存在数据
            server_md5_path=unicode(exist_file_dic["md5_path"]).strip()
            new_server_md5_path=server_md5_path
            if server_md5_path=="":#服务器不存在这个文件
                try:
                    new_server_md5_path=self.m_http.upload(t_session_id, t_sou, a_db, t_file_name , t_md5, self.__call_back)   

                except Exception, e:
                    raise Exception(u"media_file.upload, "+e.message)
  
            self.m_already_perform_size += t_file_size #计入已下载大小
                
            #文件已经在服务器上。这个时候则需要插入数据
            if is_exist_data!="y" or server_md5_path=="":#不存在数据            
                try:
                    upload_res=a_fun("c_media_file", "upload", {"db":a_db, 
                                                                "file_name":t_file_name,
                                                                "version_id":a_version_id, 
                                                                "folder_id":t_folder_id, 
                                                                "md5":t_md5, 
                                                                "md5_path":new_server_md5_path, 
                                                                "sys_size":unicode(t_file_size), 
                                                                "sys_modify_time":t_file_modify_time, 
                                                                "is_cover":"Y",
                                                                "meta_data_array":{"task_id":a_task_id, "module":a_module, "module_type":a_module_type,} 
                                                                })  
                except Exception, e:
                    #print e.message
                    raise Exception(u"media_file.upload, upload data fail")
                
            else:
                #文件已经在服务器上。数据也存在的情况,
                #更改文件修改时间
                try:
                    update_modify_time_res=a_fun("c_media_file", "update_file_modify_time", {"db":a_db, "file_name":t_file_name, "folder_id":t_folder_id, "md5":t_md5, "file_modify_time":t_file_modify_time})
                except:
                    raise Exception(u"media_file.upload, update file_modify_time fail")                  
                
                
                #这个点要在version中的media_file的值
                try:
                    if unicode(a_version_id).strip()!="":
                        update_res=a_fun("c_media_file", "update_version_data", {"db":a_db, "file_name":t_file_name, "folder_id":t_folder_id, "md5":t_md5, "version_id":a_version_id})
                except:
                    raise Exception(u"media_file.upload, update version fail")
                    
        return True
        
    
    def download_path(self,a_fun, a_db, a_online_path_list, a_des_path_list, a_call_back):
        t_fail_list = []
        self.m_call_back = a_call_back

        #--获取在线文件对应信息
        t_online_file_list = a_fun('c_media_file','get_online_file_path_array',{'db':a_db,'path_array':a_online_path_list})  
        if len(t_online_file_list) != len(a_des_path_list): #获取在线文数量不正确 
            raise Exception("media_file.download_path Incorrect number of online files obtained,"+json.dumps(t_online_file_list))
        
        
        #--计算所有将下载文件的总大小
        for _online_file_dict in t_online_file_list:
            if isinstance(_online_file_dict, dict) and _online_file_dict.has_key('size'):
                self.m_total_size += int(_online_file_dict['size'])
        
        #--循环下载
        for index in range(len(t_online_file_list)):
            t_online_data   = t_online_file_list[index]
            t_media_file_id = t_online_data['id']
            t_sou           = t_online_data['path']
            t_size          = t_online_data['size']
            t_des           = a_des_path_list[index]

            try:
                if t_des.strip() == "" or t_media_file_id.strip() == "":
                    t_fail_list.append(t_sou)
                    self.m_already_perform_size += int(t_size)  #计算当前已经下载的所有大小 --->(成功的时候添加)  
                    continue
                
                t_name = os.path.basename(t_des)
                t_download_backup_path = self.__download_backup_path(t_des, {}, t_name, _lib.now('%Y-%m-%d-%H-%M-%S'))
                
                if not self.m_http.download(a_db, t_media_file_id, t_des, self.__call_back, t_download_backup_path):
                    t_fail_list.append(t_sou)
                else:    
                    self.m_already_perform_size += int(t_size)  #计算当前已经下载的所有大小 --->(成功的时候添加)  
                
            except Exception,e:
                t_fail_list.append(t_sou)

        if len(t_fail_list) > 0:
            raise Exception("media_file.download_path download fail,"+json.dumps(t_fail_list))
            
        return True

    
    def upload_path(self,a_fun, a_db, a_sou_path_list, a_online_path_list, a_metadata, a_call_back):
        
        self.m_call_back = a_call_back
        a_version_id = ""
        t_fail_list = []
              
        #--计算总文件大小
        t_new_sou_path_list = [] #新的原文件列表{'size':'','md5':'','modify_time':'','sou':''}
        for _file in a_sou_path_list: 
            if  _file.strip() == "" or not os.path.exists(_file):
                t_fail_list.append(_file)
                continue
            if not os.path.isfile(_file):
                t_fail_list.append(_file)
                continue
            t_file_size        = self.m_ct_file.get_size(_file)
            t_md5              = self.m_ct_file.get_md5(_file)
            t_file_modify_time = self.m_ct_file.get_modify_time(_file)
            self.m_total_size  += t_file_size
            t_new_sou_path_list.append({'size':t_file_size,'md5':t_md5,'modify_time':t_file_modify_time,'sou':_file})
        
        #--存在不是文件 或不存在 或空的 直接返回
        if len(t_fail_list) > 0:
            raise Exception("media_file.upload_path There are not file or not exists,please check,"+json.dumps(t_fail_list))
            
        
        for index in range(len(t_new_sou_path_list)):
            t_sou_data          = t_new_sou_path_list[index]
            t_sou               = t_sou_data['sou']
            t_file_modify_time  = t_sou_data['modify_time']
            t_md5               = t_sou_data['md5']
            t_file_size         = t_sou_data['size'] 
            t_des               = a_online_path_list[index]
            try:
                if t_des[0] != "/":
                    t_des = "/" + t_des

                t_session_id = t_md5
                t_file_name = os.path.basename(t_des)
    
                t_folder_id = a_fun("c_media_file", "create_path_and_get_folder_id", {"db":a_db, "path":os.path.dirname(t_des)})
    
                exist_file_res = a_fun("c_media_file", "exist_file", {"db": a_db, "file_name": t_file_name, "folder_id": t_folder_id, "md5": t_md5})
    
                exist_file_dic = dict(exist_file_res)

                if not exist_file_dic.has_key("md5_path") and not exist_file_dic.has_key("is_exist_data") and not exist_file_dic.has_key('id'):
                    t_fail_list.append(t_sou)
                    continue
                
                media_file_id         = exist_file_dic['id'].strip()
                is_exist_data   = unicode(exist_file_dic["is_exist_data"]).strip().lower()  # 数据库是否存在数据
                server_md5_path = unicode(exist_file_dic["md5_path"]).strip()
                new_server_md5_path = server_md5_path
                if server_md5_path == "":  # 服务器不存在这个文件
                    new_server_md5_path = self.m_http.upload(t_session_id, t_sou, a_db, t_file_name, t_md5, self.__call_back)
                    
                self.m_already_perform_size += t_file_size  #计入已下载大小
                # 文件已经在服务器上。这个时候则需要插入数据
                if is_exist_data != "y" or server_md5_path == "" or media_file_id == "":  # 不存在数据
                    upload_res = a_fun("c_media_file", "upload", {"db": a_db,
                                                                      "file_name": t_file_name,
                                                                      "version_id": a_version_id,
                                                                      "folder_id": t_folder_id,
                                                                      "md5": t_md5,
                                                                      "md5_path": new_server_md5_path,
                                                                      "sys_size": unicode(t_file_size),
                                                                      "sys_modify_time": t_file_modify_time,
                                                                      "is_cover": "Y",
                                                                      "meta_data_array": a_metadata
                                                                      })
                else:
                    if media_file_id != "" and a_metadata != {}:
                        a_fun('c_media_file','set_metadata',{'db':a_db,'id':media_file_id,'meta_data_array':a_metadata})
 
                    update_modify_time_res = a_fun("c_media_file", "update_file_modify_time", {"db": a_db, "file_name": t_file_name, "folder_id": t_folder_id, "md5": t_md5, "file_modify_time": t_file_modify_time})

            except Exception, e:
                t_fail_list.append(t_sou)
    
        if len(t_fail_list) > 0:
            raise Exception("media_file.upload_path upload fail,"+json.dumps(t_fail_list))
    
        return True            
        
    
    def download_lastest(self, a_fun, a_db, a_online_dir, a_des_dir, a_time, a_call_back):
        t_fail_list = []
        t_all_list  = []
        self.m_call_back = a_call_back
        a_online_dir=unicode(a_online_dir).rstrip("/").rstrip("\\")
        a_des_dir=unicode(a_des_dir).rstrip("/").rstrip("\\")
        filter_list=[ ["media_file.sys_create_time", ">", a_time] ]
        if unicode(a_online_dir).strip()=="":
            media_folder_id=""
        else:
            media_folder_id = a_fun('c_media_file','get_folder_id',{'db':a_db,'path':a_online_dir})
            if media_folder_id=="":
                raise Exception("media_file.download_lastest, online dir not exist")
            filter_list=filter_list+[ "and", "(",["#array_position(media_folder.all_p_id, '"+media_folder_id+"')", "!is", "null"], "or", ["#media_folder.id", "=", media_folder_id],")" ]
            
        #--获取在线文件对应信息
        t_online_file_list = a_fun('c_media_file','get_online_file_with_filter',{'db':a_db,'filter_array':filter_list})          
        
        #--计算所有将下载文件的总大小
        for _online_file_dict in t_online_file_list:
            if isinstance(_online_file_dict, dict) and _online_file_dict.has_key('size'):
                self.m_total_size += int(_online_file_dict['size'])
        

        #--循环下载
        for _online_file_dict in t_online_file_list:
            t_media_file_id = _online_file_dict['id']
            t_sou           = _online_file_dict['path']
            t_size          = _online_file_dict['size']
            t_des           = a_des_dir + unicode(_online_file_dict['path']).replace(a_online_dir, "")
            try:
                if t_des.strip() == "" or t_media_file_id.strip() == "":
                    t_fail_list.append(t_sou)
                    self.m_already_perform_size += int(t_size)  #计算当前已经下载的所有大小 --->(成功的时候添加)  
                    continue
                
                t_name = os.path.basename(t_des)
                t_download_backup_path = self.__download_backup_path(t_des, {}, t_name, _lib.now('%Y-%m-%d-%H-%M-%S'))
                t_temp_dict={}
                if not self.m_http.download(a_db, t_media_file_id, t_des, self.__call_back, t_download_backup_path, t_temp_dict):
                    t_fail_list.append(t_sou)
                else:    
                    self.m_already_perform_size += int(t_size)  #计算当前已经下载的所有大小 --->(成功的时候添加)  
                        #不显示已经存在的
                    if isinstance(t_temp_dict, dict) and t_temp_dict.has_key("exist") and t_temp_dict["exist"]:
                        continue
                    else:
                        t_all_list.append(t_des)  
                
            except Exception,e:
                t_fail_list.append(t_sou)

        if len(t_fail_list) > 0:
            raise Exception("media_file.download_lastest download fail,"+json.dumps(t_fail_list))
            
        return t_all_list    

    def __call_back(self, a,b,c):
        if self.m_call_back != None and (type(self.m_call_back)==types.FunctionType or type(self.m_call_back)==types.MethodType):
            self.m_call_back(self.m_already_perform_size+a, b, self.m_total_size)

    
    #---私有
    def __download_backup_path(self, a_des, a_filebox_data, a_name, a_time, a_replace_dir=""):
        #a_name有可能是文件夹名称/或者文件的名称
        #a_time: 2018-01-01-22-11-22
        t_time_no_char=unicode(a_time).replace("-", "") #a_time: 20180101221122
        base_name=os.path.basename(a_des)        
        lis=os.path.splitext(base_name)
        if len(lis)==2:
            backup_path=t_back_dir=os.path.dirname(a_des)+"/history/backup/"+lis[0]+"."+t_time_no_char+lis[1]
        else:
            backup_path=t_back_dir=os.path.dirname(a_des)+"/history/backup/"+base_name+"."+t_time_no_char
        if a_filebox_data.has_key("move_to_history")  and a_filebox_data.has_key("is_in_history_add_version")  and a_filebox_data.has_key("path") and a_filebox_data.has_key("is_in_history_add_datetime"):
            if unicode(a_filebox_data["move_to_history"]).lower()=="y":
                filebox_path=a_filebox_data["path"]
                #取文件框目录下层级的名称
                if a_replace_dir=="":
                    if unicode(a_filebox_data["is_in_history_add_datetime"]).lower()=="y":
                        des_path=filebox_path+"/history/"+a_time+"/"+a_name
                    else:
                        des_path=filebox_path+"/history/"+a_name
                    temp_des_file=des_path
                    if unicode(a_filebox_data["is_in_history_add_version"]).lower()=="y":
                        temp_des_file=self.__auto_add_version(des_path)                        
                else:
                    temp_des_file=a_replace_dir

                backup_path=unicode(a_des).replace(filebox_path+"/"+a_name, temp_des_file)
        return backup_path        
    
    
    def __auto_add_version(self, a_path):
        res=a_path
        temp=""
        size=0
        basename=os.path.basename(a_path)
        temp_list=os.path.splitext(basename)
        suf=unicode(temp_list[-1]).strip(".")
        if suf.strip()!="":
            #用isFile的话，如果文件不存在会不对
            cmp_basename=temp_list[0]
            t_dir=os.path.dirname(a_path)
            for i in range(10000):
                if i<100:
                    size=2
                elif i>=100 and i<1000:
                    size=3
                elif i>=1000 and i<10000:
                    size=4
                temp=t_dir+"/"+cmp_basename+"_v"+self.__start_add_zero(unicode(i+1), size)+"."+suf
                if not os.path.exists(temp):
                    res=temp
                    break
        else:
            absolute_path=a_path
            for i in range(10000):
                if i<100:
                    size=2
                elif i>=100 and i<1000:
                    size=3
                elif i>=1000 and i<10000:
                    size=4
                temp=absolute_path+"_v"+ self.__start_add_zero(unicode(i+1), size)
                if not os.path.exists(temp):
                    res=temp
                    break
        return res            



    
    def __start_add_zero(self, a_string, a_size=4):
        string=a_string
        temp=a_size-len(a_string)
        if temp>0:
            for i in range(temp):
                string="0"+string
        return string

    