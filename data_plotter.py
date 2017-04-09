import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.patches as patches

NHAZARD_COLOR_MAP = { 1 : "#E0E0E0", 2 : "#919191", 3 : "#575757", 'other': '#1A1A1A'}

def define_color(size, i, style):
    cmap = cm.get_cmap(style)
    rgba = cmap(i/float(size))
    return rgba

def make_plot(time, duration, magnitude, hazards, parameters, h_active, title=''):
    fig, ax = plt.subplots()
    fig.show()
    plt.axhline(y=-4.5, linewidth=2, color='k')
    n_hazards = len(hazards)
    mag_max = np.max(magnitude)

    T = []
    hazards_number = []
    offset = 5

    for k in range(n_hazards):
        y_pos = k*(mag_max+offset)+2
        # create a rectangle
        xy = (time[k], y_pos)
        r = patches.Rectangle(
            xy,
            duration[k],
            magnitude[k],
            facecolor=define_color(len(time),k,'Spectral'),
            alpha=1,
             )

        ax.add_patch(r)
        ax.stem((time[k],time[k]+duration[k] ), (y_pos,y_pos), '--', bottom= -100, markerfmt = '')
        T.append(y_pos)
        hazards_number.append('h' + str(k+1) + ': ' + str(hazards[k]) )
        text = str(parameters[k]) + ': ' + str(magnitude[k])
        xy_t = (time[k], y_pos + magnitude[k] + 1.5)
        ax.annotate(text, xy=xy_t, horizontalalignment='left', verticalalignment='bottom')

    ax.autoscale(True, axis='both', tight=None)
    max_height = max([len(h_active[j]) for j in h_active.keys()])

    plt.ylim((-max_height-35 , y_pos+magnitude[k]+5))
    plt.xlim((np.min(time)-1, np.max(time+duration)+3))

    #ax.yaxis.set_visible(False)
    ax.set_yticks(T)
    ax.set_yticklabels(hazards_number)
    ax.set_xlabel('Time [h]')
    ax.set_title(title)
    #ax.set_aspect(40, adjustable=None, anchor=None)
    plt.grid()



    keys = sorted(h_active.keys())
    for ix in range(len(keys)-1):
        t = keys[ix]

        #plt.axvline(x=t, linestyle ='dashed', color = 'red')
        xy = (t,-(max_height + 19))


        if h_active[t] != []:
            if 0 < len(h_active[t]) < 4:
                color = NHAZARD_COLOR_MAP[len(h_active[t])]
                height = len(h_active[t])+1
            else:
                color = NHAZARD_COLOR_MAP['other']
                height = 5

            r = patches.Rectangle(
                xy,
                keys[ix + 1]-keys[ix],
                height,
                facecolor= color,
                alpha=1,
                label = str(len(h_active[t]))
                 )
            ax.add_patch(r)



            handles, labels = ax.get_legend_handles_labels()
            handle_list, label_list = [], []
            for handle, label in zip(handles, labels):
                if label not in label_list:
                    handle_list.append(handle)
                    label_list.append(label)
            #plt.legend(handle_list, label_list, loc='best', bbox_to_anchor=(1, 0.5), prop={'size':10})
            plt.legend(handle_list, label_list, loc='lower right', prop={'size': 10}, fancybox=True, shadow=True, title= "Number of \n hazards")


            text = ' h:' + ",".join([str(h + 1) for h in h_active[t]])

            if ix % 2 == 0:
                xy_t = (t,-(max_height + 19) )
                ax.annotate(text, xy=xy_t, horizontalalignment='left', verticalalignment='top')
            else:
                xy_t = (t, -19 - (max_height-height) + 1.5)
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
    time = np.array([0, 5,10, 6, 15, 9, 8])
    duration = np.array([5, 3, 2, 5, 4, 5, 5])
    magnitude = np.array([1, 2, 1, 4, 2, 6, 3])
    hazards_names = ['hearthquake', 'flood', 'landslide', 'earthquake', 'flood', 'snowstorm', 'landslide']
    hazards_forcings = ['pga [g]', 'wd [m]', 'vel [cm/yr]', 'pga [g]', 'wd [m]', 'height [m]', 'vel [cm/yr]']

    '''
    time = np.array([0, 8])
    duration = np.array([5, 3])
    magnitude = np.array([1, 2])
    hazards_names = ['a', 'b']
    hazards_forcings = ['a', 'b']
    '''


    h_active = extract_h_active(time, duration, magnitude)
    title = 'Evolution of hazards on time'
    make_plot(time, duration, magnitude, hazards_names, hazards_forcings, h_active, title)

