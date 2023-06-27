# coding=utf8
# Copyright (c) lovICer 2022/7/21 in gtec_media_dev


import datetime
import os

from NikoKit.NikoStd.NKDataStructure import NKDataStructure


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
        self.log_plan_projects = log_plan_projects
        self.log_plan_handler = log_plan_handler
        self.log_plan_handler_chinese = log_plan_handler_chinese
        self.log_result_projects = log_result_projects
        self.log_result_handler = log_result_handler
        self.log_result_handler_chinese = log_result_handler_chinese


def login_in_gml_db():
    import mysql.connector

    conn = mysql.connector.connect(host='10.10.20.4',
                                   port=3306,
                                   user='GML',
                                   password='GML_PASSWD',
                                   db='GMLauncher')
    cur = conn.cursor(dictionary=True)
    return conn, cur


def gml_db_query(sql_str):
    gml_conn, gml_cur = login_in_gml_db()

    gml_cur.execute(sql_str)
    result = gml_cur.fetchall()
    gml_cur.close()
    gml_conn.close()

    if isinstance(result, list):
        for line in result:
            for column in line.keys():
                try:
                    line[column] = eval(line[column].decode())
                except:
                    pass
                if line[column] == "None":
                    line[column] = eval(line[column])
                if isinstance(line[column], str) \
                        and line[column].startswith("[") \
                        and line[column].endswith("]"):
                    line[column] = eval(line[column])

    return result


def get_logs(log_dates=None):
    if not log_dates:
        sql_str = '''
                SELECT *
                FROM Plugin_WorkforceMonitor
                ORDER BY log_username, log_date
                '''
    else:
        date_begin, date_end = min(log_dates), max(log_dates)
        sql_str = '''
                SELECT *
                FROM Plugin_WorkforceMonitor
                WHERE log_date >= %s and log_date <= %s
                ORDER BY log_username, log_date
                ''' % (date_begin, date_end)
    # else:
    #     sql_str = '''
    #             SELECT *
    #             FROM Plugin_WorkforceMonitor
    #             WHERE log_date in (%s)
    #             ORDER BY log_username, log_date
    #             ''' % ",".join(["'" + date_to_str(date) + "'" for date in log_dates])

    result = gml_db_query(sql_str)

    logs = {}

    for record in result:
        logs[record["log_username"] + "/" + date_to_str(record["log_date"])] = WMLog(
            log_username=record["log_username"],
            log_username_chinese=record["log_username_chinese"],
            log_date=record["log_date"],
            log_plan_projects=record["log_plan_projects"],
            log_plan_handler=record["log_plan_handler"],
            log_plan_handler_chinese=record["log_plan_handler_chinese"],
            log_result_projects=record["log_result_projects"],
            log_result_handler=record["log_result_handler"],
            log_result_handler_chinese=record["log_result_handler_chinese"],
        )

    return logs


def get_users_info(users=None):
    if not users:
        sql_str = '''
                SELECT *
                FROM User
                '''
    else:
        sql_str = '''
                SELECT *
                FROM User
                WHERE user_account in (%s)
                ''' % ",".join(["'" + user + "'" for user in users])

    result = gml_db_query(sql_str)

    users_info = {}
    for record in result:
        users_info[record["user_account"]] = {}
        users_info[record["user_account"]]["user_account"] = record["user_account"]
        if isinstance(record["user_last_name"], str) and isinstance(record["user_first_name"], str):
            users_info[record["user_account"]]["username_cn"] = record["user_last_name"] + record["user_first_name"]
        else:
            if isinstance(record["user_last_name"], str):
                users_info[record["user_account"]]["username_cn"] = record["user_last_name"]

        if record["user_ou_list"]:
            users_info[record["user_account"]]["user_department"] = ou_to_department(record["user_ou_list"][0])
        else:
            users_info[record["user_account"]]["user_department"] = None
        users_info[record["user_account"]]["user_cgt_account"] = record["user_cgt_account"]
        users_info[record["user_account"]]["user_cgt_available_projects"] = record["user_cgt_available_projects"]

    return users_info


def date_to_str(target_date):
    if not target_date:
        return ""
    return target_date.strftime("%Y-%m-%d")


def str_to_date(target_date_str):
    import datetime

    if not target_date_str:
        return None
    return datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()


