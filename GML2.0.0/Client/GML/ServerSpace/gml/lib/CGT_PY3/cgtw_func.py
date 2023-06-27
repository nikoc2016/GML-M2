# coding=utf8
# Copyright (c) 2019 GVF

import sys
#
# sys.path.append(r"c:/cgteamwork/bin/base")
from CGT_PY3 import cgtw2


def login_in_cgtw(ip="10.10.20.13", user="passenger", password="123456"):
    """

    Args:
        ip:
        user:
        password:

    Returns:

    """

    t_tw = cgtw2.tw(ip, user, password)
    return t_tw


def get_account_name(t_tw):
    id_list = t_tw.info.get_id('public', 'account', [['account.account', '=', get_current_account(t_tw)]])
    return t_tw.info.get('public', 'account', id_list, ['account.name'])[0]['account.name']


def get_current_account(t_tw):
    """
    Get the current CgTeamWork account
    Args:
        t_tw(object): The CgTeamWork account instance

    Returns:
        (unicode): The current CgTeamWork account

    """
    return t_tw.login.account()


def get_account_id(t_tw):
    """
    Get the current CgTeamWork account' id
    Args:
        t_tw(object): The CgTeamWork account instance

    Returns:

    """
    return t_tw.login.account_id()


def get_department(t_tw):
    """

    Args:
        t_tw(object): The CgTeamWork account instance

    Returns:
            (str): The department of the user
    """
    id_list = t_tw.info.get_id('public', 'account', [['account.account', '=', get_current_account(t_tw)]])
    return t_tw.info.get('public', 'account', id_list, ['account.department'])[0]['account.department']


def get_shot_related_task_id(t_tw, db, module, scene, shot):
    """
    Get the related task id specified by scene and shot
    Args:
        t_tw(object): The CgTeamWork account instance
        db(str): The database of current project
        module(str): The current module
        scene(str): The specified scene
        shot(str): The specified shot

    Returns:
        (list): The related task id list
    """
    return t_tw.task.get_id(db, module, [["shot.shot", "=", shot], 'and', ['eps.eps_name', '=', scene]])


def get_asset_related_task_id(t_tw, db, module, asset_name):
    """
    Get the related task id specified by asset_name
    Args:
        t_tw(object): The CgTeamWork account instance
        db(str): The database of current project
        module(str): The current module
        asset_name(str): The specified asset's name

    Returns:
        (list): The related task id list
    """
    return t_tw.task.get_id(db, module, [["asset.asset_name", "=", asset_name]])


def specified_task_info(t_tw, db, module, task_id_list, filter_list=None):
    """
    Get the specified info of the given task id
    Args:
        t_tw(object): The CgTeamWork account instance
        db(str): The database of current project
        module(str): The current module
        task_id_list(list): The given id list
        filter_list(list): The section list to specify what info need to be given


    Returns:
        tasks_info(list):
    """
    if module == u"shot":
        certain_filter = filter_list if filter_list else ['shot.shot', 'eps.eps_name', 'task.pipeline', 'task.artist',
                                                          'shot.frame', 'task.start_date', 'task.end_date',
                                                          'task.remaining_day',
                                                          'task.status']
    elif module == u"asset":
        certain_filter = filter_list if filter_list else ['asset.cn_name', 'asset.asset_name', 'task.pipeline',
                                                          'task.artist',
                                                          'task.start_date', 'task.end_date', 'task.remaining_day',
                                                          'task.status']

    tasks_info = t_tw.task.get(db, module, task_id_list, certain_filter)
    return tasks_info


def get_all_tasks_id(t_tw, project_db, modules):
    """
    get all tasks from the specified project
    Args:
        t_tw:object
        project_db:str - project db name
        modules:str - Modules category ["shot" or "asset"]

    Returns:list - all tasks id

    """
    id_lists = t_tw.task.get_id(project_db, modules, [])
    return id_lists


def get_specify_tasks_id(t_tw, project_db, modules, pipeline):
    """
    get all tasks from the specified project
    Args:
        t_tw:object
        project_db:str - project db name
        modules:str - Modules category ["shot" or "asset"]
        pipeline:list

    Returns:list - all tasks id

    """
    id_lists = t_tw.task.get_id(project_db, modules, [pipeline])
    return id_lists


