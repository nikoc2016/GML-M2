from PySide2.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QLabel

import GML
from GML_Qt.Widgets.SuperWidgets.GML_LaunchPad import GML_LaunchPad
from GML_Qt.Widgets.LaunchWidget import GML_LaunchWidget


class GML_MainWindow(GML_LaunchPad):
    def __init__(self):
        super(GML_MainWindow, self).__init__(
            inline=False,
            widget_name="GML_MainWindow",
            widget_title="MainWindow"
        )
        self.main_lay = QHBoxLayout()
        self.main_lay.setMargin(0)
        # self.temp_btn = QTextEdit()
        # self.main_lay.addWidget(self.temp_btn)
        # self.setLayout(self.main_lay)
        self.resize(1200, 800)
        self.setWindowIcon(GML.Qt.Icon.get_pixmap("GParasite_Logo"))
        self.test_btn = QPushButton("reset")
        self.test2_btn = QPushButton("skin")
        self.insert_dialog("Launch", GML.Qt.Icon.get_icon("GParasite_Logo"), GML_LaunchWidget.GML_LaunchWidget(inline=True, widget_name="Launch_Widget", widget_title="Launch_Widget"))
        self.insert_dialog("test1", GML.Qt.Icon.get_icon("GParasite_Logo"), QLabel("aas"))
        self.insert_dialog("test2", GML.Qt.Icon.get_icon("btn_reset"), self.test_btn)
        self.insert_dialog("test3", GML.Qt.Icon.get_icon("btn_skin"), self.test2_btn)

        self.show()

        GML.Cmd.register_command("MainWindow", " -h for detail")
        GML.Qt.Service.Signals.has_new_command.connect(self.slot_command_handler)

    def slot_command_handler(self, command_id, command_line):
        return_str = ""
        if command_line.startswith("MainWindow"):
            command_parts = command_line.split()
            if command_parts[1] == "-h":
                return_str += ("MainWindow show [-dialog_id]\n"
                               "MainWindow hide [-dialog_id]")
                GML.Cmd.finish_command(command_id=command_id,
                                       result_sign=GML.Cmd.RESULT_SIGN_GOOD,
                                       result_detail=str(return_str))
            else:
                a = int(command_parts[1])
                b = int(command_parts[2])
                c = a + b
                GML.Cmd.finish_command(command_id=command_id,
                                       result_sign=GML.Cmd.RESULT_SIGN_GOOD,
                                       result_detail=str(c))