def ou_to_department(ou):
    ou_data = {
        "Animation": "动画",
        "Art": "美术",
        "Asset": "资产",
        "Commercial": "商务",
        "Domestic_marketing": "国内市场",
        "FD": "财务",
        "Fx": "特效",
        "Game": "游戏",
        "Light": "灯光",
        "Producer": "制片",
        "Rig": "绑定",
        "Script": "编剧",
        "Storyboard": "动态分镜",
        "TD": "技术",
        "administration": "行政",
        "meet": "会议室",
    }
    return ou_data[ou]


def allocate_sheet_data(logs):
    statistical_data = {"users": [],
                        "dates": [],
                        "projects": []}

    years_data = {}
    for username_date in logs:
        username = logs[username_date].log_username
        date = logs[username_date].log_date

        log_year = date.year
        log_month = date.month

        if log_year not in years_data:
            years_data[log_year] = {"users": [],
                                    "dates": [],
                                    "projects": [],
                                    "months": {}}
        log_year_data = years_data[log_year]

        if (log_year, log_month) not in log_year_data["months"]:
            log_year_data["months"][(log_year, log_month)] = {"users": [],
                                                              "dates": [],
                                                              "projects": []}
        log_month_data = log_year_data["months"][(log_year, log_month)]

        if username not in statistical_data["users"]:
            statistical_data["users"].append(username)
        if username not in log_year_data["users"]:
            log_year_data["users"].append(username)
        if username not in log_month_data["users"]:
            log_month_data["users"].append(username)

        if date not in statistical_data["dates"]:
            statistical_data["dates"].append(date)
        if date not in log_year_data["dates"]:
            log_year_data["dates"].append(date)
        if date not in log_month_data["dates"]:
            log_month_data["dates"].append(date)

        # print(logs)
        # print(username_date)

        for project in logs[username_date].log_result_projects:
            if project not in statistical_data["projects"]:
                statistical_data["projects"].append(project)
            if project not in log_year_data["projects"]:
                log_year_data["projects"].append(project)
            if project not in log_month_data["projects"]:
                log_month_data["projects"].append(project)

    return statistical_data, years_data


def assembly_sheet_data(data_dict, count_logs, users_info, units=None):
    sheet_data_list = []
    sheet_title = ""

    table_caption = ["部门", "负责人", "成员姓名", "时间", "出勤天数"]
    specific_project = ["LiZhi", "QingJia"]

    project_list = []
    for project in data_dict["projects"]:
        if project not in specific_project:
            project_list.append(project)

    project_list.sort()

    project_count = len(project_list)
    table_caption += ["（%s）占比" % project for project in project_list]

    date_list = []
    for date in data_dict["dates"]:
        date_list.append(date)
    date_list.sort()
    table_caption += [date_to_str(date) for date in date_list]

    date_count = len(date_list)

    sheet_data_list.append(table_caption)

    if date_list:
        current_date = date_list[-1]
        current_year = str(current_date.year)
        current_month = str(current_date.month)

        if units == "year":
            date_range = "%s年" % current_year
        elif units == "month":
            date_range = "%s.%s" % (current_year, current_month)
        else:
            if date_count == 1:
                date_range = date_to_str(current_date)
            else:
                date_range = "%s至%s" % (date_list[0], date_list[-1])

    else:
        return [], sheet_title

    if units:
        sheet_title = date_range
    else:
        sheet_title = "统计"

    for username in sorted(data_dict["users"]):
        user_projects_data = {}
        result_handlers = []

        user_data_list = [users_info[username]["user_department"],
                          [],
                          users_info[username]["username_cn"],
                          date_range,
                          0
                          ] + ["0.00%"] * project_count + [[]] * date_count
        plan_attendance = 0
        result_attendance = 0
        for date_idx, date in enumerate(date_list):
            workload = 1
            log_key = username + "/" + date_to_str(date)
            if log_key in count_logs:
                current_log = count_logs[log_key]
                plan_attendance += 1
                result_attendance += 1
                if current_log.log_result_handler_chinese not in result_handlers:
                    result_handlers.append(current_log.log_result_handler_chinese)
                log_projects = current_log.log_result_projects[:]
                if log_projects == ["LiZhi"] or log_projects == ["QingJia"]:
                    log_projects = []
                elif "LiZhi" in log_projects:
                    log_projects.remove("LiZhi")
                elif "QingJia" in log_projects:
                    result_attendance -= 0.5
                    log_projects.remove("QingJia")
                    workload = 0.5
                if log_projects:
                    date_project_str = ",".join(log_projects)
                else:
                    date_project_str = ""
                    result_attendance -= 1
                user_data_list[5 + project_count + date_idx] = date_project_str

                for log_project in log_projects:
                    if log_project not in user_projects_data:
                        user_projects_data[log_project] = 0
                    user_projects_data[log_project] += workload / len(log_projects)

        user_data_list[1] = ",".join(result_handlers)
        user_data_list[4] = str(result_attendance)

        project_idx = 0
        for project in sorted(data_dict["projects"]):
            if project not in specific_project:
                if project in user_projects_data:
                    user_data_list[5 + project_idx] = "%.2f" % (
                            user_projects_data[project] / result_attendance * 100) + "%"
                else:
                    user_data_list[5 + project_idx] = "0.00%"
                project_idx += 1
        sheet_data_list.append(user_data_list)

    return sheet_data_list, sheet_title


