# coding=utf8
# Copyright (c) lovICer 2021/6/25 GVF

import functools

from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QHBoxLayout, QGraphicsPixmapItem, QWidget, QFrame, \
    QPushButton
from PySide2.QtGui import QBrush, QColor, QPainter, QPen
from PySide2.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QTimer, QEvent, Signal, QByteArray


class GML_GuidPrivate(QFrame):
    sig_go_to_page = Signal()

    def __init__(self, parent=None):
        super(GML_GuidPrivate, self).__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.set_checked(False)

    def set_checked(self, value):
        if value:
            self.setStyleSheet('background-color:{}'.format("white"))
            self.setFixedSize(20, 4)
        else:
            self.setStyleSheet('background-color:{}'.format("black"))
            self.setFixedSize(16, 4)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.sig_go_to_page.emit()
        return super(GML_GuidPrivate, self).mousePressEvent(event)


def property_mixin(cls):
    """Run function after dynamic property value changed"""

    def _new_event(self, event):
        if event.type() == QEvent.DynamicPropertyChange:
            prp = event.propertyName()
            if hasattr(self, '_set_{}'.format(prp)):
                callback = getattr(self, '_set_{}'.format(prp))
                callback(self.property(str(prp)))
        return super(cls, self).event(event)

    setattr(cls, 'event', _new_event)
    return cls


@property_mixin
class GML_Carousel(QGraphicsView):
    def __init__(self, pix_list, autoplay=True, width=900, height=350, parent=None):
        super(GML_Carousel, self).__init__(parent)

        self.pix_list = pix_list
        self.autoplay = autoplay
        self.carousel_width = width
        self.carousel_height = height

        self.main_scene = None
        self.hor_bar = None
        self.navigate_lay = None
        self.page_count = None
        self.loading_ani = None
        self.autoplay_timer = None

        self.current_index = None

        self.construct()

    def construct(self):

        self.main_scene = QGraphicsScene()
        self.main_scene.setBackgroundBrush(QBrush(QColor(255, 255, 255, 0)))  # 背景色
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setScene(self.main_scene)
        self.setRenderHints(QPainter.Antialiasing)
        self.hor_bar = self.horizontalScrollBar()

        pos = QPoint(0, 0)
        pen = QPen(Qt.red)
        pen.setWidth(5)
        self.page_count = len(self.pix_list)
        line_width = 20
        total_width = self.page_count * (line_width + 5)
        self.main_scene.setSceneRect(0, 0, self.page_count * self.carousel_width, self.carousel_height)

        self.navigate_lay = QHBoxLayout()
        self.navigate_lay.setSpacing(5)
        target_size = max(self.carousel_width, self.carousel_height)
        for index, pix in enumerate(self.pix_list):
            if pix.width() > pix.height():
                new_pix = pix.scaledToWidth(target_size, Qt.SmoothTransformation)
            else:
                new_pix = pix.scaledToHeight(target_size, Qt.SmoothTransformation)
            pix_item = QGraphicsPixmapItem(new_pix)
            pix_item.setPos(pos)
            pix_item.setTransformationMode(Qt.SmoothTransformation)
            pos.setX(pos.x() + self.carousel_width)
            line_item = GML_GuidPrivate()
            line_item.sig_go_to_page.connect(functools.partial(self.go_to_page, index))
            self.navigate_lay.addWidget(line_item)
            self.main_scene.addItem(pix_item)

        hud_widget = QWidget(self)
        hud_widget.setLayout(self.navigate_lay)
        hud_widget.move(self.carousel_width / 2 - total_width / 2, self.carousel_height - 30)

        self.setFixedWidth(self.carousel_width + 2)
        self.setFixedHeight(self.carousel_height + 2)
        self.loading_ani = QPropertyAnimation()
        self.loading_ani.setTargetObject(self.hor_bar)
        self.loading_ani.setEasingCurve(QEasingCurve.InOutQuad)
        self.loading_ani.setDuration(500)
        self.loading_ani.setPropertyName(b'value')
        self.autoplay_timer = QTimer(self)
        self.autoplay_timer.setInterval(2000)
        self.autoplay_timer.timeout.connect(self.next_page)

        self.current_index = 0
        self.go_to_page(self.current_index)
        self.set_autoplay(self.autoplay)

    def set_autoplay(self, value):
        self.setProperty('autoplay', value)

    def _set_autoplay(self, value):
        if value:
            self.autoplay_timer.start()
        else:
            self.autoplay_timer.stop()

    def set_interval(self, ms):
        self.autoplay_timer.setInterval(ms)

    def next_page(self):
        if self.current_index + 1 < self.page_count:
            index = self.current_index + 1
        else:
            index = 0
        self.go_to_page(index)

    def pre_page(self):
        if self.current_index > 0:
            index = self.current_index - 1
        else:
            index = self.page_count - 1
        self.go_to_page(index)

    def go_to_page(self, index):
        self.loading_ani.setStartValue(self.current_index * self.carousel_width)
        self.loading_ani.setEndValue(index * self.carousel_width)
        self.loading_ani.start()
        self.current_index = index
        for i in range(self.navigate_lay.count()):
            frame = self.navigate_lay.itemAt(i).widget()
            frame.set_checked(i == self.current_index)

