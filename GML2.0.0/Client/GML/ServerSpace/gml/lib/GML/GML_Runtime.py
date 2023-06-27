from PySide2.QtCore import Signal

from NikoKit.NikoQt.NQSatellite.Runtime import NQSatelliteRuntime, NQSatelliteSignals


class GMLSignals(NQSatelliteSignals):
    cmd_broadcast = Signal(str, str)  # cmd_id, cmd_line
    awake = Signal(str)  # Awake Signal
    user_updated = Signal()  # For user-info sensitive modules
    proj_updated = Signal()  # For project sensitive modules


class GMLRuntime(NQSatelliteRuntime):
    SatelliteApp = None
    Signals = GMLSignals()

    class Database(NQSatelliteRuntime.Database):
        AdConn = None

    class Data(NQSatelliteRuntime.Data):
        cgtw_obj = None
        current_user = None
        current_proj = None
        all_users = None

    class App(NQSatelliteRuntime.App):
        server_ip = None
        gml_g_pid = None

    class Plugin:
        loader = None
        stopper = None
        LaunchPad = None
        LegacySupport = None
        WorkforceMonitor = None
        Appointment = None

    class Dir(NQSatelliteRuntime.Dir):
        config_dir = ""
        plugin_dir = ""
        lib_dir = ""
        release_dir = ""
        icon_dir = ""

    class File(NQSatelliteRuntime.File):
        yaml_upgrade = "upgrade.yaml"
        py_plugin_loader = "PluginLoader.py"

    class Feature:
        refresh_current_user = None
        refresh_all_users = None