def create_sheet(workbook, sheet_data, count_logs, users_info, caption_format, units=None):
    sheet_data_list, sheet_title = assembly_sheet_data(sheet_data,
                                                       count_logs=count_logs,
                                                       users_info=users_info,
                                                       units=units)
    sheet_worksheet = workbook.add_worksheet(sheet_title)
    column_widths = [6] * len(sheet_data_list[0])
    for row, sheet_data_line in enumerate(sheet_data_list):
        for column, column_data in enumerate(sheet_data_line):
            if isinstance(column_data, list):
                column_data = ",".join(column_data)
            if row == 0:
                sheet_worksheet.write(row, column, column_data, caption_format)
            else:
                sheet_worksheet.write(row, column, column_data)
            if column_widths[column] < len(column_data):
                column_widths[column] = len(column_data)

    sheet_worksheet.set_row(row=0, height=30)

    for column, column_width in enumerate(column_widths):
        sheet_worksheet.set_column(first_col=column, last_col=column, width=1.5 * column_width)


def get_table_name():
    filename_list = os.listdir()
    workforce_nums = []
    for filename in filename_list:
        if filename.startswith("WorkforceMonitorDataExport") and filename.endswith(".xlsx"):
            fname, ext = os.path.splitext(filename)
            if fname == "WorkforceMonitorDataExport":
                workforce_nums.append(0)
            else:
                workforce_num = fname.replace("WorkforceMonitorDataExport", "")
                try:
                    workforce_nums.append(int(workforce_num))
                except:
                    pass
    if workforce_nums:
        table_name = "WorkforceMonitorDataExport%s.xlsx" % (max(workforce_nums) + 1)
    else:
        table_name = "WorkforceMonitorDataExport.xlsx"

    return table_name


def run(log_dates=None):
    count_logs = get_logs(log_dates=log_dates)
    users_info = get_users_info()

    statistical_data, years_data = allocate_sheet_data(count_logs)

    import xlsxwriter

    table_name = get_table_name()

    workbook = xlsxwriter.Workbook(table_name)

    caption_format = workbook.add_format({
        'bold': True,  # 字体加粗
        'align': 'center',  # 水平位置设置：居中
        'valign': 'vcenter',  # 垂直位置设置，居中
        'font_size': 10,  # '字体大小设置'
    })

    create_sheet(workbook=workbook,
                 sheet_data=statistical_data,
                 count_logs=count_logs,
                 users_info=users_info,
                 caption_format=caption_format,
                 units=None)

    for year in sorted(years_data.keys()):
        create_sheet(workbook=workbook,
                     sheet_data=years_data[year],
                     count_logs=count_logs,
                     users_info=users_info,
                     caption_format=caption_format,
                     units="year")
        for month in sorted(years_data[year]["months"].keys()):
            create_sheet(workbook=workbook,
                         sheet_data=years_data[year]["months"][month],
                         count_logs=count_logs,
                         users_info=users_info,
                         caption_format=caption_format,
                         units="month")
    workbook.close()

    try:
        os.startfile(table_name)
    except:
        os.system("start explorer /select, %s" % __file__)


if __name__ == '__main__':
    run()
