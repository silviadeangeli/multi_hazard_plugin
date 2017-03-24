import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import rasterio
from rasterio.features import shapes

#fig, ax = plt.subplots()

#time =[10, 12, 8]
#duration=[20, 30, 10]

def define_color(size, i, style):
    cmap = cm.get_cmap(style)
    rgba = cmap(i/float(size))
    return rgba

def create_rectangle(time, duration, y_pos,color, alpha_set):
    time_end= time + duration
    xy = (time, y_pos)
    h = 0.1
    rectangle = patches.Rectangle(xy, time_end,h,facecolor=color, alpha=alpha_set)
    return rectangle

def obtain_raster_values(raster_path,band,x,y):
    with rasterio.open(raster_path) as src:
        #x = (src.bounds.left + src.bounds.right) / 1.5
        #y = (src.bounds.bottom + src.bounds.top) / 1.5
        vals = src.sample([(x, y)])
        for val in vals:
            return val[band-1]

def make_plot(time,duration):
    fig, ax = plt.subplots()
    for k in range(len(time)):
        ax.add_patch(create_rectangle(time[k], duration[k], 0.025+k*0.15, define_color(len(time),k,'Spectral'),1))
    for k in range(len(time)):
        ax.add_patch(create_rectangle(time[k], duration[k], -0.2, define_color(len(time),k,'Spectral'),0.5))

    ax.autoscale(True, axis='both', tight=None)
    ax.yaxis.set_visible(False)
    ax.set_aspect(40, adjustable=None, anchor=None)
    plt.show()

