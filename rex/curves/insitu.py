"""
All functions in this file make use of the current axis or figure in memory
"""

from pylab import gcf, gca

def bnw(markers = ['o','p','s','v','x',
                   '<','>','D','H',
                   '^','d','h','*'],
        styles = ['solid','dashed','dashdot','dotted'],
        facecolor = ['black','white'],
        numpoints = None):
    """
    convert default lines into black and white
    able to marker, styles, and facecolor are iterated to prevent dupes
    """


    cf = gcf()

    for gc in cf.get_axes():
        # TODO, do this for scatters too
        for i, li in enumerate(gc.lines):
            li.set_color('black')
            li.set_marker(markers[i%13])
            li.set_mfc(facecolor[i%len(facecolor)])
            li.set_ls(styles[i%len(styles)])
            li.set_lw(1)
            li.set_ms(6)
            if numpoints == 'every':
                li.set_markevery(1)
            elif numpoints == 'quarter':
                li.set_markevery(4)
            elif numpoints is not None:
                li.set_markevery(int(len(li.get_xdata())/numpoints))

def markers(markers = ['o','p','s','v','x',
                   '<','>','D','H',
                   '^','d','h','*'],
        styles = ['solid','dashed','dashdot','dotted'],
        numpoints = None):
    """
    convert default lines into black and white
    able to marker, styles, and facecolor are iterated to prevent dupes
    """

    cf = gcf()

    for gc in cf.get_axes():
        # TODO, do this for scatters too
        for i, li in enumerate(gc.lines):
            li.set_marker(markers[i%13])
            li.set_ls(styles[i%len(styles)])
            li.set_ms(6)
            if numpoints == 'every':
                li.set_markevery(1)
            elif numpoints == 'quarter':
                li.set_markevery(4)
            elif numpoints is not None:
                li.set_markevery(int(len(li.get_xdata())/numpoints))

def stack_plots(location = 1400, bound=3, voffset = 0):
    """
    align all curves at index for x_i == location
    """
    gc = gca()

    y_data = []
    x_data = []
    index = []

    for li in gc.lines:
        x_data.append(li.get_xdata())
        y_data.append(li.get_ydata())

        # find the index @ location for each curve
        index.append((location - bound < x_data[-1]) & ( x_data[-1] > location + bound))

    offset = []

    # determine offset needed
    for i in range(len(x_data)):
        values = y_data[i][index[i]][0]
        if i == 0:
            baseline = values
        offset = values - baseline
        y_data[i] = y_data[i] - offset + voffset * i
        gc.lines[i].set_ydata(y_data[i])

