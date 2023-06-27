# Classes
from GML_Database.GDB_V2 import GMySQLConnector as GML_MySQLConnector
import GML

# Instance
GDC = None
GDC_V2 = None


def init():
    if GML.app_dev_mode:
        GML.Database.GDC = GML_MySQLConnector(connection_config={
            'user': "GML",
            'password': "GML_PASSWD",
            'host': "10.10.20.12",
            'database': "GDataCenter",
        })
        GML.Database.GDC_V2 = GML_MySQLConnector(connection_config={
            'user': "GML",
            'password': "GML_PASSWD",
            'host': "10.10.20.2",
            'database': "GDataCenterV2",
        })
    else:
        GML.Database.GDC = GML_MySQLConnector(connection_config={
            'user': "GML",
            'password': "GML_PASSWD",
            'host': "10.10.20.12",
            'database': "GDataCenter",
        })
        GML.Database.GDC_V2 = GML_MySQLConnector(connection_config={
            'user': "GML",
            'password': "GML_PASSWD",
            'host': "10.10.20.2",
            'database': "GDataCenterV2",
        })
