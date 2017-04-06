from qgis.core import *
from qgis.utils import *
from qgis.gui import *

import numpy as np
from data_plotter import *
import rasterio

def obtain_raster_values(raster_path, band, x, y):
    with rasterio.open(raster_path) as src:
        vals = src.sample([(x, y)])
        for val in vals:
            #QgsMessageLog.logMessage("val" + str(val), "debug")
            return val[band-1]

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
        x_click = event.pos().x()
        y_click = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x_click, y_click)
        x, y = point.x(), point.y()

        time, duration, magnitude, hazards_names, hazards_forcings = \
            self.extract_hazard_values(x, y)

        h_active = extract_h_active(time, duration, magnitude)
        title = 'Evolution of hazards in time in x: ' + str(x) + ' and y: ' + str(y)
        make_plot(time, duration, magnitude, hazards_names, hazards_forcings, h_active, title)

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

    def extract_hazard_values(self, x, y):
        time_list = []
        duration_list = []
        magnitude_list = []
        hazards_names = []
        hazards_forcings = []

        for hazard_i in self.hazard:
            m_val = obtain_raster_values(hazard_i.path, int(hazard_i.m), x, y)
            t_val = obtain_raster_values(hazard_i.path, int(hazard_i.t), x, y)
            d_val = obtain_raster_values(hazard_i.path, int(hazard_i.d), x, y)

            time_list.append(t_val)
            duration_list.append(d_val)
            magnitude_list.append(m_val)
            hazards_names.append(hazard_i.hazard_type)
            hazards_forcings.append(hazard_i.hazard_forcing)

        time = np.array(time_list)
        duration = np.array(duration_list)
        magnitude = np.array(magnitude_list)

        return time, duration, magnitude, hazards_names, hazards_forcings