def get_artist_task_info(t_tw, db, module, account, filter_list=None):
    """
    Get the scene, shot, pipeline, artist, frame, task's beginning and end date,
    remaining day, status of every task
        t_tw(object): The CgTeamWork account instance
        db(str): The database of current project
        module(str): The current module
        account(str): The artist who assigned to the tasks
        filter_list(list): The section list to specify what info need to be given
    Returns:
        (list): The tasks' list including the info mentioned above
    """

    if module == u"shot":
        certain_filter = filter_list if filter_list else ['shot.shot', 'eps.eps_name', 'task.pipeline', 'task.artist',
                                                          'shot.frame', 'task.start_date', 'task.end_date',
                                                          'task.remaining_day',
                                                          'task.status']
        try:
            id_list = t_tw.task.get_id(db, module, [['task.account', 'has', account]])
            return t_tw.task.get(db, module, id_list,
                                 certain_filter, '5000', ['eps.eps_name'])
        except AttributeError:
            return []
    elif module == u"asset":
        certain_filter = filter_list if filter_list else ['asset.cn_name', 'asset.asset_name', 'task.pipeline',
                                                          'task.artist',
                                                          'task.start_date', 'task.end_date', 'task.remaining_day',
                                                          'task.status', 'asset.type_name']
        try:
            id_list = t_tw.task.get_id(db, module, [['task.account', '=', account]])
            return t_tw.task.get(db, module, id_list,
                                 certain_filter, '5000')
        except AttributeError:
            return []
    return []


def get_all_projects():
    """
    Get all existed projects

    Returns:
        project_data(list): The dictionary list includes the projects' database and code
    """
    t_tw = login_in_cgtw()
    project_id = t_tw.info.get_id('public', 'project',
                                  [["project.status", "!=", "Lost"], "and",
                                   ["project.status", "!=", "Close"]])
    project_data = t_tw.info.get('public', 'project', project_id,
                                 ['project.database', 'project.code'])
    return project_data


def get_allowed_projects(t_tw):
    """
    Get projects allowed to access by current account
    Args:
        t_tw(object): The CgTeamWork account instance

    Returns:
        project_data(list): The list includes the projects' database and code
    """
    account_id = get_account_id(t_tw)
    id_list = t_tw.info.get_id('public', 'account', [["account.id", "=", account_id]])
    allow_data = t_tw.info.get('public', 'account', id_list, ["account.project_permission"])

    allow_project = ""
    if len(allow_data) != 0 and "account.project_permission" in allow_data[0].keys():
        allow_project = allow_data[0]["account.project_permission"]
    filter_list = [["project.status", "!=", "Lost"], "and", ["project.status", "!=", "Close"]]
    if allow_project == "":
        return []
    if allow_project.lower() != "all":
        filter_list = filter_list + ["and", ["project.code", "in", allow_project.split(",")]]
    project_id_list = t_tw.info.get_id('public', 'project', filter_list)
    project_data = t_tw.info.get('public', 'project', project_id_list, ["project.database", "project.code"])
    return project_data


def get_note_id(t_tw, db, module, task_id):
    """

    Args:
        t_tw(object):The CgTeamWork account instance
        db(str): The current database
        module(str): The specified module
        task_id(str): The given task's id

    Returns:

    """
    note_id_list = t_tw.note.get_id(db,
                                    [['module', '=', module], 'and', ['module_type', '=', 'task'], 'and',
                                     ['#task_id', '=', task_id]])
    return note_id_list


def get_task_note(t_tw, db, note_id):
    """

    Args:
        t_tw(object): The CgTeamWork account instance
        db(str): The current database
        note_id(unicode/list): The notes' id of the specified task

    Returns:
        note_info(dict/list): The content, creating time and editor of the note(s)
    """
    if isinstance(note_id, unicode):
        note_info = t_tw.note.get(db, [note_id],
                                  ['text', 'create_time', 'create_by'])[0]
    elif isinstance(note_id, list):
        note_info = t_tw.note.get(db, note_id,
                                  ['text', 'create_time', 'create_by'])
    return note_info


