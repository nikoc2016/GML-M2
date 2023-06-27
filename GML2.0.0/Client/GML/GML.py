import argparse
import codecs
import datetime
import getpass
import locale
import os
import subprocess
import sys
import traceback
import os.path as p

# DO NOT DELETE PyInstaller Hint
import schedule
import ast
import yaml
import wmi
import shiboken2
import html
import uuid
import json
import socketserver
import psutil
import errno
import mysql.connector
import ldap3
import past
import past.types
import six
import cgi
import http.cookies

# CONSTS
GML_VERSION = "2.0.2"
GML_PORT = 40000
GML_SERVER = "10.10.20.4"


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


def launch_gml():
    # GETTING BASIC ENVIRONMENT INFO
    if getattr(sys, 'frozen', False):
        compiled = True
        my_dir = p.dirname(sys.executable)
        my_file_name = p.splitext(p.basename(sys.executable))[0]
        my_file_ext = p.splitext(p.basename(sys.executable))[1]
    else:
        compiled = False
        my_dir = p.dirname(p.abspath(__file__))
        my_file_name = p.splitext(p.basename(__file__))[0]
        my_file_ext = p.splitext(p.basename(__file__))[1]

    # # DEV MODE
    # smb_dir = p.join(my_dir, "ServerSpace")

    # RELEASE MODE
    smb_dir = r"\\" + GML_SERVER
    connect_to_smb_share(host=GML_SERVER)

    # PYTHON PATH
    for import_dir in [p.join(smb_dir, "gml", "lib"),
                       p.join(smb_dir, "gml", "lib", "GML"),
                       p.join(smb_dir, "gml", "plugin")]:
        sys.path.append(import_dir)

    # CHECKING IF SERVER IS ONLINE
    try:
        import NikoKit
    except:
        print("Server Offline")
        with open(p.join(my_dir, "GML_SERVER_OFFLINE"), "w") as f:
            f.write(str(datetime.datetime.now()))
        return
    print("Server OK")

    # CONFIG GML RUNTIME + PRELOAD LOGGER
    from GML_Runtime import GMLRuntime
    from GML_Feature import Feature
    import GML_Database
    from GML_Language import GML_Language_pack
    from NikoKit.NikoLib.NKLogger import NKLogger
    GMLRuntime.App.compiled = compiled
    GMLRuntime.App.my_dir = my_dir
    GMLRuntime.App.my_file_name = my_file_name
    GMLRuntime.App.my_file_ext = my_file_ext
    GMLRuntime.App.server_ip = GML_SERVER
    GMLRuntime.Dir.config_dir = p.join(smb_dir, "gml", "config")
    GMLRuntime.Dir.plugin_dir = p.join(smb_dir, "gml", "plugin")
    GMLRuntime.Dir.lib_dir = [p.join(smb_dir, "gml", "lib")]
    GMLRuntime.Dir.release_dir = p.join(smb_dir, "gml", "release")
    GMLRuntime.Dir.icon_dir = p.join(smb_dir, "gml", "icon")
    if compiled:
        GMLRuntime.Dir.log_dir = p.join(smb_dir, "logs", getpass.getuser())
    GMLRuntime.Service.NKLogger = NKLogger(log_dir=GMLRuntime.Dir.log_dir)
    GMLRuntime.Database.AdConn = GML_Database.GVFActiveDirectory()
    GMLRuntime.Database.Conn = GML_Database.GMLDBConnector(host=GML_SERVER)
    GMLRuntime.Database.Create = GML_Database.Create
    GMLRuntime.Database.Update = GML_Database.Update
    GMLRuntime.Database.Retrieve = GML_Database.Retrieve
    GMLRuntime.Database.Delete = GML_Database.Delete
    GMLRuntime.Feature = Feature

    # PREVENT MULTI-INSTANCE
    from NikoKit.NikoLib import NKFileSystem
    if compiled:
        if not NKFileSystem.NKHDLock.lock("GMLauncher"):
            print("SingleInstance FAIL")
            from GML_Connector import GMLConnector
            GMLConnector().awake("LaunchPad")
            return
        else:
            print("SingleInstance OK")
    else:
        print("SingleInstance Disabled")

    # PATCHING CONFIG
    from NikoKit.NikoStd.NKConfig import NKConfig
    GMLRuntime.Config = NKConfig(secret=False, admin_password="sudo")
    yaml_config_path = p.join(smb_dir, "gml", "config", GMLRuntime.File.yaml_config)
    GMLRuntime.Config.patch_yaml_config(yaml_path=yaml_config_path, silent_mode=True)
    parser = argparse.ArgumentParser()
    GMLRuntime.Config.configure_parser(parser=parser)
    GMLRuntime.Config.patch_from_parser(parser=parser)

    print("Config OK --secret" if GMLRuntime.Config.secret else "Config OK")

    # Init current user
    GMLRuntime.Feature.refresh_current_user()

    # Init ad users
    GMLRuntime.Feature.refresh_all_users()

    # NQSatellite
    from NikoKit.NikoQt.NQSatellite.Satellite import NQSatellite
    from NikoKit.NikoStd.NKVersion import NKVersion
    from GML_Res import res as res_patch
    GMLRuntime.SatelliteApp = NQSatellite(name="GMainLauncher",
                                          name_short="GML",
                                          version=NKVersion(GML_VERSION),
                                          version_tag=NKVersion.ALPHA,
                                          entry_py_path=__file__,
                                          admin_password="sudo",
                                          before_exit_callback=before_exit_callback,
                                          icon_res_name="GML.png",
                                          runtime=GMLRuntime,
                                          appdata_dir="",  # Auto-Generated
                                          log_dir=GMLRuntime.Dir.log_dir,
                                          use_dummy=False,
                                          scan_machine_spec=True,
                                          cmd_server_port=GML_PORT,
                                          enable_nk_logger=False,  # Pre-Loaded, Disabled
                                          enable_dark_theme=True,
                                          enable_resource=True,
                                          resource_patch=res_patch,
                                          enable_timer=True,
                                          enable_window_manager=True,
                                          enable_appdata_manager=True,
                                          enable_data_loader=True,
                                          enable_nk_language=True,
                                          enable_nk_guard=True)

    print("NQSatellite OK")

    # Language Patch & Default CMD support
    from NikoKit.NikoStd import NKConst
    GMLRuntime.Service.NKLang.patch(language=NKConst.ZH_CN, patch_pack=GML_Language_pack)
    register_commands()
    GMLRuntime.Signals.cmd_broadcast.connect(cmd_handler)

    # Add Restart Button
    tray_content = GMLRuntime.Gui.TrayIconMgr.tray_menu_generator.content_list
    from NikoKit.NikoQt.NQKernel.NQComponent.NQMenu import NQMenuOption
    tray_content.insert(-1, NQMenuOption(name="restart",
                                         display_name=GMLRuntime.Service.NKLang.tran("restart"),
                                         slot_callback=restart_gml))
    GMLRuntime.Gui.TrayIconMgr.rebuild()

    # Import PluginLoader
    try:
        from GML_PluginLoader import plugin_loader, plugin_stopper
        GMLRuntime.Plugin.loader = plugin_loader
        GMLRuntime.Plugin.stopper = plugin_stopper
        print("PluginLoader READY")
        GMLRuntime.Plugin.loader()
    except:
        from NikoKit.NikoStd.NKPrint import eprint
        eprint("PluginLoader FAILURE\n%s" % traceback.format_exc())

    # Launch GMLG
    if GMLRuntime.App.compiled:
        try:
            launch_gml_g()
            print("GMLG OK")
        except Exception as e:
            print(f"GMLG FAIL -> {e}")
    else:
        print("GMLG Disabled")

    print("GML Version %s is now Online " % str(GMLRuntime.App.version))
    GMLRuntime.SatelliteApp.serve()


