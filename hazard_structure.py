
from qgis.core import QgsMessageLog
from PyQt4.QtCore import QFileInfo

class hazard():

    def __init__(self, m, t, d, path, hazard_type, hazard_forcing):
        self.m = m
        self.t = t
        self.d = d
        self.path = path
        self.hazard_type = hazard_type
        self.hazard_forcing = hazard_forcing
        self.name = QFileInfo(path).baseName()


    def print_debug(self):
        QgsMessageLog.logMessage("Layer name: " + self.name, "debug")
        QgsMessageLog.logMessage("Layer path: " + self.path, "debug")
        QgsMessageLog.logMessage("Magnitude band of" + self.name + ": " + self.m, "debug")
        QgsMessageLog.logMessage("Initial time band of" + self.name + ": "+ self.t, "debug")
        QgsMessageLog.logMessage("Duration band of"+ self.name + ": " + self.d, "debug")


