import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def define_color(size, i, style):
    cmap = cm.get_cmap(style)
    rgba = cmap(i/float(size))
    return rgba

def make_plot(time, duration, magnitude, hazards, parameters, h_active, title=''):
    fig, ax = plt.subplots()
    fig.show()
    n_hazards = len(hazards)
    mag_max = np.max(magnitude)

    T = []
    hazards_number = []
    offset = 5
    for k in range(n_hazards):
        y_pos = k*(mag_max+offset)
        # create a rectangle
        xy = (time[k], y_pos)
        r = patches.Rectangle(
            xy,
            duration[k],
            magnitude[k],
            facecolor=define_color(len(time),k,'Spectral'),
            alpha=1,
            label=str(hazards[k])
        )
        ax.add_patch(r)
        T.append(y_pos)
        hazards_number.append('Hazard ' + str(k+1))
        text = str(parameters[k]) + ': ' + str(magnitude[k])
        xy_t = (time[k], y_pos + magnitude[k] + 0.1)
        ax.annotate(text, xy=xy_t, horizontalalignment='left', verticalalignment='bottom')


    ax.autoscale(True, axis='both', tight=None)
    plt.ylim((-11, y_pos+magnitude[k]+5))
    plt.xlim((np.min(time)-1, np.max(time+duration)+1))

    #ax.yaxis.set_visible(False)
    ax.set_yticks(T)
    ax.set_yticklabels(hazards_number)
    ax.set_xlabel('Time [h]')
    ax.set_title(title)
    #ax.set_aspect(40, adjustable=None, anchor=None)
    plt.legend()
    plt.grid()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    keys = sorted(h_active.keys())
    for ix in range(len(keys)):
        t = keys[ix]
        plt.axvline(x=t)
        xy = (t, -10)
        print h_active[t]
        if h_active[t] != []:
            r = patches.Rectangle(
                xy,
                keys[ix + 1]-keys[ix],
                3,
                facecolor='red',
                alpha=1
            )
            ax.add_patch(r)
            xy_t = (t, -5.8)
            text = 'h:' +  ",".join([str(h+1) for h in h_active[t]])
            ax.annotate(text, xy=xy_t, horizontalalignment='left', verticalalignment='bottom')
    size = fig.get_size_inches()
    fig.set_size_inches(size[0] * 2, size[1] * 2,
                      forward=True)  # Set forward to True to resize window along with plot in figure.
    plt.show()



def extract_h_active(time, duration, magnitude):
    final_time = time + duration
    important_t = np.concatenate((time,final_time))
    ordered_important_t = np.unique(np.sort(important_t))
    print ordered_important_t

    h_active = {}
    h_active_old = None
    for time_s in ordered_important_t:
        h_active_t = []
        if h_active_old:
            h_active_t.extend(h_active_old)

        to_append = np.where(time == time_s)[0]
        for el in to_append:
            h_active_t.append(el)

        to_remove = np.where(final_time == time_s)[0]
        for el in to_remove:
            if el in h_active_t:
                h_active_t.remove(el)

        h_active[time_s] = h_active_t
        h_active_old = h_active_t
    print h_active
    return h_active

# will be called if we run this module as main, useful for debug/test/development
if __name__ == "__main__":
    #time = np.array([0, 5,10, 6, 15])
    #duration = np.array([5, 3, 2, 5, 4])
    #magnitude = np.array([1, 2, 1, 4, 2])
    #hazards_names = ['a', 'b', 'c', 'd', 'e']
    #hazards_forcings = ['a', 'b', 'c', 'd', 'e']

    time = np.array([0, 8])
    duration = np.array([5, 3])
    magnitude = np.array([1, 2])
    hazards_names = ['a', 'b']
    hazards_forcings = ['a', 'b']

    h_active = extract_h_active(time, duration, magnitude)
    title = 'Test'
    make_plot(time, duration, magnitude, hazards_names, hazards_forcings, h_active, title)

