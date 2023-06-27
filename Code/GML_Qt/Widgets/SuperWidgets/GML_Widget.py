import uuid

from PySide2 import QtCore
from PySide2.QtCore import QSize
from PySide2.QtGui import Qt, QEnterEvent
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy

import GML

Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)


class GML_TitleBar(QWidget):
    def __init__(self, main_win):
        super(GML_TitleBar, self).__init__()
        self.main_win = main_win
        self.offset = None

        # GUI Component
        self.main_lay = None
        self.icon_label = None
        self.title_label = None
        self.min_btn = None
        self.max_reset_btn = None
        self.close_btn = None

        # Construct
        self.construct()

        # QSS
        self.apply_style_sheet()

        # Connect Signals
        self.connect_signals()

    def construct(self):

        self.main_lay = QHBoxLayout()

        # self.main_lay.setMargin(0)
        self.main_lay.setContentsMargins(5, 5, 5, 0)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("icon_label")
        self.icon_label.hide()
        self.title_label = QLabel()
        self.title_label.hide()
        self.title_label.setObjectName("title_label")
        self.min_btn = QPushButton()
        self.min_btn.setIcon(GML.Qt.Icon.get_icon("btn_min"))
        self.min_btn.setFixedSize(45, 25)
        self.min_btn.setProperty("class", "zoom_btn")
        # self.min_btn.setObjectName("min_btn")
        self.max_reset_btn = QPushButton("")
        self.max_reset_btn.setIcon(GML.Qt.Icon.get_icon("btn_max"))
        self.max_reset_btn.setFixedSize(45, 25)
        # self.max_reset_btn.setObjectName("max_reset_btn")
        self.max_reset_btn.setProperty("class", "zoom_btn")
        self.close_btn = QPushButton()
        self.close_btn.setIcon(GML.Qt.Icon.get_icon("btn_close"))
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setFixedSize(45, 25)

        self.main_lay.addWidget(self.icon_label)
        self.main_lay.addWidget(self.title_label)
        self.main_lay.addStretch()
        self.main_lay.addWidget(self.min_btn)
        self.main_lay.addWidget(self.max_reset_btn)
        self.main_lay.addWidget(self.close_btn)

        self.setLayout(self.main_lay)
        self.setStyleSheet("""QWidget {
            background-color: #52d3aa;
            background-image: brepeating-linear-gradient(to bottom right, #3f95ea 0%, #52d3aa 100%);
        }""")

    def apply_style_sheet(self):

        style_sheet = """
        
        QPushButton {
            border:none;
        }
        
        #title_label{
            color:rgba(187,187,187);
            font:msyhbd;
            float:left;
        }
        
        #close_btn {
            background-color:rgba(255,255,255,0);
        }
        
        #close_btn:hover {
            background-color:rgba(232,17,35,1);
        }
        
        .zoom_btn {
            background-color:rgba(255,255,255,0);
        }
        
        .zoom_btn:hover {
            background-color:rgba(79,82,84,1);
        }
        """

        self.setStyleSheet(style_sheet)

    def connect_signals(self):
        self.min_btn.clicked.connect(self.slot_min)
        self.max_reset_btn.clicked.connect(self.slot_max_reset)
        self.close_btn.clicked.connect(self.slot_close)

    def set_title(self, title):
        if title:
            self.title_label.setText(str(title))
            self.title_label.show()
        else:
            self.title.hide()

    def set_icon(self, icon):
        if icon:
            size = QSize(20, 20)
            self.icon_label.setFixedSize(QSize(20, 20))
            icon_resized = icon.scaled(QSize(20, 20), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(icon_resized)
            self.icon_label.show()
        else:
            self.icon_label.hide()

    def slot_min(self):
        self.main_win.showMinimized()

    def slot_max_reset(self):
        if self.main_win.isMaximized():
            self.main_win.showNormal()
            self.max_reset_btn.setIcon(GML.Qt.Icon.get_icon("btn_max"))
        else:
            self.main_win.showMaximized()
            self.max_reset_btn.setIcon(GML.Qt.Icon.get_icon("btn_reset"))

    def slot_close(self):
        self.main_win.close()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.globalPos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.main_win.move(self.main_win.pos() + event.globalPos() - self.offset)
            self.offset = event.globalPos()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)


class GML_Widget(QWidget):
    def __init__(self,
                 inline,
                 widget_name,
                 widget_title):
        super(GML_Widget, self).__init__()

        # GML Properties
        self.inline = inline
        self.widget_name = widget_name
        self.widget_title = widget_title
        self.widget_id = str(uuid.uuid4())

        self.widget_main_lay = QVBoxLayout()
        self.widget_main_lay.setMargin(0)
        self.widget_title_widget = GML_TitleBar(self)
        self.widget_body_widget = QWidget()

        # Configure Title Widget
        self.widget_title_widget.set_title(widget_title)

        # Configure Central Widget
        self.widget_body_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # GML Independent Window Management
        if not self.inline:
            GML.Qt.SubWins[self.widget_id] = self
            self.widget_main_lay.addWidget(self.widget_title_widget)
            self.apply_window_theme()

        # Load Body
        self.widget_main_lay.addWidget(self.widget_body_widget)

        # Set Layout
        super(GML_Widget, self).setLayout(self.widget_main_lay)

    def apply_window_theme(self):
        self.setWindowFlags(Qt.CustomizeWindowHint)

    def setLayout(self, target_layout):
        self.widget_body_widget.setLayout(target_layout)

    def setWindowTitle(self, title):
        self.widget_title_widget.set_title(title)
        super(GML_Widget, self).setWindowTitle(title)

    def setWindowIcon(self, icon):
        self.widget_title_widget.set_icon(icon)
        super(GML_Widget, self).setWindowIcon(icon)

    def closeEvent(self, event):
        if not self.inline:
            del GML.Qt.SubWins[self.widget_id]
