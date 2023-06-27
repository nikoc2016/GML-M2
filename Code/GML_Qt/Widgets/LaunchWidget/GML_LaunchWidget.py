# coding=utf8
# Copyright (c) lovICer 2021/6/24 GVF
import sys
import uuid

from PySide2.QtCore import QSize

import GML

from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QLabel, QWidget, QStackedWidget, \
    QApplication

from GML_Qt.Widgets.SuperWidgets.GML_Widget import GML_Widget
from GML_Qt.Widgets.CarouselWidget.GML_CarouselWidget import GML_Carousel


class GML_LaunchWidget(GML_Widget):
    def __init__(self,
                 inline,
                 widget_name,
                 widget_title
                 ):
        super(GML_LaunchWidget, self).__init__(
            inline=inline,
            widget_name=widget_name,
            widget_title=widget_title
        )

        self.widget_id = str(uuid.uuid4())

        self.widget_main_lay = None

        self.left_lay = None
        self.right_lay = None

        self.user_lay = None
        self.user_btn = None

        self.banner_widget = None

        self.used_tool_lay = None
        self.used_tool_label = None
        self.used_tool_widget = None

        self.tool_label_lay = None
        self.tool_label = None
        self.tool_btn = None
        self.tool_widget = None
        self.tool_lay = None
        self.group_btn_lay = None
        self.group_stackwidget = None

        self.mix_btn = None
        self.lgt_btn = None
        self.ass_btn = None
        self.ani_btn = None
        self.lay_btn = None
        self.vfx_btn = None

        self.task_list = None
        self.new_message = None
        self.launch_style = None

        self.construct()

    def construct(self):
        self.widget_main_lay = QHBoxLayout()

        self.left_lay = QVBoxLayout()
        self.right_lay = QVBoxLayout()

        self.user_lay = QHBoxLayout()
        ks = "lasdasd\nsdfds"
        self.user_btn = QPushButton(ks)
        self.user_btn.setFixedSize(100, 50)
        self.user_btn.setIcon(GML.Qt.Icon.get_pixmap("GParasite_Logo"))
        self.user_btn.setIconSize(QSize(25, 25))
        self.user_btn.setProperty("class", "user_btn")

        self.banner_widget = GML_Carousel([GML.Qt.Icon.get_pixmap("test1"), GML.Qt.Icon.get_pixmap("test2"),
                                           GML.Qt.Icon.get_pixmap("test3")])

        self.used_tool_lay = QHBoxLayout()
        self.used_tool_label = QLabel("Used Tool")
        self.used_tool_widget = QWidget()

        self.tool_label_lay = QHBoxLayout()
        self.tool_label = QLabel("Tool")
        self.tool_btn = QPushButton()
        self.tool_widget = QWidget()
        self.tool_lay = QVBoxLayout()
        self.group_btn_lay = QHBoxLayout()
        self.group_stackwidget = QStackedWidget()

        self.mix_btn = QPushButton()
        self.mix_btn.setProperty("class", "group_btn")
        self.mix_btn.setFixedWidth(40)
        self.mix_btn.setFixedHeight(20)
        self.lgt_btn = QPushButton()
        self.lgt_btn.setProperty("class", "group_btn")
        self.lgt_btn.setFixedWidth(40)
        self.lgt_btn.setFixedHeight(20)
        self.ass_btn = QPushButton()
        self.ass_btn.setProperty("class", "group_btn")
        self.ass_btn.setFixedWidth(40)
        self.ass_btn.setFixedHeight(20)
        self.ani_btn = QPushButton()
        self.ani_btn.setProperty("class", "group_btn")
        self.ani_btn.setFixedWidth(40)
        self.ani_btn.setFixedHeight(20)
        self.lay_btn = QPushButton()
        self.lay_btn.setProperty("class", "group_btn")
        self.lay_btn.setFixedWidth(40)
        self.lay_btn.setFixedHeight(20)
        self.vfx_btn = QPushButton()
        self.vfx_btn.setProperty("class", "group_btn")
        self.vfx_btn.setFixedWidth(40)
        self.vfx_btn.setFixedHeight(20)

        self.task_list = QTextEdit()
        self.new_message = QTextEdit()

        self.user_lay.addWidget(self.user_btn)
        self.user_lay.addStretch()

        self.used_tool_lay.addWidget(self.used_tool_label)

        self.tool_label_lay.addWidget(self.tool_label)
        self.tool_label_lay.addStretch()
        self.tool_label_lay.addWidget(self.tool_btn)

        self.group_btn_lay.addWidget(self.mix_btn)
        self.group_btn_lay.addWidget(self.lgt_btn)
        self.group_btn_lay.addWidget(self.ass_btn)
        self.group_btn_lay.addWidget(self.ani_btn)
        self.group_btn_lay.addWidget(self.lay_btn)
        self.group_btn_lay.addWidget(self.vfx_btn)
        self.group_btn_lay.addStretch()

        self.tool_lay.addLayout(self.group_btn_lay)
        self.tool_lay.addWidget(self.group_stackwidget)

        self.left_lay.addLayout(self.user_lay)
        self.left_lay.addWidget(self.banner_widget)
        self.left_lay.addLayout(self.used_tool_lay)
        self.left_lay.addWidget(self.used_tool_widget)
        self.left_lay.addLayout(self.tool_label_lay)
        self.left_lay.addWidget(self.tool_widget)

        self.right_lay.addWidget(self.task_list)
        self.right_lay.addWidget(self.new_message)

        self.widget_main_lay.addLayout(self.left_lay)
        self.widget_main_lay.addLayout(self.right_lay)

        self.tool_widget.setLayout(self.tool_lay)
        self.setLayout(self.widget_main_lay)

        self.launch_style = """
        
        .user_btn {
            border-radius:15px;
            border:none;
            font-size:13px;
        }
        
        """

        self.setStyleSheet(self.launch_style)