def register_commands():
    from GML_Runtime import GMLRuntime
    GMLRuntime.Service.NKCmd.register_command("restart", "This will restart GML.")
    GMLRuntime.Service.NKCmd.register_command("alert", "This pop up a message.")


def cmd_handler(command_id, command_line):
    from GML_Runtime import GMLRuntime
    from NikoKit.NikoLib import NKCmd
    if command_line.strip() == "restart":
        GMLRuntime.Service.NKCmd.finish_command(
            command_id=command_id,
            result_sign=NKCmd.NKCmdServer.RESULT_SIGN_GOOD,
            result_detail="restart received"
        )
        restart_gml()
    if command_line.startswith("alert"):
        GMLRuntime.Service.NKCmd.finish_command(
            command_id=command_id,
            result_sign=NKCmd.NKCmdServer.RESULT_SIGN_GOOD,
            result_detail="alert received"
        )
        alert(message=command_line[5:].strip())


def alert(message):
    from NikoKit.NikoQt.NQKernel.NQGui.NQWindowInfo import NQWindowInfo
    NQWindowInfo(w_title="GML", info_string=message, w_width=500, w_height=300, on_top=True).show()


def launch_gml_g():
    # Must Run After NQApplication Established
    from GML_Runtime import GMLRuntime
    from NikoKit.NikoStd import NKLaunch
    from NikoKit.NikoStd.NKLaunch import DISPLAY_MODE_HIDE
    process = NKLaunch.run(command=[p.join(GMLRuntime.App.my_dir, 'GMLG.exe'),
                                    "--log_dir", p.join(GMLRuntime.Dir.log_dir, 'GMLG'),
                                    "--gml_pid", str(os.getpid()),
                                    "--gml_version", str(GMLRuntime.App.version),
                                    "--gml_server_host", GML_SERVER],
                           cwd=GMLRuntime.App.my_dir,
                           display_mode=DISPLAY_MODE_HIDE,
                           custom_env=None
                           )
    GMLRuntime.App.gml_g_pid = process.pid


def kill_gml_g():
    # Shutdown GML
    from NikoKit.NikoStd import NKLaunch, NKConst
    from NikoKit.NikoStd.NKPrint import tprint, eprint
    from GML_Runtime import GMLRuntime
    if GMLRuntime.App.gml_g_pid:
        kill_proc = NKLaunch.run_pipe(command=["taskkill", "/IM", "GMLG.exe", "/F"])
        while kill_proc.poll() is None:
            new_line = kill_proc.stdout.readline().decode(NKConst.SYS_CHARSET)
            tprint(f"KillGMLG::{new_line.replace(os.linesep, '')}")
    else:
        eprint(f"KillGMLG::There is no PID of GMLG.")


def before_exit_callback(restart=False):
    from GML_Runtime import GMLRuntime
    if GMLRuntime.App.compiled and not restart:
        kill_gml_g()

    try:
        GMLRuntime.Plugin.stopper()
    except:
        from NikoKit.NikoStd.NKPrint import eprint
        eprint(traceback.format_exc())

    from NikoKit.NikoStd import NKLaunch
    NKLaunch.run(command=["taskkill", "/PID", str(os.getpid()), "/F"])


def restart_gml():
    from GML_Runtime import GMLRuntime
    GMLRuntime.SatelliteApp.exit(restart=True)


if __name__ == "__main__":
    launch_gml()
