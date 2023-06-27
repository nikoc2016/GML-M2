import traceback

from PySide2.QtCore import Qt

from CGT_PY3 import cgtw_func
from GML_Database import User
from NikoKit.NikoLib import NKLogger
from GML_Runtime import GMLRuntime
from NikoKit.NikoQt.NQKernel.NQGui.NQWindow import NQWindow
from NikoKit.NikoQt.NQKernel.NQGui.NQWindowLogin import NQWindowLogin

LOG_CHANNEL = "CGT_Login"


class CGTWLoginWindow(NQWindowLogin):
    @staticmethod
    def login_validator(username, password):
        tw = None
        allow_projects = None
        try:
            tw = cgtw_func.login_in_cgtw(user=username, password=password)
            project_data = cgtw_func.get_allowed_projects(tw)
            allow_projects = [project.get('project.code')
                              for project in project_data
                              if project.get('project.code') and project.get('project.database')
                              ]

            GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                            log_type=NKLogger.STD_OUT,
                                            log_context=f"CGTW Login Successfully\n")
        except Exception as e:
            if "unsupported operand type(s)" in str(e):
                GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                                log_type=NKLogger.STD_ERR,
                                                log_context=f"CGTW Login Failure: Wrong Username or Password\n")
            else:
                GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                                log_type=NKLogger.STD_ERR,
                                                log_context=f"CGTW Login Failure:\n {traceback.format_exc()} \n")
            return False

        if tw:
            user = User(user_account=GMLRuntime.Machine.username,
                        user_cgt_account=username,
                        user_cgt_password=password,
                        user_cgt_available_projects=str(allow_projects))

            result, errors = GMLRuntime.Database.Create.users_on_duplicate_update(user_obj=user)

            if errors:
                GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                                log_type=NKLogger.STD_ERR,
                                                log_context=f"CGTW -> SQL Failure\n{''.join(errors)}\n")
            else:
                GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                                log_type=NKLogger.STD_OUT,
                                                log_context=f"CGTW -> SQL Successfully\n")

            GMLRuntime.Data.cgtw_obj = tw
            GMLRuntime.Feature.refresh_current_user()

        return tw

    def __init__(self,
                 cgt_username="",
                 cgt_password="",
                 fast_login=True,
                 success_callback=None,
                 *args,
                 **kwargs):
        self.cgt_username = cgt_username
        self.cgt_password = cgt_password
        self.fast_login = fast_login

        super(CGTWLoginWindow, self).__init__(login_validator=self.login_validator,
                                              w_width=300,
                                              w_height=100,
                                              appdata_name="CGTWLogin",
                                              appdata_mgr=None,
                                              ignore_auto_login=False,
                                              require_username=True,
                                              require_password=True,
                                              allow_remember_me=False,
                                              allow_auto_login=False,
                                              success_callback=success_callback,
                                              *args,
                                              **kwargs)

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        super(CGTWLoginWindow, self).show()
        self.username_line_edit.setText(self.cgt_username)
        self.password_line_edit.setText(cgt_password)

        if fast_login:
            self.slot_login_button_clicked()

    def show(self):
        NQWindow.show(self)
