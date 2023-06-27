from PySide2.QtWidgets import QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel

from GML_Runtime import GMLRuntime
from LegacySupport.GDC_V2 import GDC_SQLConnector
from NikoKit.NikoQt.NQKernel.NQGui.NQWindow import NQWindow


class ITWindow(NQWindow):
    def __init__(self, *args, **kwargs):
        # GUI Component
        self.main_lay = None
        self.seat_num_line_edit = None
        self.ticket_detail_text_edit = None
        self.info_label = None
        self.submit_button = None

        super(ITWindow, self).__init__(*args, **kwargs)

    def construct(self):
        super(ITWindow, self).construct()
        main_lay = QVBoxLayout()
        seat_num_line_edit = QLineEdit()
        ticket_detail_text_edit = QTextEdit()
        info_label = QLabel(self.lang("ui_it_ticket_info_default"))
        submit_button = QPushButton(self.lang("submit"))

        main_lay.addWidget(QLabel(self.lang("ui_it_seat_number")))
        main_lay.addWidget(seat_num_line_edit)
        main_lay.addWidget(QLabel(self.lang("ui_it_ticket", "detail")))
        main_lay.addWidget(ticket_detail_text_edit)
        main_lay.addWidget(info_label)
        main_lay.addWidget(submit_button)

        self.setLayout(main_lay)
        self.main_lay = main_lay
        self.seat_num_line_edit = seat_num_line_edit
        self.ticket_detail_text_edit = ticket_detail_text_edit
        self.info_label = info_label
        self.submit_button = submit_button

    def connect_signals(self):
        super(ITWindow, self).connect_signals()
        self.submit_button.clicked.connect(self.slot_submit)

    def slot_submit(self):
        seat_num = self.seat_num_line_edit.text()
        ticket_detail = self.ticket_detail_text_edit.toPlainText()

        if seat_num == "" or ticket_detail == "" or not seat_num.isdigit():
            self.info_label.setText(self.lang("ui_it_ticket_error"))
        else:
            result, errors = self.submit_GDC_V2_ticket(user_seat_number=int(self.seat_num_line_edit.text()),
                                                       ticket_detail=self.ticket_detail_text_edit.toPlainText())
            if errors:
                self.info_label.setText("ui_it_submit_error")
                self.ticket_detail_text_edit.setText("".join(errors))
            else:
                self.close()

    def submit_GDC_V2_ticket(self, user_seat_number, ticket_detail):
        ticket_mboard_id = GMLRuntime.Machine.hardware_snapshot["mboards"][0]["mboard_id"]
        ticket_pc_name = GMLRuntime.Machine.pc_name
        ticket_seat_id = user_seat_number
        ticket_ip = GMLRuntime.Machine.ip
        ticket_username = GMLRuntime.Machine.username
        ticket_realname = GMLRuntime.Data.current_user.user_last_name + GMLRuntime.Data.current_user.user_first_name
        ticket_description = ticket_detail

        sql_line_tech_ticket = """
        INSERT INTO GDC_tech_ticket 
        (   ticket_id, 
            ticket_mboard_id, 
            ticket_pc_name, 
            ticket_seat_id, 
            ticket_ip, 
            ticket_username, 
            ticket_realname, 
            ticket_description, 
            ticket_handler_id, 
            ticket_handler_name, 
            ticket_open_datetime, 
            ticket_close_datetime, 
            ticket_is_legacy, 
            ticket_solution) 
        VALUES 
        (   Null, 
            %s, 
            %s, 
            %s, 
            %s, 
            %s, 
            %s, 
            %s, 
            Null, 
            Null, 
            current_timestamp(), 
            Null, 
            0, 
            Null) 
        """
        sql_data_tech_ticket = (
            ticket_mboard_id,
            ticket_pc_name,
            ticket_seat_id,
            ticket_ip,
            ticket_username,
            ticket_realname,
            ticket_description
        )

        sql_line_tech_chat = ("INSERT INTO GDC_tech_chat "
                              "(chat_id, ticket_id, chat_username, chat_usergroup, chat_content, chat_datetime) "
                              "VALUES "
                              "(Null, LAST_INSERT_ID(), %s, %s, %s, current_timestamp())")
        sql_data_tech_chat = (ticket_realname,
                              self.lang("ui_it_user"),
                              self.lang("ui_it_user_has_created_ticket"))

        sql_lines = [
            [sql_line_tech_ticket, sql_data_tech_ticket],
            [sql_line_tech_chat, sql_data_tech_chat]
        ]

        gdc_v2_sql_connector = GDC_SQLConnector()

        return gdc_v2_sql_connector.write_transaction(sql_lines)
