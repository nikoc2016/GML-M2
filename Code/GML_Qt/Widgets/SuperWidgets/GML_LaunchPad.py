import sys
import uuid
import GML

from PySide2.QtCore import Signal, QSize
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QSplitter, QWidget, QVBoxLayout, QApplication, QHBoxLayout, QLabel, QStackedWidget, \
    QPushButton

from GML_Qt.Widgets.SuperWidgets.GML_Widget import GML_Widget


class GML_LaunchPad(GML_Widget):
    def __init__(self,
                 inline,
                 widget_name,
                 widget_title):
        super(GML_LaunchPad, self).__init__(
            inline=inline,
            widget_name=widget_name,
            widget_title=widget_title
        )

        # Variables
        self.dialog_manager = self.DialogManager()  # {dialog_id: dialog, dialog_id: dialog...}

        # GUI Components

        self.main_lay = None

        self.side_win = None
        self.side_lay = None
        self.body_win = None
        self.body_lay = None

        self.side_style = None
        self.body_style = None

        # Construct
        self.construct()

        # Connect Signals

    def construct(self):

        self.main_lay = QHBoxLayout()

        self.side_win = QWidget()
        self.side_win.setObjectName("side_win")
        self.side_win.setFixedWidth(60)

        self.body_win = QStackedWidget()

        self.side_lay = QVBoxLayout()

        self.side_win.setLayout(self.side_lay)

        self.main_lay.addWidget(self.side_win)
        self.main_lay.addWidget(self.body_win)
        self.main_lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.main_lay)

        self.side_style = '''

            QWidget {
                background-color:rgb(60,63,65);
            }
            
            DialogButton {
                color:rgb(187,187,187);
                background-color:rgb(43,43,43);
                border-radius:15px;
                border:none;
                font-size:20px;
            }

            DialogButton:hover {
                color:rgba(187,187,187,0.8);
                background-color:rgba(43,43,43,0.8);
                border-radius:25px;
                border:none;
            }

            #add_tool_btn {
                background:url(D:/Users/picture/favicon.ico);
                height:100%;
                width:100%;
                background-poisitn:center,center;
                /*background-repeat:no-repeat;*/
            }

            '''

        self.body_style = '''

            QWidget {
                background-color:rgb(43,43,43);
            }
    
            #title_label {
                color:rgba(187,187,187,1);
                background-color:rgb(43,43,43);
                font-size:20px;
                font-style:italic;
            }
            '''

        self.side_win.setStyleSheet(self.side_style)
        self.body_win.setStyleSheet(self.body_style)

    # def connect_signals(self):
    #     pass
    #     # self.signal_dialog_btn_clicked.connect(self.slot_dialog_btn_clicked)

    def slot_dialog_btn_clicked(self):
        btn = self.sender()
        self.focus_dialog(btn.dialog.widget)
        # self.stackedWidget.setCurrentIndex(self.DialogManager.get_index_by_dialog_id(dialog_id))

    def focus_dialog(self, widget):
        self.body_win.setCurrentWidget(widget)
        return True

    def slot_refresh(self):
        """
        for dialog_id in self.dialog_manager.xx:
            if dialog_id exists in self.buttons || self.dialog_instances
                continue
            else
                self.dialog_instances.append() || insert()
                new_button.clicked.connect(self.slot_dialog_btn_clicked)
        :return:
        """
        if self.body_win.count() > 1:
            for index in reversed(range(self.body_win.count())):
                self.body_win.removeWidget(self.body_win.widget(index))

        if self.side_lay.count() > 1:
            # for i in range(self.body_win.count()):
            # for index in range(self.side_lay.count() - 1, -1, -1):
            for index in reversed(range(self.side_lay.count())):
                self.side_lay.takeAt(index)

        for dialog_id in self.dialog_manager.dialogs_order:
            self.side_lay.addWidget(self.dialog_manager.dialogs[dialog_id].button)
            self.body_win.addWidget(self.dialog_manager.dialogs[dialog_id].widget)
            self.dialog_manager.dialogs[dialog_id].button.clicked.connect(self.slot_dialog_btn_clicked)

        # print(self.side_lay.count())
        self.side_lay.addStretch(1)

        # for dialog_idx, dialog_id in enumerate(self.dialog_manager.dialogs_order):
        #
        #     if dialog_id in [button.dialog.id for button in self.buttons]:
        #         btn_idx = self.buttons.index(self.dialog_manager.get_button_by_id(dialog_id))
        #         if not dialog_idx == btn_idx:
        #             self.buttons[dialog_idx], self.buttons[btn_idx] = self.buttons[btn_idx], self.buttons[dialog_idx]
        #         continue
        #     else:
        #         # self.dialog_instances.append(dialog_id)
        #         self.buttons.insert(dialog_idx, self.dialog_manager.get_dialog_by_id(dialog_id).button)
        #         new_button.clicked.connect(self.slot_dialog_btn_clicked)
        #         self.buttons.append(new_button)
        return True

    def insert_dialog(self, title, icon, widget, size=50, user_closable=False, unread_messsage_count=None):
        new_dialog = self.Dialog(title, icon, widget, size, user_closable, unread_messsage_count)
        new_dialog.button.setIcon(icon)
        new_dialog.button.setFixedSize(QSize(size, size))
        self.dialog_manager.add_dialog(new_dialog)
        self.slot_refresh()

    def close_dialog(self, dialog_id):

        self.dialog_manager.dialogs[dialog_id].widget.close()
        self.dialog_manager.dialogs[dialog_id].widget.deleteLater()
        self.dialog_manager.dialogs[dialog_id].button.close()
        self.dialog_manager.dialogs[dialog_id].button.deleteLater()
        self.dialog_manager.remove_dialog(dialog_id)
        self.body_win.setCurrentIndex(0)
        self.slot_refresh()

        return True

    class DialogButton(QPushButton):
        def __init__(self, dialog):
            super(GML_LaunchPad.DialogButton, self).__init__()
            self.dialog = dialog

        def slot_refresh(self):
            self.setIcon(self.dialog.icon)

            # user closable
            if self.dialog.user_closable:
                pass

            # Unread messages
            if self.dialog.unread_messsage_count:
                pass

    class Dialog:
        def __init__(self, title, icon, widget, size=50, user_closable=None, unread_messsage_count=None):
            self.id = str(uuid.uuid4())
            self.title = title
            self.icon = icon
            self.widget = widget
            self.size = size
            self.user_closable = user_closable
            self.unread_messsage_count = unread_messsage_count

            self.button = GML_LaunchPad.DialogButton(self)
            self.button.setIcon(icon)
            self.button.setFixedSize(QSize(size, size))

    class DialogManager:
        def __init__(self):
            self.dialogs = {}
            self.dialogs_order = []

        def add_dialog(self, dialog):
            dialog_id = dialog.id
            self.dialogs[dialog_id] = dialog
            self.dialogs_order.append(dialog_id)
            return dialog_id

        def remove_dialog(self, dialog_id):
            del self.dialogs[dialog_id]
            self.dialogs_order.remove(dialog_id)
            print(self.dialogs)
            print(self.dialogs_order)

        def get_dialog_by_id(self, dialog_id):
            try:
                return self.dialogs[dialog_id]
            except:
                return None

        def get_title_by_id(self, dialog_id):
            try:
                return self.dialogs[dialog_id].title
            except:
                return None

        def get_icon_by_id(self, dialog_id):
            try:
                return self.dialogs[dialog_id].icon
            except:
                return None

        def get_widget_by_id(self, dialog_id):
            try:
                return self.dialogs[dialog_id].widget
            except:
                return None

        def get_button_by_id(self, dialog_id):
            try:
                return self.dialogs[dialog_id].button
            except:
                return None

        def get_size_by_id(self, dialog_id):
            try:
                return self.dialogs[dialog_id].size
            except:
                return None

        def get_closable_by_id(self, dialog_id):
            try:
                return self.dialogs[dialog_id].user_closable
            except:
                return None

        def get_count_by_id(self, dialog_id):
            try:
                return self.dialogs[dialog_id].unread_messsage_count
            except:
                return None

        def get_index_by_id(self, dialog_id):
            try:
                return self.dialogs_order.index(dialog_id)
            except:
                return None

        def get_id_by_widget(self, widget):
            for dialog in self.dialogs:
                if widget == dialog.widget:
                    return dialog.id
            return None

        def get_dialog_by_index(self, index):
            try:
                return self.dialogs[self.dialogs_order[index]]
            except:
                return None

        def get_id_list_by_title(self, title):
            for dialog in self.dialogs:
                if title == dialog.title:
                    return dialog.id
            return None
