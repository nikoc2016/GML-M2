# coding: utf-8
import os,sys

class _proxy:
    
    @staticmethod
    def set_proxy(a_cgtw_session, a_ip, a_bin_path):
	try:
	    proxy_path=a_bin_path+"/base/proxy/proxy.py"
	    if os.path.exists(proxy_path):
		if os.path.dirname(proxy_path) not in sys.path:
		    sys.path.append(os.path.dirname(proxy_path))
    
		from proxy import proxy
		t_proxy_dict=proxy().get_proxy(a_ip)
		if t_proxy_dict!={}:
		    a_cgtw_session.proxies = t_proxy_dict                                
	except:
	    pass 
	
