# Normal Imports
import GML

# Classes
from GML_Qt.Service.GML_Signals import GML_Signals
from GML_Qt.Service.GML_Timer import GML_Timer

# Instance
Signals = None
Timer = None


def launch():
    GML.Qt.Service.Signals = GML_Signals()
    GML.Qt.Service.Timer = GML_Timer()
    print("Qt::Service::Initiated.")
