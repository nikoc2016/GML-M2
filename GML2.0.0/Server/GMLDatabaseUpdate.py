import sys

sys.path.append(r"/home/data/smb/gml/lib")
from NikoKit.NikoLib.NKActiveDirectory import NKAd
from NikoKit.NikoLib.NKDatabase import NKMySQLConnector
from NikoKit.NikoStd.NKDataStructure import NKDataStructure


class GVFActiveDirectory(NKAd):
    def __init__(self):
        super(GVFActiveDirectory, self).__init__(host="10.10.20.10",
                                                 username=r"gvfnew\administrator",
                                                 password="tech.1012",
                                                 search_base="OU=gvf_user,DC=gvfnew,DC=com")


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


class User(NKDataStructure):
    def __init__(self,
                 user_account=None,
                 user_last_name=None,
                 user_first_name=None,
                 user_group_list=None,
                 user_ou_list=None,
                 user_account_control=None,
                 user_cgt_account=None,
                 user_cgt_password=None,
                 user_cgt_available_projects=None,
                 ):
        self.user_account = user_account
        self.user_last_name = user_last_name
        self.user_first_name = user_first_name
        self.user_group_list = user_group_list
        self.user_ou_list = user_ou_list
        self.user_account_control = user_account_control
        self.user_cgt_account = user_cgt_account
        self.user_cgt_password = user_cgt_password
        self.user_cgt_available_projects = user_cgt_available_projects
        super(User, self).__init__()

    def p_key(self):
        return self.user_account


def main():
    print("Get users from Active Directory...")
    conn = GMLDBConnector(host="10.10.20.4")
    users = GVFActiveDirectory().get_users()
    try:
        print("Users: " + str(users)[:40])
    except:
        print("Users: " + str(users))
    gml_users = []
    sql_data = []
    for username, user in users.items():
        new_user = User(user_account=str(user.person.sAMAccountName),
                        user_last_name=str(user.person.sn),
                        user_first_name=str(user.person.givenName),
                        user_group_list=str(user.groups),
                        user_ou_list=str(user.ous),
                        user_account_control=int(str(user.person.userAccountControl)),
                        user_cgt_account=None,
                        user_cgt_password=None,
                        user_cgt_available_projects=None)
        gml_users.append(new_user)
        sql_data.append([new_user.user_account,
                         new_user.user_last_name,
                         new_user.user_first_name,
                         new_user.user_group_list,
                         new_user.user_ou_list,
                         new_user.user_account_control])

    fields = ["user_account",
              "user_last_name",
              "user_first_name",
              "user_group_list",
              "user_ou_list",
              "user_account_control"]

    insert_statement = conn.build_insert_clause(table="User",
                                                fields=fields,
                                                values=["%s"] * len(fields),
                                                on_duplicate_ignore_fields=["user_account"])

    print("Inserting to GML-Database")
    result, errors = conn.write_multiple_times(insert_statement, sql_data)

    if errors:
        for error in errors:
            print(error)
    else:
        print("Insertion succeed")


if __name__ == "__main__":
    import schedule

    schedule.every(30).seconds.do(main)
    main()
    while True:
        schedule.run_pending()
