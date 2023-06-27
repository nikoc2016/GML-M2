import traceback

from GML_Database import User
from NikoKit.NikoStd.NKPrint import eprint
from GML_Runtime import GMLRuntime


class Feature:
    @staticmethod
    def refresh_current_user():
        current_user_records, errors = GMLRuntime.Database.Retrieve.users(
            where_clause=" WHERE user_account='%s' " % GMLRuntime.Machine.username
        )
        if errors:
            print("CurrentUser Failure")
            eprint("".join(errors))
        else:
            user = User(user_account=GMLRuntime.Machine.username)
            if current_user_records:
                user = User(**current_user_records[0])

            GMLRuntime.Data.current_user = user
            GMLRuntime.Signals.user_updated.emit()

    @staticmethod
    def refresh_all_users():
        user_records, errors = GMLRuntime.Database.Retrieve.users()
        if errors:
            print("GetAllUser Failure")
            eprint("".join(errors))
        else:
            GMLRuntime.Data.all_users = {}
            for user in user_records:
                user_obj = User(user_account=user["user_account"],
                                user_last_name=user["user_last_name"],
                                user_first_name=user["user_first_name"],
                                user_group_list=user["user_group_list"],
                                user_ou_list=user["user_ou_list"],
                                user_account_control=user["user_account_control"],
                                user_cgt_account=user["user_cgt_account"],
                                user_cgt_password=user["user_cgt_password"],
                                user_cgt_available_projects=user["user_cgt_available_projects"])
                GMLRuntime.Data.all_users[user["user_account"]] = user_obj
