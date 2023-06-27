from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from NikoKit.NikoQt.NQKernel.NQGui.NQWidgetArea import NQWidgetArea
from NikoKit.NikoQt.NQKernel.NQGui.NQWidgetCheckList import NQWidgetCheckList
from NikoKit.NikoQt.NQKernel.NQGui.NQWindow import NQWindow
from GML_Runtime import GMLRuntime


class ProjectSelectionWindow(NQWindow):
    def __init__(self,
                 w_width=400,
                 w_height=300,
                 *args,
                 **kwargs):
        # Data
        self.selected_project = ""

        # GUI Component
        self.main_lay = None
        self.selection_area = None
        self.selection_checklist = None
        self.info_label = None
        self.btn_okay = None

        super(ProjectSelectionWindow, self).__init__(w_width=w_width, w_height=w_height, *args, **kwargs)

        self.slot_refresh_checklist()
        self.slot_update_info()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def construct(self):
        super(ProjectSelectionWindow, self).construct()

        main_lay = QVBoxLayout()
        selection_checklist = NQWidgetCheckList(exclusive=True)
        selection_area = NQWidgetArea(title=self.lang("select", "project"), central_widget=selection_checklist)
        info_label = QLabel()
        btn_lay = QHBoxLayout()
        btn_okay = QPushButton(self.lang("confirm"))

        main_lay.addWidget(selection_area)
        main_lay.addWidget(info_label)
        main_lay.addLayout(btn_lay)
        main_lay.setStretchFactor(main_lay, 1)

        btn_lay.addStretch()
        btn_lay.addWidget(btn_okay)
        btn_lay.addStretch()

        self.setLayout(main_lay)

        self.main_lay = main_lay
        self.selection_area = selection_area
        self.selection_checklist = selection_checklist
        self.info_label = info_label
        self.btn_okay = btn_okay

    def connect_signals(self):
        super(ProjectSelectionWindow, self).connect_signals()
        self.selection_checklist.changed.connect(self.slot_selected)
        self.btn_okay.clicked.connect(self.slot_okay)
        GMLRuntime.Signals.user_updated.connect(self.slot_refresh_checklist)

    def slot_refresh_checklist(self):
        self.selection_checklist.remove_all_options()
        selection_list = []
        try:
            selection_list = eval(GMLRuntime.Data.current_user.user_cgt_available_projects)
        except:
            pass
        for selection in selection_list:
            self.selection_checklist.add_option(option_name=selection, display_text=selection)

        self.selection_checklist.set_focus(option_name=GMLRuntime.Data.current_proj, set_check=True)
        self.slot_update_info()

    def slot_selected(self, selected_project):
        self.selected_project = selected_project
        self.slot_update_info()

    def slot_update_info(self):
        self.info_label.setText(self.lang("lp_status") % (GMLRuntime.Data.current_proj, self.selected_project))

    def slot_okay(self):
        self.selected_project = self.selection_checklist.get_checked()
        GMLRuntime.Data.current_proj = self.selected_project
        GMLRuntime.Signals.proj_updated.emit()
        self.close()
