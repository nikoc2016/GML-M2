import datetime
import json
import os.path as p
import traceback

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QVBoxLayout, QLabel, QMenuBar, QScrollArea, QLineEdit, QHBoxLayout, QSystemTrayIcon

from NikoKit.NikoLib import NKLogger, NKCmd
from NikoKit.NikoQt import NQApplication
from NikoKit.NikoQt.NQKernel.NQComponent import NQMenu
from NikoKit.NikoQt.NQKernel.NQComponent.NQMenu import NQMenuOption
from NikoKit.NikoQt.NQKernel.NQGui.NQWidgetLabel import NQWidgetLabel
from NikoKit.NikoQt.NQKernel.NQGui.NQWidgetLaunchPad import NQWidgetLaunchPad
from NikoKit.NikoQt.NQKernel.NQGui.NQWindow import NQWindow
from NikoKit.NikoStd import NKLaunch

from LaunchPad.CGTLoginWindow import CGTWLoginWindow
from LaunchPad.ConfigLoader import load_configs
from LaunchPad.ProjectSelectionWindow import ProjectSelectionWindow

from GML_Runtime import GMLRuntime


def load():
    GMLRuntime.Plugin.LaunchPad = LPRuntime
    LPRuntime.Dir.boot_dir = p.join(GMLRuntime.Dir.config_dir, "LaunchPad", "boot")
    LPRuntime.Dir.plan_dir = p.join(GMLRuntime.Dir.config_dir, "LaunchPad", "plan")
    LPRuntime.Dir.proj_dir = p.join(GMLRuntime.Dir.config_dir, "LaunchPad", "proj")
    contents = GMLRuntime.Gui.TrayIconMgr.tray_menu_generator.content_list
    contents.insert(2, NQMenuOption(name="launch_pad",
                                    display_name="GML",
                                    icon=GMLRuntime.Data.Res.QIcon(GMLRuntime.App.icon_res_name),
                                    slot_callback=show_launch_pad_window))
    GMLRuntime.Gui.TrayIconMgr.rebuild()
    GMLRuntime.Signals.tray_clicked.connect(slot_tray_clicked)

    register_commands()
    GMLRuntime.Signals.cmd_broadcast.connect(cmd_handler)
    GMLRuntime.Signals.awake.connect(awake_handler)

    if not GMLRuntime.Config.secret:
        show_launch_pad_window()


def unload():
    if GMLRuntime.Plugin.LaunchPad.WinMain:
        GMLRuntime.Plugin.LaunchPad.WinMain.close()


class LPRuntime:
    WinMain = None

    class Dir:
        boot_dir = None
        plan_dir = None
        proj_dir = None


def slot_tray_clicked(reason):
    if reason == QSystemTrayIcon.DoubleClick:
        show_launch_pad_window()


def show_launch_pad_window():
    if LPRuntime.WinMain:
        try:
            LPRuntime.WinMain.close()
        except:
            pass
    LPRuntime.WinMain = LaunchWindow()
    LPRuntime.WinMain.show()


BOOT = "boot"
PLAN = "plan"
PROJ = "proj"
JSON = "json"
YAML = "yaml"
LOG_CHANNEL = "LaunchPad"


def register_commands():
    GMLRuntime.Service.NKCmd.register_command("launch", "launch {'method': '?', 'param': '?'}")
    GMLRuntime.Service.NKCmd.register_command("launch boot", "launch boot [boot_name]")


def awake_handler(target):
    if target.lower() == "launchpad":
        show_launch_pad_window()


def cmd_handler(command_id, command_line):
    if command_line.startswith("launch"):
        temp_launch_pad_window = LaunchWindow(fast_login_cgt=False)
        temp_launch_pad_window.slot_refresh_all()
        result_table = {
            True: NKCmd.NKCmdServer.RESULT_SIGN_GOOD,
            False: NKCmd.NKCmdServer.RESULT_SIGN_FAIL,
        }

        command_detail = command_line[6:].strip()
        if command_detail.startswith("boot"):
            boot_name = command_detail[4:].strip()
            result_bool = temp_launch_pad_window.launch_boot(boot_name=boot_name)
            GMLRuntime.Service.NKCmd.finish_command(
                command_id=command_id,
                result_sign=result_table[result_bool],
                result_detail="launch boot received"
            )
        else:
            try:
                app_run = json.loads(command_detail)
                result_bool = temp_launch_pad_window.launch(method=app_run["method"], params=app_run["params"])
                GMLRuntime.Service.NKCmd.finish_command(
                    command_id=command_id,
                    result_sign=result_table[result_bool],
                    result_detail="launch received"
                )
            except Exception as e:
                GMLRuntime.Service.NKCmd.finish_command(
                    command_id=command_id,
                    result_sign=result_table[False],
                    result_detail="Wrong JSON " + str(e)
                )

        temp_launch_pad_window.close()


