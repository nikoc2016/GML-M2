ENFORCE_DEV_MODE = False

if __name__ == "__main__":
    import sys
    import os

    # ===== GML =====
    import GML
    if getattr(sys, 'frozen', False):
        GML.app_compiled = True
        GML.app_dir = os.path.dirname(sys.executable)
        GML.app_exe = os.path.basename(sys.executable)
    else:
        GML.app_compiled = False
        GML.app_dir = os.path.dirname(os.path.abspath(__file__))
        GML.app_exe = os.path.basename(__file__)

    # ===== Logger =====
    from GML_Logger import Logger
    GML.app_log_path = os.path.join(GML.app_dir, GML.app_short_name + ".log")
    GML.Logger = Logger()

    # ===== Sys =====
    import GML_Sys
    GML.Sys = GML_Sys
    GML.Sys.configure_paths(ENFORCE_DEV_MODE)

    # Lock GML
    GML.Sys.lock_multi_instance()

    # Async Hardware Snapshot
    GML.Hardware = GML.Sys.GML_Hardware()

    # ===== Database =====
    import GML_Database
    GML.Database = GML_Database
    GML.Database.init()

    # ===== Cmd =====
    import GML_Cmd
    GML.Cmd = GML_Cmd
    GML.Cmd.init()

    # ===== Qt =====
    import GML_Qt
    GML.Qt = GML_Qt
    GML.Qt.launch()
