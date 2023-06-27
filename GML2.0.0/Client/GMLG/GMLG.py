import argparse
import codecs
import locale
import os
import subprocess
import threading
import traceback
from time import sleep

import yaml

from NikoKit.NikoLib import NKFileSystem
from NikoKit.NikoLib.NKDatabase import NKMySQLConnector
from NikoKit.NikoLib.NKGuard import NKGuard
from NikoKit.NikoLib.NKLogger import NKLogger
from NikoKit.NikoLib.NKRoboCopy import NKRoboCopy
from NikoKit.NikoStd import NKLaunch, NKConst
from NikoKit.NikoStd.NKConfig import NKConfig

import os.path as p
import sys

from NikoKit.NikoStd.NKPrint import tprint, eprint
from NikoKit.NikoStd.NKVersion import NKVersion


class GMLDBConnector(NKMySQLConnector):
    def __init__(self, host):
        super(GMLDBConnector, self).__init__(
            {
                'user': 'GML',
                'password': 'GML_PASSWD',
                'host': host,
                'database': 'GMLauncher',
                'charset': "gbk",
                'collation': "gbk_chinese_ci"
            }
        )


class GuardRuntime:
    config = None
    logger = None
    compiled = False
    my_dir = ""
    my_file_name = ""
    my_file_ext = ""
    gml_exe_file = "GML.exe"
    gml_guard_exe_file = "GMLG.exe"
    old_postfix = "_OLD"
    update_thread = None
    nk_guard = None


def connect_to_smb_share(host):
    print("Mounting SMB Share...")
    process = subprocess.Popen(fr"net use \\{host} /user:normal normal",
                               creationflags=subprocess.CREATE_NO_WINDOW,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE
                               )

    while process.poll() is None:
        new_line = process.stdout.readline().decode(codecs.lookup(locale.getpreferredencoding()).name)
        if new_line.strip():
            print(new_line)
    print("Mounting SMB Share Finished")


def main():
    # Get Basic Info
    if getattr(sys, 'frozen', False):
        GuardRuntime.compiled = True
        GuardRuntime.my_dir = p.dirname(sys.executable)
        GuardRuntime.my_file_name = p.splitext(p.basename(sys.executable))[0]
        GuardRuntime.my_file_ext = p.splitext(p.basename(sys.executable))[1]
    else:
        GuardRuntime.compiled = False
        GuardRuntime.my_dir = p.dirname(p.abspath(__file__))
        GuardRuntime.my_file_name = p.splitext(p.basename(__file__))[0]
        GuardRuntime.my_file_ext = p.splitext(p.basename(__file__))[1]

    # Default Config
    GuardRuntime.config = NKConfig(
        log_dir=p.join(GuardRuntime.my_dir, "GMLG_LOGS"),
        gml_pid=0,
        gml_version="0.0.0",
        config_yaml_path=p.join(GuardRuntime.my_dir, GuardRuntime.my_file_name + ".yaml"),
        gml_server_host="10.10.20.4",
    )

    # Init Logger
    GuardRuntime.logger = NKLogger(log_dir=GuardRuntime.config.log_dir)

    # YAML Config
    GuardRuntime.config.patch_yaml_config(yaml_path=GuardRuntime.config.config_yaml_path,
                                          silent_mode=True)

    # Arg Config
    parser = argparse.ArgumentParser()
    GuardRuntime.config.configure_parser(parser)
    GuardRuntime.config.patch_from_parser(parser)

    # SMB Share
    connect_to_smb_share(host=GuardRuntime.config.gml_server_host)

    # Convert Version
    GuardRuntime.config.gml_version = NKVersion(GuardRuntime.config.gml_version)

    # Update Log File
    GuardRuntime.logger.log_dir = GuardRuntime.config.log_dir

    # Run Update
    GuardRuntime.update_thread = UpdateThread(gml_server_host=GuardRuntime.config.gml_server_host)
    GuardRuntime.update_thread.launch()

    # Run NKGuard
    GuardRuntime.nk_guard = NKGuard(auto_quit=True)
    if GuardRuntime.config.gml_pid:
        GuardRuntime.nk_guard.protect(pid=GuardRuntime.config.gml_pid, launcher=gml_closed_handler)
        GuardRuntime.nk_guard.launch()


