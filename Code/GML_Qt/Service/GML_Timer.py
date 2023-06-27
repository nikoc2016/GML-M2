from PySide2.QtCore import QObject, QTimer, QDateTime

import GML


class GML_Timer(QObject):
    def __init__(self):
        super(GML_Timer, self).__init__()

        # Private Storage
        self.previous_month = 0
        self.previous_day = 0
        self.previous_hour = 0
        self.previous_minute = 0
        self.previous_second = 0
        self.previous_has_initiated = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.slot_timeout)
        self.timer.start(1000)

    def slot_timeout(self):
        # Extract Current Time
        curr_datetime = QDateTime.currentDateTime()
        curr_month = int(curr_datetime.toString('MM'))
        curr_day = int(curr_datetime.toString('dd'))
        curr_hour = int(curr_datetime.toString('hh'))
        curr_minute = int(curr_datetime.toString('mm'))
        curr_second = int(curr_datetime.toString('ss'))

        # Emit Signals
        if self.previous_has_initiated:
            if self.previous_month != curr_month:
                GML.Qt.GML_Signals.month_passed.emit(curr_month)
            if self.previous_day != curr_day:
                GML.Qt.GML_Signals.PublicSignals.day_passed.emit(curr_day)
            if self.previous_hour != curr_hour:
                GML.Qt.GML_Signals.PublicSignals.hour_passed.emit(curr_hour)
            if self.previous_minute != curr_minute:
                GML.Qt.GML_Signals.PublicSignals.minute_passed.emit(curr_minute)
            if self.previous_second != curr_second:
                GML.Qt.GML_Signals.PublicSignals.seconds_passed.emit(curr_second)

        # Cache Current Time
        self.previous_month = curr_month
        self.previous_day = curr_day
        self.previous_hour = curr_hour
        self.previous_minute = curr_minute
        self.previous_second = curr_second
        self.previous_has_initiated = False