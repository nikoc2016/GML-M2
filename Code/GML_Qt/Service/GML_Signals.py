from PySide2.QtCore import QObject, Signal


class GML_Signals(QObject):
    # Timer
    seconds_passed = Signal(int)  # Range 0-59
    minute_passed = Signal(int)  # Range 0-59
    hour_passed = Signal(int)  # Range 0-23
    day_passed = Signal(int)  # Range 1-31
    month_passed = Signal(int)  # Range 1-12

    # GML_Cmd
    has_new_command = Signal(int, str)  # Command ID, Command_Line
