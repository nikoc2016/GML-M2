from GML_Runtime import GMLRuntime
from LegacySupport.GDC_V2 import GDC, log, log_err, log_warn
from LegacySupport.GML_Connector_Legacy import save_mydoc_login_file
from LegacySupport.ITWindow import ITWindow
from LegacySupport.Legacy_Runtime import LegacyRuntime
from NikoKit.NikoLib import NKCmd
from NikoKit.NikoQt.NQKernel.NQComponent.NQMenu import NQMenuOption


def load():
    # LoginStatus.json
    GMLRuntime.Signals.second_passed.connect(save_mydoc_login_file)
    log("GML LoginStatus Service OK")
    GMLRuntime.Plugin.LegacySupport = LegacyRuntime

    # IT Ticket
    contents = GMLRuntime.Gui.TrayIconMgr.tray_menu_generator.content_list
    contents.insert(3, NQMenuOption(name="it_ticket",
                                    display_name=GMLRuntime.Service.NKLang.tran("ui_it_ticket"),
                                    icon=None,
                                    slot_callback=slot_launch_it_ticket_window))
    GMLRuntime.Gui.TrayIconMgr.rebuild()
    register_commands()
    GMLRuntime.Signals.cmd_broadcast.connect(cmd_handler)

    # GDC_V2 Plugin from GML-1M
    LegacyRuntime.GDC_thread = GDC()
    log("GML GDC Service OK")
    LegacyRuntime.GDC_thread.start()


def unload():
    GMLRuntime.Signals.second_passed.disconnect(save_mydoc_login_file)
    if LegacyRuntime.GDC_thread:
        LegacyRuntime.GDC_thread.stop_flag = True


def slot_launch_it_ticket_window():
    ITWindow(w_title=GMLRuntime.Service.NKLang.tran("ui_it_ticket"),
             w_width=400,
             w_height=300).show()


def register_commands():
    GMLRuntime.Service.NKCmd.register_command("ticket", "Start IT-Ticket Window")


def cmd_handler(command_id, command_line):
    if command_line == "ticket":
        slot_launch_it_ticket_window()
        GMLRuntime.Service.NKCmd.finish_command(
            command_id=command_id,
            result_sign=NKCmd.NKCmdServer.RESULT_SIGN_GOOD,
            result_detail="ticket command received"
        )
