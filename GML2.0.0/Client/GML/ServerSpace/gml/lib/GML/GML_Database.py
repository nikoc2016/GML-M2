from NikoKit.NikoLib.NKDatabase import NKMySQLConnector
from NikoKit.NikoStd.NKDataStructure import NKDataStructure
from NikoKit.NikoStd.NKTime import TimeMeasure
from NikoKit.NikoLib.NKActiveDirectory import NKAd
from GML_Runtime import GMLRuntime


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


class GVFActiveDirectory(NKAd):
    def __init__(self):
        super(GVFActiveDirectory, self).__init__(host="10.10.20.10",
                                                 username=r"gvfnew\administrator",
                                                 password="tech.1012",
                                                 search_base="OU=gvf_user,DC=gvfnew,DC=com")


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


class Retrieve:
    @staticmethod
    @TimeMeasure.time_measure_decorator
    def users(fields=None,
              where_clause="",
              sort_field="user_account",
              sort_asc=True):
        sql_line = GMLRuntime.Database.Conn.build_select_clause(fields)
        sql_line += " FROM User "
        sql_line += where_clause
        sql_line += GMLRuntime.Database.Conn.build_order_clause(sort_field, sort_asc)

        result, errors = GMLRuntime.Database.Conn.query(sql_line)

        return GMLRuntime.Database.Conn.no_binary(result), errors


class Create:
    @staticmethod
    @TimeMeasure.time_measure_decorator
    def users_on_duplicate_update(user_obj):
        fields = []
        values = []
        for field, value in vars(user_obj).items():
            if value is not None:
                fields.append(field)
                values.append(value)
        dummy_values = ["%s" for i in range(len(fields))]
        insert_clause = GMLRuntime.Database.Conn.build_insert_clause(table="User",
                                                                     fields=fields,
                                                                     values=dummy_values,
                                                                     on_duplicate_ignore_fields=["user_account"])

        result, errors = GMLRuntime.Database.Conn.write(sql_line=insert_clause, sql_data=values)
        return GMLRuntime.Database.Conn.no_binary(result), errors


class Update:
    pass


class Delete:
    pass
