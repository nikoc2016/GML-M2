# coding=utf8
# Copyright (c) lovICer 2022/7/11 in gtec_media_dev


import os
import traceback

import yaml
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QTextEdit, QLabel, QPushButton, QTabWidget, QApplication

from GML_Runtime import GMLRuntime
from NikoKit.NikoLib import NKLogger
from NikoKit.NikoQt.NQKernel.NQGui.NQWidgetArea import NQWidgetArea
from NikoKit.NikoQt.NQKernel.NQGui.NQWidgetCheckList import NQWidgetCheckList
from NikoKit.NikoQt.NQKernel.NQGui.NQWindow import NQWindow
from NikoKit.NikoStd.NKDataStructure import NKDataStructure
from NikoKit.NikoStd.NKTime import NKDatetime, NKDate


def load():
    GMLRuntime.Plugin.WorkforceMonitor = WMRuntime
    WMRuntime.Path.org_path = os.path.join(GMLRuntime.Dir.config_dir, "WorkforceMonitor", "org.yaml")
    WMRuntime.Path.proj_path = os.path.join(GMLRuntime.Dir.config_dir, "WorkforceMonitor", "proj.yaml ")
    WMRuntime.MainWin = WorkforceMonitor()
    GMLRuntime.Signals.awake.connect(awake_handler)
    # WMRuntime.MainWin.show()


def unload():
    if GMLRuntime.Plugin.WorkforceMonitor.MainWin:
        GMLRuntime.Plugin.WorkforceMonitor.MainWin.close()


LOG_CHANNEL = "WorkforceMonitor"


def log(context):
    context = str(context)
    if not context.endswith("\n"):
        context += "\n"
    GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                    log_type=NKLogger.STD_OUT,
                                    log_context=context)


def log_warn(context):
    context = str(context)
    if not context.endswith("\n"):
        context += "\n"
    GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                    log_type=NKLogger.STD_WARNING,
                                    log_context=context)


def log_err(context):
    context = str(context)
    if not context.endswith("\n"):
        context += "\n"
    GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                    log_type=NKLogger.STD_ERR,
                                    log_context=context)


class WMRuntime:
    MainWin = None

    class Path:
        org_path = None
        proj_path = None

    class Database:
        Conn = GMLRuntime.Database.Conn

        class Create:
            @classmethod
            def log(cls, wm_log_obj):
                table = "Plugin_WorkforceMonitor"
                fields = ["log_username",
                          "log_username_chinese",
                          "log_date",
                          "log_plan_projects",
                          "log_plan_handler",
                          "log_plan_handler_chinese",
                          "log_result_projects",
                          "log_result_handler",
                          "log_result_handler_chinese"]
                values = ["%s" for i in range(len(fields))]

                sql_line = WMRuntime.Database.Conn.build_insert_clause(table=table,
                                                                       fields=fields,
                                                                       values=values,
                                                                       on_duplicate_ignore_fields=["log_username",
                                                                                                   "log_date"])

                sql_data = [wm_log_obj.log_username,
                            wm_log_obj.log_username_chinese,
                            wm_log_obj.log_date,
                            str(wm_log_obj.log_plan_projects),
                            wm_log_obj.log_plan_handler,
                            wm_log_obj.log_plan_handler_chinese,
                            str(wm_log_obj.log_result_projects),
                            wm_log_obj.log_result_handler,
                            wm_log_obj.log_result_handler_chinese]

                return WMRuntime.Database.Conn.write(sql_line=sql_line, sql_data=sql_data)

        class Retrieve:
            @classmethod
            def log(cls,
                    fields=None,
                    where_clause="",
                    sort_field="log_username, log_date",
                    sort_asc=True,
                    limit=None):
                table = "Plugin_WorkforceMonitor"

                sql_line = WMRuntime.Database.Conn.build_select_clause(fields)
                sql_line += WMRuntime.Database.Conn.build_from_clause(table)
                sql_line += where_clause
                sql_line += WMRuntime.Database.Conn.build_order_clause(sort_field, sort_asc)
                sql_line += WMRuntime.Database.Conn.build_limit_clause(limit)

                result, errors = WMRuntime.Database.Conn.query(sql_line)
                return WMRuntime.Database.Conn.no_binary(result), errors


def show_workforce_monitor_window():
    if WMRuntime.MainWin:
        try:
            WMRuntime.MainWin.close()
        except:
            log_err(traceback.format_exc())
    WMRuntime.MainWin = WorkforceMonitor()
    WMRuntime.MainWin.show()
    # if not WMRuntime.MainWin:
    #     WMRuntime.MainWin = WorkforceMonitor()
    # WMRuntime.MainWin.show()


