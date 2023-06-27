# coding: utf-8
import os,sys,json
class _flow:
    
    @staticmethod
    def get_data(a_fun, a_db, a_pipeline_id_list):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_pipeline_id_list, list) :
            raise Exception("_flow.get_data argv error,  must be( str, list)")
        if len(a_pipeline_id_list)==0:
            return []
        return a_fun("c_flow", "get_with_pipeline_id", {"db":a_db, "pipeline_id_array":a_pipeline_id_list})
        