def gml_closed_handler():
    tprint("Guard::GML shutdown accidentally, relaunching target.")
    GuardRuntime.update_thread.stop()
    kill_gml()
    launch_gml()


def kill_gml():
    # Shutdown GML
    kill_proc = NKLaunch.run_pipe(command=r"taskkill /im GML.exe /f")
    while kill_proc.poll() is None:
        new_line = kill_proc.stdout.readline().decode(NKConst.SYS_CHARSET)
        tprint(f"KillGML::{new_line.replace(os.linesep, '')}")


def launch_gml():
    NKLaunch.run(command=[p.join(GuardRuntime.my_dir, GuardRuntime.gml_exe_file), "--secret"],
                 display_mode=NKLaunch.DISPLAY_MODE_NORMAL)


def update_gml(file_paths):
    my_dir = GuardRuntime.my_dir
    GML = GuardRuntime.gml_exe_file
    GML_OLD = GuardRuntime.gml_exe_file + GuardRuntime.old_postfix
    GMLG = GuardRuntime.gml_guard_exe_file
    GMLG_OLD = GuardRuntime.gml_guard_exe_file + GuardRuntime.old_postfix

    # Make Space for Update
    NKFileSystem.delete_try(p.join(my_dir, GML_OLD))
    NKFileSystem.delete_try(p.join(my_dir, GMLG_OLD))
    try:
        os.rename(p.join(my_dir, GML), p.join(my_dir, GML_OLD))
    except Exception as e:
        eprint(f"RenameOld::{e}")
    try:
        os.rename(p.join(my_dir, GMLG), p.join(my_dir, GMLG_OLD))
    except Exception as e:
        eprint(f"RenameOld::{e}")

    # Downloading New Version
    tprint("NKRoboCopying")
    for file_path in file_paths:
        result = NKRoboCopy.copy_file_to_dir(source_path=file_path, target_dir=my_dir, silent_mode=True)
        tprint(f"NKRoboCopy::{file_path}->{my_dir}::Result({result})")


class UpdateThread(threading.Thread):
    def __init__(self, gml_server_host):
        super(UpdateThread, self).__init__()
        self.stop_flag = False
        self.gml_server_host = gml_server_host

    def launch(self, silent_mode=False):
        if not silent_mode:
            tprint("Update::UpdateThread Started")
        self.start()

    def stop(self, silent_mode=False):
        try:
            self.stop_flag = True
        except:
            pass
        if not silent_mode:
            tprint("Update::UpdateThread Stopped")

    def run(self):
        tprint("Update::Checking...")
        while not self.stop_flag:
            upgrade_obj = None

            try:
                conn = GMLDBConnector(host=self.gml_server_host)
                result, error = conn.query(sql_line="SELECT * FROM UpdateInfo")
                upgrade_obj = {}
                for record in result:
                    upgrade_obj[record["update_field"]] = record["update_value"]
                print(upgrade_obj)
            except:
                eprint(traceback.format_exc())

            if upgrade_obj:
                current_version = GuardRuntime.config.gml_version
                latest_version = NKVersion(upgrade_obj["latest_version"])
                if latest_version > current_version:
                    self.stop_flag = True
                    GuardRuntime.nk_guard.stop(join=False)
                    kill_gml()
                    tprint(f"Update::New Version Found, Current Version V{current_version}, "
                           f"Remote Version V{latest_version}")
                    tprint(f"Update::Start Updating.")
                    update_gml(file_paths=[upgrade_obj["exe_path_gml"], upgrade_obj["exe_path_gml_guard"]])
                    tprint(f"Update::Launching new GML.")
                    launch_gml()

            for i in range(100):
                if not self.stop_flag:
                    sleep(0.1)
                else:
                    break

        tprint("Update::End Check")


if __name__ == "__main__":
    main()
