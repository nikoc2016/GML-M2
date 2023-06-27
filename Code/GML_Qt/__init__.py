# Normal Imports
from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import QApplication

# Classes
import GML_Qt.Widgets
import GML_Qt.Service
import GML_Qt.Icon

# Instance
QApp = None
MainWin = None
SubWins = None


def launch():
    import GML

    GML.Qt.QApp = QApplication([])
    GML.Qt.apply_dark_theme(GML.Qt.QApp)
    GML.Qt.Service.launch()
    GML.Qt.SubWins = {}
    GML.Qt.MainWin = GML.Qt.Widgets.GML_MainWindow()
    GML.Qt.QApp.exec_()


def apply_dark_theme(app):
    app.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(60, 63, 65))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(200, 200, 200).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)