class LaunchWindow(NQWindow):
    def __init__(self,
                 fast_login_cgt=True,
                 w_title=f"{GMLRuntime.App.name} V{GMLRuntime.App.version} {GMLRuntime.App.version_tag}",
                 w_width=550,
                 w_height=800
                 ):
        # Data Storage
        self.boot_name_to_obj = {}
        self.plan_name_to_obj = {}
        self.proj_name_to_obj = {}

        # GUI Components
        self.main_lay = None
        self.welcome_label = None
        self.search_line_edit = None
        self.launch_pad = None
        self.menu_gml_generator = None
        self.action_cgt_login = None
        self.action_switch_project = None

        super(LaunchWindow, self).__init__(w_title=w_title, w_width=w_width, w_height=w_height)

        self.load_menu()
        if fast_login_cgt and not GMLRuntime.Data.current_user.user_cgt_account:
            self.slot_cgt_login(fast_login=True)
        else:
            if not GMLRuntime.Data.current_proj:
                self.slot_project_selection()
        self.slot_refresh_all()

    def closeEvent(self, event):
        LPRuntime.WinMain = None
        super(LaunchWindow, self).closeEvent(event)

    def construct(self):
        super(LaunchWindow, self).construct()
        main_lay = QVBoxLayout()
        welcome_label = QLabel("")
        welcome_label.setAlignment(Qt.AlignHCenter)
        search_lay = QHBoxLayout()
        search_label = QLabel(self.lang("tool", "search"))
        search_line_edit = QLineEdit()
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidgetResizable(True)
        scroll_area.setContentsMargins(0, 0, 0, 0)
        launch_pad = NQWidgetLaunchPad(w_name="GMLaunchPad", w_title="GMLaunchPad", launch_btn_col_count=3)
        menu_gml_generator = NQMenu.NQMenuGenerator(
            content_list=[
                NQMenu.NQMenuOption(name="cgt_login",
                                    display_name=self.lang("CGT", "login"),
                                    icon=GMLRuntime.Data.Res.QIcon(GMLRuntime.App.icon_res_name),
                                    slot_callback=self.slot_cgt_login),
                NQMenu.NQMenuOption(name="switch_project",
                                    display_name=self.lang("switch", "project"),
                                    icon=GMLRuntime.Data.Res.QIcon(GMLRuntime.App.icon_res_name),
                                    slot_callback=self.slot_project_selection),
                NQMenu.NQMenuOption(name="refresh",
                                    display_name=self.lang("refresh"),
                                    icon=GMLRuntime.Data.Res.QIcon(GMLRuntime.App.icon_res_name),
                                    slot_callback=self.slot_refresh_all),
            ]
        )

        main_lay.addWidget(welcome_label)
        main_lay.addLayout(search_lay)
        main_lay.addWidget(scroll_area)
        main_lay.setStretchFactor(scroll_area, 1)

        search_lay.addStretch()
        search_lay.addWidget(search_label)
        search_lay.addWidget(search_line_edit)
        search_lay.addStretch()

        scroll_area.setWidget(launch_pad)

        self.main_lay = main_lay
        self.welcome_label = welcome_label
        self.search_line_edit = search_line_edit
        self.launch_pad = launch_pad
        self.menu_gml_generator = menu_gml_generator

        self.setLayout(main_lay)

    def connect_signals(self):
        super(LaunchWindow, self).connect_signals()
        GMLRuntime.Signals.user_updated.connect(self.slot_refresh_all_and_select_project)
        GMLRuntime.Signals.proj_updated.connect(self.slot_refresh_all)
        self.launch_pad.signal_launch.connect(self.launch_boot)
        self.search_line_edit.textChanged.connect(self.slot_refresh_launch_pad)

    def load_menu(self):
        menu_bar = QMenuBar()
        menu_bar.addMenu(self.menu_gml_generator.to_menu(title="GML"))
        self.main_lay.setMenuBar(menu_bar)

    def slot_refresh_all_and_select_project(self):
        if not GMLRuntime.Data.current_proj:
            self.slot_project_selection()
        self.slot_refresh_all()

    def slot_refresh_all(self):
        self.slot_update_welcome_label()
        self.slot_reload_boot_configs(refresh_launch_pad=True)

    def slot_reload_boot_configs(self, refresh_launch_pad=True):
        self.boot_name_to_obj, self.plan_name_to_obj, self.proj_name_to_obj = load_configs(
            search_dirs=[LPRuntime.Dir.boot_dir,
                         LPRuntime.Dir.plan_dir,
                         LPRuntime.Dir.proj_dir])
        if refresh_launch_pad:
            self.slot_refresh_launch_pad()

    def slot_refresh_launch_pad(self):
        self.launch_pad.clear_launch_targets()

        # Get Current Project
        current_proj = f"proj_{GMLRuntime.Data.current_proj}"
        if not current_proj or current_proj not in self.proj_name_to_obj:
            current_proj = "proj"

        # Get Boot Options
        boot_options = set(self.proj_name_to_obj[current_proj])
        plans = set()
        for possible_plan in boot_options:
            if possible_plan.startswith(PLAN):
                plans.add(possible_plan)
        for plan in plans:
            for boot_option in self.plan_name_to_obj[plan]:
                boot_options.add(boot_option)
            boot_options.remove(plan)

        # Render to Panel
        launch_order_list = [self.lang("ui_launch_pad_workspace"),
                             self.lang("ui_launch_pad_common_tool"),
                             self.lang("ui_launch_pad_offline_tool"),
                             self.lang("ui_launch_pad_playground")]
        launch_options = {}
        for boot_option in boot_options:
            boot_config = self.boot_name_to_obj[boot_option]
            boot_config["boot_option"] = boot_option
            if boot_config["app_category"] not in launch_order_list:
                launch_order_list.append(boot_config["app_category"])
            if boot_config["app_category"] not in launch_options:
                launch_options[boot_config["app_category"]] = []
            launch_options[boot_config["app_category"]].append(boot_config)

        if launch_options is {}:
            return

        for category_name in launch_order_list:
            category_list = launch_options.get(category_name)
            if category_list is None:
                continue
            category_list.sort(key=lambda option: option["app_display_name"])
            for app_option in category_list:
                try:
                    if self.search_line_edit.text() == "" \
                            or self.search_line_edit.text().lower() in app_option["app_display_name"].lower():
                        icon_path = p.join(GMLRuntime.Dir.icon_dir, app_option["app_icon"])
                        if p.isfile(icon_path):
                            icon = QIcon(icon_path)
                        else:
                            icon = GMLRuntime.Data.Res.QIcon(GMLRuntime.App.icon_res_name)

                        launch_target = NQWidgetLaunchPad.LaunchTarget(
                            value=app_option["boot_option"],
                            label=app_option["app_display_name"],
                            tooltip=app_option["app_tooltip"],
                            group=app_option["app_category"],
                            group_display_name=app_option["app_category"],
                            size=150,
                            icon=icon,
                            enabled=True
                        )
                        self.launch_pad.add_launch_target(launch_target)
                except:
                    GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                                    log_type=NKLogger.STD_ERR,
                                                    log_context=traceback.format_exc())

        # for boot_option in boot_options:
        #     try:
        #         boot_config = self.boot_name_to_obj[boot_option]
        #         if self.search_line_edit.text() == "" or self.search_line_edit.text().lower() in boot_config[
        #             "app_display_name"].lower():
        #             icon_path = p.join(GMLRuntime.Dir.icon_dir, boot_config["app_icon"])
        #             if p.isfile(icon_path):
        #                 icon = QIcon(icon_path)
        #             else:
        #                 icon = GMLRuntime.Data.Res.QIcon(GMLRuntime.App.icon_res_name)
        #
        #             launch_target = NQWidgetLaunchPad.LaunchTarget(
        #                 value=boot_option,
        #                 label=boot_config["app_display_name"],
        #                 tooltip=boot_config["app_tooltip"],
        #                 group=boot_config["app_category"],
        #                 group_display_name=boot_config["app_category"],
        #                 size=150,
        #                 icon=icon,
        #                 enabled=True
        #             )
        #             self.launch_pad.add_launch_target(launch_target)
        #     except:
        #         GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
        #                                         log_type=NKLogger.STD_ERR,
        #                                         log_context=traceback.format_exc())

    def slot_update_welcome_label(self):
        try:
            chinese_name = str(GMLRuntime.Data.current_user.user_last_name) + str(
                GMLRuntime.Data.current_user.user_first_name)
        except:
            chinese_name = self.lang("yet", "login")
        base_str = f'{self.lang("hello")}, {chinese_name} {self.lang("project")}: {GMLRuntime.Data.current_proj}'
        self.welcome_label.setText(base_str)

    def slot_cgt_login(self, fast_login=False):
        CGTWLoginWindow(w_title=self.lang("CGTW", "login"),
                        cgt_username=GMLRuntime.Data.current_user.user_cgt_account,
                        cgt_password=GMLRuntime.Data.current_user.user_cgt_password,
                        fast_login=fast_login,
                        success_callback=self.slot_refresh_all).show()

    def slot_project_selection(self):
        ProjectSelectionWindow(w_title=self.lang("select", "project")).show()

    def launch_boot(self, boot_name):
        log = GMLRuntime.Service.NKLogger.log
        try:
            return self.launch(method=self.boot_name_to_obj[boot_name]["app_run"]["method"],
                               params=self.boot_name_to_obj[boot_name]["app_run"]["params"])
        except:
            log(log_channel=LOG_CHANNEL,
                log_type=NKLogger.STD_ERR,
                log_context=f"launch_boot(boot_name={boot_name})\n{traceback.format_exc()}")
            return False

    @staticmethod
    def launch(method, params):
        log = GMLRuntime.Service.NKLogger.log

        if not method:
            log(log_channel=LOG_CHANNEL,
                log_type=NKLogger.STD_ERR,
                log_context=f"launch(method={method}, params={params})::"
                            f"No Method Found\n")
            return False
        elif method == "run":
            required_params = ["command", "custom_env", "cwd", "display_mode"]
            display_mode = {
                "SW_HIDE": 0,
                "SW_SHOWNORMAL": 1,
                "SW_MINIMIZE": 6,
                "SW_MAXIMIZE": 3
            }
            for required_param in required_params:
                if required_param not in params.keys():
                    log(log_channel=LOG_CHANNEL,
                        log_type=NKLogger.STD_ERR,
                        log_context=f"launch(method={method}, params={params})::"
                                    f"Required params not satisfied: {required_params}\n")
                    return False
            if not params["command"]:
                log(log_channel=LOG_CHANNEL,
                    log_type=NKLogger.STD_ERR,
                    log_context=f"launch(method={method}, params={params}):: Empty Command\n")
                return False
            if params["custom_env"] and not isinstance(params["custom_env"], dict):
                log(log_channel=LOG_CHANNEL,
                    log_type=NKLogger.STD_ERR,
                    log_context=f"launch(method={method}, params={params}):: custom_env must be dict.\n")
                return False
            if params["display_mode"] and params["display_mode"] not in display_mode.keys():
                log(log_channel=LOG_CHANNEL,
                    log_type=NKLogger.STD_ERR,
                    log_context=f"launch(method={method}, params={params}):: unsupported display mode, "
                                f"use {display_mode.keys()}\n")
                return False

            try:
                NKLaunch.run(command=params["command"],
                             cwd=params["cwd"],
                             display_mode=display_mode[params["display_mode"]],
                             custom_env=params["custom_env"])
                return True
            except:
                log(log_channel=LOG_CHANNEL,
                    log_type=NKLogger.STD_ERR,
                    log_context=f"launch(method={method}, params={params})\n{traceback.format_exc()}")
                return False

        elif method == "run_system" or method == "run_system_sequential":
            required_params = ["command", "pause"]
            for required_param in required_params:
                if required_param not in params.keys():
                    log(log_channel=LOG_CHANNEL,
                        log_type=NKLogger.STD_ERR,
                        log_context=f"launch(method={method}, params={params})::"
                                    f"Required params not satisfied: {required_params}\n")
                    return False

            if not params["command"]:
                log(log_channel=LOG_CHANNEL,
                    log_type=NKLogger.STD_ERR,
                    log_context=f"launch(method={method}, params={params}):: Empty Command\n")
                return False

            if params["pause"]:
                params["pause"] = True
            else:
                params["pause"] = False

            try:
                if method == "run_system":
                    NKLaunch.run_system(command=params["command"], pause=params["pause"])
                elif method == "run_system_sequential":
                    NKLaunch.run_system_sequential(commands=params["command"], pause=params["pause"])
                else:
                    log(log_channel=LOG_CHANNEL,
                        log_type=NKLogger.STD_ERR,
                        log_context=f"launch(method={method}, params={params})::Unexpected method this shouldn't happen")
                    return False
                return True
            except:
                log(log_channel=LOG_CHANNEL,
                    log_type=NKLogger.STD_ERR,
                    log_context=f"launch(method={method}, params={params})\n{traceback.format_exc()}")
                return False

        elif method == "gml_cmd":
            required_params = ["command"]
            for required_param in required_params:
                if required_param not in params.keys():
                    log(log_channel=LOG_CHANNEL,
                        log_type=NKLogger.STD_ERR,
                        log_context=f"launch(method={method}, params={params})::"
                                    f"Required params not satisfied: {required_params}\n")
                    return False

            if not params["command"]:
                log(log_channel=LOG_CHANNEL,
                    log_type=NKLogger.STD_ERR,
                    log_context=f"launch(method={method}, params={params}):: Empty Command\n")
                return False

            try:
                GMLRuntime.Service.NKCmd.execute_command(
                    command_line=params["command"],
                    client_socket=None,
                    client_address=None
                )
                return True
            except:
                log(log_channel=LOG_CHANNEL,
                    log_type=NKLogger.STD_ERR,
                    log_context=f"launch(method={method}, params={params})\n{traceback.format_exc()}")
                return False
