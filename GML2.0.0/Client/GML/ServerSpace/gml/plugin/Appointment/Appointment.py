# coding=utf8
# Copyright (c) lovICer 2022/7/25 in gtec_media_dev
import os
import threading
from functools import partial

import schedule

from GML_Runtime import GMLRuntime
from NikoKit.NikoQt.NQApplication import NQRuntime
from NikoKit.NikoStd.NKVersion import NKVersion


def load():
    GMLRuntime.Plugin.Appointment = AppointmentRuntime
    AppointmentRuntime.App = Appointment()
    GMLRuntime.Signals.tick_passed.connect(AppointmentRuntime.App.run_pending)


def unload():
    if GMLRuntime.Plugin.Appointment:
        GMLRuntime.Signals.tick_passed.disconnect(AppointmentRuntime.App.run_pending)
        AppointmentRuntime.App = None


class AppointmentRuntime(NQRuntime):
    App = None


class Appointment:

    def __init__(self):
        super(Appointment, self).__init__()

        # API Info and Settings (Fill in here)
        self.name = "Appointment"
        self.version = NKVersion("1.0.0")
        self.api_version = "1"
        self.auto_start = True

        # FLags for Main to Control (Check here repeatedly for flow control)
        self.stop_flag = False
        self.pause_flag = False

        # Status for GUI to access (Put value here for GUI to render)
        self.log_lines = []
        self.errors = []
        self.log_progress_bar_precentage = 0
        self.log_progress_bar_title = ""
        self.log_progress_bar_color = 0  # 0-Normal 1-Green 2-Red

        # Declare thread death here
        self.isDead = False
        self.register_schedules()

    def register_schedules(self):
        schedule.every().day.at("10:00").do(self.awake, "WorkforceMonitor")
        schedule.every().day.at("18:00").do(self.awake, "WorkforceMonitor")

    def run_pending(self):
        schedule.run_pending()

    def awake(self, plugin_name):
        GMLRuntime.Signals.awake.emit(plugin_name)