def get_history_id(t_tw, db, module, task_id):
    """

    Args:
        t_tw(object):The CgTeamWork account instance
        db(str): The current database
        module(str): The specified module
        task_id(str): The given task's id

    Returns:
        history_id_list(list): The histories' id of the specified task
    """
    history_id_list = t_tw.history.get_id(db,
                                          [['module', '=', module], 'and', ['module_type', '=', 'task'], 'and',
                                           ['#task_id', '=', task_id]])
    return history_id_list


def get_task_history(t_tw, db, history_id_list):
    """
    Get the histories' info list ordered by creating time
    Args:
        t_tw(object): The CgTeamWork account instance
        db(str): The current database
        history_id_list(list): The histories' id of the specified task

    Returns:
        history_info(list): The histories' info list including content, status, creating time and editor
    """
    history_info = t_tw.history.get(db, history_id_list, ['time', 'status', 'text', 'create_by', 'file'],
                                    order_list=['create_time'])
    return history_info


def get_link_assets_info(t_tw, db, module, task_id, filter_list=['asset.cn_name', 'asset.type_name', 'asset.asset_name',
                                                                 'asset.pid_PVCSBDVX_SBFO_BWES_OTBW_DOOERPXPBOXQ']):
    """
    Get assets' info linked to the specified task
    Args:
        t_tw(object):The CgTeamWork account instance
        db(str): The current database
        module(str): The specified module
        task_id(unicode): The id of specified task
        filter_list(list): The section list to specify what info need to

    Returns:

    """
    link_id_list = t_tw.link.get_asset(db, module, 'task', task_id)

    link_info = t_tw.info.get(db, 'asset', link_id_list, filter_list)
    return link_info


def set_task_info(t_tw, db, module, task_id, update_data):
    """
    Update the specified tasks' data
    Args:
        t_tw(object):The CgTeamWork account instance
        db(str): The current database
        module(str): The specified module
        task_id(list): The id list of specified task
        update_data(dict): The data to update. Example: {'task.startframe':'101', 'task.status':'Work'}

    Returns:
        (bool): True for success, False otherwise

    """
    if not isinstance(task_id, list):
        task_id = [task_id]
    return t_tw.task.set(db, module, task_id, update_data)


def excute_action(t_tw, module, project_db, action, t_data, t_type):
    """
    notify cgtw client excute action
    Args:
        t_tw:The CgTeamWork account instance
        module:The specified module
        project_db:The current database
        action:script_action
        t_data:dict - {"task_id": task_id,
                      "db":project_db,
                      "module": module,
                      "module_type": "task",
                      "filebox_data": {"#id": "id"},
                      "file_path_list": [path]}
        t_type:str

    Returns:

    """
    t_tw.send_local_http(project_db, module, action, t_data, t_type)


def get_submit_filebox_info(t_tw, db, module, task_id):
    """
    get file box info
    Args:
        t_tw:The CgTeamWork account instance
        db:The current database
        module:The specified module
        task_id:str - task_id

    Returns:dict - file box_info

    """
    return t_tw.task.get_submit_filebox(db, module, task_id)


def notify_artist(tw, project_db, module, task_id, artist, product_artist, pipeline, asset_name=None, scene=None,
                  shot=None, content=""):
    t_account = tw.info.get_id("public", "account", [["account.name", "=", artist]])
    if module == "shot":
        tw.send_msg(project_db, module, "task", task_id, t_account,
                    u"艺术家：{}<br/>场次：{}<br/>镜头：{}<br/>阶段：{} <br/>已发布新的文件，上下游相关制作人员请注意! <br/>更新内容：{}".format(
                        product_artist, scene, shot,
                        pipeline, content))
    elif module == "asset":
        tw.send_msg(project_db, module, "task", task_id, t_account,
                    u"艺术家：{}<br/>资产名：{}<br/>阶段：{} <br/>已发布新的文件，上下游相关制作人员请注意!<br/> 更新内容：{}".format(product_artist,
                                                                                                  asset_name, pipeline,
                                                                                                  content))


def submit_file(t_tw, db, module, task_id, path_list):
    return t_tw.task.submit(db, module, task_id, path_list)


def get_filebox_info(tw, db, module, task_id, filebox_sign):
    filebox_id = tw.task.get_sign_filebox(db, module, task_id, filebox_sign)
    if filebox_id:
        filebox_info = tw.task.get_filebox(db, module, task_id, filebox_id["#id"])
        return filebox_info