def awake_handler(target):
    if target.lower().startswith("workforcemonitor"):
        show_workforce_monitor_window()


class WMLog(NKDataStructure):
    def __init__(self,
                 log_username=None,
                 log_username_chinese=None,
                 log_date=None,
                 log_plan_projects=None,
                 log_plan_handler=None,
                 log_plan_handler_chinese=None,
                 log_result_projects=None,
                 log_result_handler=None,
                 log_result_handler_chinese=None):
        super(WMLog, self).__init__()
        self.log_username = log_username
        self.log_username_chinese = log_username_chinese
        self.log_date = log_date
        self.log_plan_projects = log_plan_projects or []
        self.log_plan_handler = log_plan_handler
        self.log_plan_handler_chinese = log_plan_handler_chinese
        self.log_result_projects = log_result_projects or []
        self.log_result_handler = log_result_handler
        self.log_result_handler_chinese = log_result_handler_chinese


class WorkforceMonitor(NQWindow):
    def __init__(self,
                 detail_datetime=None,
                 *args,
                 **kwargs):
        # Private Storage
        self.current_user = None
        self.detail_time = detail_datetime or NKDatetime.now()
        self.is_afternoon = detail_datetime.hour > 12

        self.organization = {}
        self.available_projects = []

        self.logs = {}

        self.selected_username = ""
        self.selected_plan_projects = []
        self.selected_result_projects = []

        # GUI Component
        self.main_lay = None

        self.assign_label = None
        self.assign_user_checklist = None
        self.assign_plan_projects_checklist = None
        self.assign_result_projects_checklist = None

        self.refresh_btn = None
        self.submit_btn = None
        self.exit_btn = None

        self.help_textedit = None
        self.preview_user_textedit = None
        self.preview_project_textedit = None

        super(WorkforceMonitor, self).__init__(
            *args,
            **kwargs)

        self.slot_refresh_data_and_ui()

    def closeEvent(self, event):
        WMRuntime.MainWin = None
        super(WorkforceMonitor, self).closeEvent(event)

    def construct(self):
        super(WorkforceMonitor, self).construct()

        # GUI Component
        main_lay = QHBoxLayout()
        v1 = QVBoxLayout()
        v1_v1 = QVBoxLayout()
        v1_v1_h1 = QHBoxLayout()
        btn_lay = QHBoxLayout()

        preview_user_textedit = QTextEdit()
        preview_user_textedit.setReadOnly(True)
        preview_project_textedit = QTextEdit()
        preview_project_textedit.setReadOnly(True)
        preview_tab_widget = QTabWidget()
        preview_tab_widget.addTab(preview_user_textedit, self.lang("ui_wm_preview_user_tab"))
        preview_tab_widget.addTab(preview_project_textedit, self.lang("ui_wm_preview_project_tab"))
        preview_area = NQWidgetArea(title=self.lang("ui_wm_preview_title"), central_widget=preview_tab_widget)

        help_textedit = QTextEdit()
        help_textedit.setReadOnly(True)
        help_textedit.setText(self.lang("ui_wm_help_text"))
        help_area = NQWidgetArea(title=self.lang("ui_wm_help_title"), central_widget=help_textedit)
        help_area.setMaximumHeight(280)

        assign_area = NQWidgetArea(title=self.lang("ui_wm_assign_title"), central_layout=v1_v1)

        assign_label = QLabel()
        assign_user_checklist = NQWidgetCheckList(exclusive=True)

        assign_plan_projects_checklist = NQWidgetCheckList(exclusive=False)
        assign_plan_projects_area = NQWidgetArea(title=self.lang("ui_wm_assign_plan_projects_title"),
                                                 central_widget=assign_plan_projects_checklist)

        assign_result_projects_checklist = NQWidgetCheckList(exclusive=False)
        assign_result_projects_area = NQWidgetArea(title=self.lang("ui_wm_assign_result_projects_title"),
                                                   central_widget=assign_result_projects_checklist)

        assign_plan_projects_checklist.set_read_only(self.is_afternoon)
        assign_result_projects_checklist.set_read_only(not self.is_afternoon)

        refresh_btn = QPushButton(self.lang("ui_wm_refresh_config_btn_text"))
        submit_btn = QPushButton(self.lang("submit"))
        exit_btn = QPushButton(self.lang("ui_wm_quit_btn_text"))

        # Relationships
        main_lay.addLayout(v1)
        main_lay.addWidget(preview_area)

        v1.addWidget(assign_area)
        v1.addWidget(help_area)

        v1_v1.addWidget(assign_label)
        v1_v1.addLayout(v1_v1_h1)
        v1_v1.addLayout(btn_lay)

        v1_v1_h1.addWidget(assign_user_checklist)
        v1_v1_h1.addWidget(assign_plan_projects_area)
        v1_v1_h1.addWidget(assign_result_projects_area)

        btn_lay.addWidget(refresh_btn)
        btn_lay.addStretch()
        btn_lay.addWidget(submit_btn)
        btn_lay.addWidget(exit_btn)

        # Storage
        self.setLayout(main_lay)

        self.main_lay = main_lay

        self.assign_label = assign_label
        self.assign_user_checklist = assign_user_checklist
        self.assign_plan_projects_checklist = assign_plan_projects_checklist
        self.assign_result_projects_checklist = assign_result_projects_checklist

        self.refresh_btn = refresh_btn
        self.submit_btn = submit_btn
        self.exit_btn = exit_btn

        self.help_textedit = help_textedit
        self.preview_user_textedit = preview_user_textedit
        self.preview_project_textedit = preview_project_textedit

    def connect_signals(self):
        self.assign_user_checklist.changed.connect(self.slot_username_selected)
        self.assign_plan_projects_checklist.changed.connect(self.slot_plan_project_selected)
        self.assign_result_projects_checklist.changed.connect(self.slot_result_project_selected)
        self.refresh_btn.clicked.connect(self.slot_refresh_data_and_ui)
        self.submit_btn.clicked.connect(self.slot_submit)
        self.exit_btn.clicked.connect(self.slot_submit_and_exit)

    def init_data(self):
        GMLRuntime.Feature.refresh_all_users()
        self.current_user = GMLRuntime.Data.all_users[GMLRuntime.Machine.username]
        self.assign_label.setText(
            self.lang("ui_wm_assign_welcome") % (self.current_user.user_last_name + self.current_user.user_first_name,
                                                 self.detail_time.date())
        )

        self.organization = self.get_organization()
        self.available_projects = self.get_available_projects()
        self.logs = self.get_logs()

        if self.logs is None:
            return

        for manage_target_name in self.organization[self.current_user.user_account]:
            manage_target_user = GMLRuntime.Data.all_users[manage_target_name]
            # 试图获取WMLog

            if manage_target_name in self.logs:
                if self.is_afternoon:
                    manage_target_log = self.logs[manage_target_name]
                    if not manage_target_log.log_result_handler:
                        manage_target_log.log_result_projects = manage_target_log.log_plan_projects
                        manage_target_log.log_result_handler = self.current_user.user_account
                        manage_target_log.log_result_handler_chinese = \
                            self.current_user.user_last_name + self.current_user.user_first_name

            # 获取失败则直接创建
            else:
                if not self.is_afternoon:
                    self.logs[manage_target_name] = WMLog(
                        log_username=manage_target_name,
                        log_username_chinese=manage_target_user.user_last_name + manage_target_user.user_first_name,
                        log_date=self.detail_time.date(),
                        log_plan_projects=[],
                        log_plan_handler=self.current_user.user_account,
                        log_plan_handler_chinese=self.current_user.user_last_name + self.current_user.user_first_name
                    )
                else:
                    self.logs[manage_target_name] = WMLog(
                        log_username=manage_target_name,
                        log_username_chinese=manage_target_user.user_last_name + manage_target_user.user_first_name,
                        log_date=self.detail_time.date(),
                        log_result_projects=[],
                        log_result_handler=self.current_user.user_account,
                        log_result_handler_chinese=self.current_user.user_last_name + self.current_user.user_first_name
                    )

    def build_user_text(self, username, project_list):
        user_text = self.lang("ui_wm_preview_text_content_title") % username
        if project_list:
            user_text += "\n    ".join(project_list)
        else:
            user_text += self.lang("ui_wm_preview_text_content_nothing_text")
        return user_text + "\n"

    def build_project_text(self, project, username_list):
        project_text = self.lang("ui_wm_preview_text_content_title") % project
        if username_list:
            project_text += ",".join(username_list)
        else:
            project_text += self.lang("ui_wm_preview_text_content_nothing_text")
        return project_text + "\n"

    def render_preview_text_edit(self):
        users_text = ""
        projects_text = ""
        project_data = {}

        for username in self.logs:
            if not self.is_afternoon:
                user_projects = self.logs[username].log_plan_projects
            else:
                user_projects = self.logs[username].log_result_projects

            users_text += self.build_user_text(self.logs[username].log_username_chinese, user_projects)
            for user_project in user_projects:
                if user_project not in project_data:
                    project_data[user_project] = []
                project_data[user_project].append(self.logs[username].log_username_chinese)
        for project in sorted(project_data.keys()):
            projects_text += self.build_project_text(project, project_data[project])

        self.preview_user_textedit.setText(users_text)
        self.preview_project_textedit.setText(projects_text)

    def slot_refresh_ui(self):
        if self.logs is None:
            self.close()
            return
        for username in self.logs:
            user = GMLRuntime.Data.all_users[username]
            self.assign_user_checklist.add_option(
                option_name=username,
                display_text=user.user_last_name + user.user_first_name,
                checked=True,
                at_index=None)

        for project in self.available_projects:
            self.assign_plan_projects_checklist.add_option(
                option_name=project,
                display_text=project,
                checked=False,
                at_index=None)

            self.assign_result_projects_checklist.add_option(
                option_name=project,
                display_text=project,
                checked=False,
                at_index=None)

        self.assign_user_checklist.set_focus(option_name=list(self.logs.keys())[0], set_check=True)
        self.slot_username_selected(list(self.logs.keys())[0])

        self.render_preview_text_edit()

    def slot_refresh_data_and_ui(self):
        self.init_data()
        self.slot_refresh_ui()

    def slot_username_selected(self, username):
        self.selected_username = username
        self.selected_plan_projects = self.logs[username].log_plan_projects
        self.assign_plan_projects_checklist.set_checked(self.selected_plan_projects, uncheck_others=True)
        self.selected_result_projects = self.logs[username].log_result_projects
        self.assign_result_projects_checklist.set_checked(self.selected_result_projects, uncheck_others=True)

    def slot_plan_project_selected(self):
        self.selected_plan_projects = self.assign_plan_projects_checklist.get_checked()
        self.logs[self.assign_user_checklist.get_checked()].log_plan_projects = \
            self.assign_plan_projects_checklist.get_checked()

        self.render_preview_text_edit()

    def slot_result_project_selected(self):
        self.selected_result_projects = self.assign_result_projects_checklist.get_checked()
        self.logs[self.assign_user_checklist.get_checked()].log_result_projects = \
            self.assign_result_projects_checklist.get_checked()

        self.render_preview_text_edit()

    def slot_submit(self):
        for user_name in self.logs:
            result, errors = WMRuntime.Database.Create.log(self.logs[user_name])
            log_content = "%s: %s" % (user_name, self.lang("succeed") if result else self.lang("fail"))
            log(log_content)
            # print(user_name, self.lang("succeed") if result else self.lang("fail"))
            if errors:
                for error in errors:
                    log_content = "SQL ERROR " % error
                    log_err(log_content)
                    # print("SQL ERROR ", error)

    def slot_submit_and_exit(self):
        self.slot_submit()
        self.slot_close()

    def get_logs(self):
        if self.current_user.user_account in self.organization:
            where_clause = " WHERE log_username in (%s) and log_date = '%s'" % (
                ",".join(
                    ["'" + user_name + "'" for user_name in self.organization[self.current_user.user_account]]),
                NKDate.date_to_str(self.detail_time.date())
            )
            result, errors = WMRuntime.Database.Retrieve.log(where_clause=where_clause)
            # print(self.lang("download", "data", "result", ":"),
            #       self.lang("succeed") if len(str(result)) > 15 else str(result))
            log_content = "%s:%s" % (self.lang("download", "data", "result"),
                                     self.lang("succeed") if len(str(result)) > 15 else str(result))
            log(log_content)

            logs = {}
            for record in result:
                logs[record["log_username"]] = WMLog(
                    log_username=record["log_username"],
                    log_username_chinese=str(record["log_username_chinese"]),
                    log_date=record["log_date"],
                    log_plan_projects=eval(record["log_plan_projects"]),
                    log_plan_handler=str(record["log_plan_handler"]),
                    log_plan_handler_chinese=str(record["log_plan_handler_chinese"]),
                    log_result_projects=eval(record["log_result_projects"]),
                    log_result_handler=str(record["log_result_handler"]),
                    log_result_handler_chinese=str(record["log_result_handler_chinese"])
                )
            return logs
        else:
            # print("You are not leader!!!")
            log_content = "You are not leader!!!"
            log_warn(log_content)
            return None

    @staticmethod
    def get_available_projects():
        with open(WMRuntime.Path.proj_path, "r") as f:
            available_projects = yaml.load(f, Loader=yaml.FullLoader)
        return available_projects

    @staticmethod
    def get_organization():
        with open(WMRuntime.Path.org_path, "r") as f:
            organization = yaml.load(f, Loader=yaml.FullLoader)
        return organization
