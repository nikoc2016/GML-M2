import json
import os
import datetime
import traceback

from GML_Runtime import GMLRuntime
from LegacySupport.Legacy_Runtime import LegacyRuntime
from NikoKit.NikoStd.NKPrint import eprint


def save_mydoc_login_file():
    mydoc_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'GML-1M')
    mydoc_loginStatus_path = os.path.join(mydoc_dir, 'login_status.json')
    lock_name = "GML.lock"
    lock_path = os.path.join(mydoc_dir, lock_name)
    try:
        LegacyRuntime.gml_lock_handle = open(lock_path, "w")
    except:
        eprint("GML-Connector-Legacy Lock failure")
        eprint(traceback.format_exc())

    try:
        available_project = eval(GMLRuntime.Data.current_user.user_cgt_available_projects)
    except:
        available_project = []

    login_status = {
        "username": GMLRuntime.Data.current_user.user_cgt_account,
        "tw_selected_project": GMLRuntime.Data.current_proj,
        "tw_username": GMLRuntime.Data.current_user.user_last_name + GMLRuntime.Data.current_user.user_first_name,
        "tw_available_projects": available_project,
        "tw_password": GMLRuntime.Data.current_user.user_cgt_password,
        "last_updated_timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "gml_2_legacy_support_generated": True,
    }

    try:
        with open(mydoc_loginStatus_path, "w", encoding="utf-8") as f:
            json.dump(login_status, f, indent=2, ensure_ascii=False)
    except:
        pass
