# coding=utf8
# Copyright (c) lovICer 2022/7/29 in gtec_media_dev


from NikoKit.NikoLib.NKCmd import NKCmdServer


def load():
    pass


def unload():
    pass


def run_maya_launcher():
    GMLMayaLauncher()


def awake_handler(target):
    if target.lower().startwicth("mayalauncher"):
        run_maya_launcher()


class GMLMayaLauncher:
    def __init__(self):
        self.cmd_server = None

    def init_data(self):
        self.cmd_server = NKCmdServer()

