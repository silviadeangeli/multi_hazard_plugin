import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import rasterio
from rasterio.features import shapes
from qgis.core import *
from qgis.utils import *
from qgis.gui import *


def define_color(size, i, style):
    cmap = cm.get_cmap(style)
    rgba = cmap(i/float(size))
    return rgba

def create_rectangle(time, duration, h, y_pos,color, alpha_set):
    xy = (time, y_pos)
    rectangle = patches.Rectangle(xy, duration,h,facecolor=color, alpha=alpha_set)
    return rectangle

def obtain_raster_values(raster_path,band,x,y):
    with rasterio.open(raster_path) as src:
        vals = src.sample([(x, y)])
        for val in vals:
            QgsMessageLog.logMessage("val" + str(val), "debug")
            return val[band-1]

def make_plot(time,duration,magnitude):
    fig, ax = plt.subplots()
    for k in range(len(time)):
        ax.add_patch(create_rectangle(time[k], duration[k], magnitude[k], 10+k*10, define_color(len(time),k,'Spectral'),1))
    for k in range(len(time)):
        ax.add_patch(create_rectangle(time[k], duration[k], magnitude[k], -0.2, define_color(len(time),k,'Spectral'),0.5))

    ax.autoscale(True, axis='both', tight=None)
    ax.yaxis.set_visible(False)
    #ax.set_aspect(40, adjustable=None, anchor=None)
    plt.show()

