from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from data_plotter import create_rectangle, define_color, obtain_raster_values, make_plot

class PointTool(QgsMapTool):
    def __init__(self, canvas, hazard):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.hazard = hazard

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        #x = event.pos().x()
        #y = event.pos().y()

        #point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        pass

    def canvasReleaseEvent(self, event):
        # Get the click
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.plot(point.x(),point.y())


    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

    def plot(self,x,y):

        time = []
        duration = []
        magnitude = []
        hazards_names = []
        hazards_forcings = []

        for hazard_i in self.hazard:
            m_val = obtain_raster_values(hazard_i.path, int(hazard_i.m), x, y)
            t_val = obtain_raster_values(hazard_i.path, int(hazard_i.t), x, y)
            d_val = obtain_raster_values(hazard_i.path, int(hazard_i.d), x, y)


            time.append(t_val)
            duration.append(d_val)
            magnitude.append(m_val)
            hazards_names.append(hazard_i.hazard_type)
            hazards_forcings.append(hazard_i.hazard_forcing)

        make_plot(time, duration, magnitude, hazards_names, hazards_forcings)



