from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from data_plotter import create_rectangle, define_color, obtain_raster_values, make_plot


class PointTool(QgsMapTool):
    def __init__(self, canvas, m1, t1, d1, path1, m2, t2, d2, path2, layer1_name, layer2_name):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.m1 = m1
        self.t1 = t1
        self.d1 = d1
        self.path1 = path1
        self.m2 = m2
        self.t2 = t2
        self.d2 = d2
        self.path2 = path2
        self.layer1_name = layer1_name
        self.layer2_name = layer2_name

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
        m1_val = obtain_raster_values(self.path1, int(self.m1), x, y)
        t1_val = obtain_raster_values(self.path1, int(self.t1), x, y)
        d1_val = obtain_raster_values(self.path1, int(self.d1), x, y)

        m2_val = obtain_raster_values(self.path2, int(self.m2), x, y)
        t2_val = obtain_raster_values(self.path2, int(self.t2), x, y)
        d2_val = obtain_raster_values(self.path2, int(self.d2), x, y)

        time = [t1_val, t2_val]
        duration = [d1_val, d2_val]
        magnitude = [m1_val, m2_val]

        hazards = (str(self.layer1_name), str(self.layer2_name))

        make_plot(time, duration, magnitude, hazards)



