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

def create_rectangle(time, duration, h, y_pos,color, alpha_set, label_set):
    xy = (time, y_pos)
    rectangle = patches.Rectangle(xy, duration,h,facecolor=color, alpha=alpha_set, label = label_set)
    return rectangle

def obtain_raster_values(raster_path,band,x,y):
    with rasterio.open(raster_path) as src:
        vals = src.sample([(x, y)])
        for val in vals:
            QgsMessageLog.logMessage("val" + str(val), "debug")
            return val[band-1]

def make_plot(time,duration,magnitude,hazards):
    fig, ax = plt.subplots()
    T = []
    hazards_number = []
    for k in range(len(time)):
        ax.add_patch(create_rectangle(time[k], duration[k], magnitude[k], 10+k*10, define_color(len(time),k,'Spectral'),1, str(hazards[k]) ))
        T.append(10+k*10+magnitude[k]/2)
        hazards_number.append('Hazard ' + str(k+1))
        plt.text(time[k]+duration[k]/2, 11+k*10+magnitude[k], 'forcing :'+ str(magnitude[k]))
    for k in range(len(time)):
        ax.add_patch(create_rectangle(time[k], duration[k], magnitude[k], -0.2, define_color(len(time),k,'Spectral'),0.5, ""))

    ax.autoscale(True, axis='both', tight=None)
    #ax.yaxis.set_visible(False)
    ax.set_yticks(T)
    ax.set_yticklabels(hazards_number)
    ax.set_xlabel('Time [h]')
    ax.set_title('Evolution of hazards in time')
    #ax.set_aspect(40, adjustable=None, anchor=None)
    plt.legend()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    #figManager = plt.get_current_fig_manager()
    #figManager.window.showMaximized()


    Size = fig.get_size_inches()
    fig.set_size_inches(Size[0] * 2, Size[1] * 2,
                      forward=True)  # Set forward to True to resize window along with plot in figure.
    plt.show()

