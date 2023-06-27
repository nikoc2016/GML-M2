import traceback

from NikoKit.NikoStd.NKPrint import eprint


def plugin_loader():
    from LaunchPad.LaunchPad import load as load_launch_pad
    try:
        load_launch_pad()
        print("PluginLoader->LaunchPad OK")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader->LaunchPad FAIL")

    from LegacySupport import load as load_legacy_support
    try:
        load_legacy_support()
        print("PluginLoader->LegacySupport OK")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader->LegacySupport FAIL")

    from WorkforceMonitor.WorkforceMonitor import load as load_workforce_monitor
    try:
        load_workforce_monitor()
        print("PluginLoader->WorkforceMonitor OK")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader->LegacySupport FAIL")

    from Appointment.Appointment import load as load_appointment
    try:
        load_appointment()
        print("PluginLoader->Appointment OK")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader->Appointment FAIL")

    from GMLMayaLauncher.GMLMayaLauncher import load as load_gml_maya_launcher
    try:
        load_gml_maya_launcher()
        print("PluginLoader->GMLMayaLauncher OK")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader->GMLMayaLauncher FAIL")


def plugin_stopper():
    from LaunchPad.LaunchPad import unload as unload_launch_pad
    try:
        unload_launch_pad()
        print("PluginLoader->LaunchPad UNLOADED")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader->LaunchPad UNLOADED FAIL")

    from LegacySupport import unload as unload_legacy_support
    try:
        unload_legacy_support()
        print("PluginLoader-> LegacySupport UNLOADED")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader-> LegacySupport UNLOADED FAIL")

    from WorkforceMonitor.WorkforceMonitor import unload as unload_workforce_monitor
    try:
        unload_workforce_monitor()
        print("PluginLoader->WorkforceMonitor UNLOADED")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader->WorkforceMonitor UNLOADED FAIL")

    from Appointment.Appointment import unload as unload_appointment
    try:
        unload_appointment()
        print("PluginLoader->Appointment UNLOADED")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader->Appointment UNLOADED FAIL")

    from GMLMayaLauncher.GMLMayaLauncher import unload as unload_gml_maya_launcher
    try:
        unload_gml_maya_launcher()
        print("PluginLoader->GMLMayaLauncher UNLOADED")
    except:
        eprint(traceback.format_exc())
        print("PluginLoader->GMLMayaLauncher UNLOADED FAIL")
