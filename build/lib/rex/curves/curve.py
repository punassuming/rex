#!/usr/bin/env python

import numpy as np
from matplotlib.pyplot import twinx, gca, subplot, title, show, setp, legend,\
    plot


"""
Curve object which stores the following information

name
array of values
label
dependant / independant tag (what class of variable?)


methods :

    plotting functions:
        ex plot = curves.plot("a","b")
        subplot
        twinplot
    add
        curve.add('name',list,'axis')
        remove


    find index

    stages (use numpy bitwise operation)

    integrate (up or down)

"""

class Curves(object):
    """
    This class is a container for multiple Curve objects
    """
    def __init__(self):
        pass

class Curve(dict):
    """
    This class represents an object storing curves as numpy arrays and plotting methods to allow quick visualization

    the curve dictionary has two entires per key.
        index 0 is a numpy array containing our data
        index 1 is a str with the axes information used when plotting

    self._labels are common legend labels used when plotting.  These are defined in the individual type files as a dictionary
    """

    def __init__(self, data_array, columns={}):
        dict.__init__(self)

        self._axes = {} # axis labels for plotting
        self._labels = {} # labels for plotting descriptors

        for key in columns:
            column = columns[key][0]
            axes = columns[key][1]
            self.add(key,data_array[column],axes)

        # stages available for experiment, default to all on (zero)
        self._raw = np.array(data_array)
        self._stage = np.zeros(len(data_array[0]), int)


    # Add and Remove Methods
    def add(self,name,list,axes=''):
        """ add a curve to the listing """
        array = np.array(list,float)
        self[name] = array
        self._axes[name] = axes

    def get(self, name, stage=0):
        # TODO Implement bitwise curve matching.
        if stage == 0:
            new_array = self.__getitem__(name)
        else:
            new_array = self.__getitem__(name)[self._stage & stage > 0]

            if 'time' in name and len(new_array) > 0:
                # convert to relative time of stage
                new_array -= new_array[0]

        return [new_array, self._axes.get(name)]

    def del_curve(self, key):
        """ delete a curve from the listing """
        del self[key]
        del self._labels[key]

    def compose(self, name, curves, stages, axes):
        """
         map provided lists to each stage
        a
        curves and stages are lists
        """
        new_array = np.zeros(len(self._stage))
        for i, stage in enumerate(stages):
            new_array[self._stage & stage > 0] = curves[i]
        self.add(name, new_array, axes)


    # Plotting Methods
    def ex_plot(self, X, Y, ttl='', label='', argl='', stage=0, shw=False, **kwargs):

        #markers = ['s','o','x','.','<','>','D','H','^','_','d','h',',','p','+','v','x',',']
        
        x_list, x_ax = self.get(X, stage=stage)
        y_list, y_ax = self.get(Y, stage=stage)

        #y_list = filter.smooth(y_list)
        if len(x_list) < 450:
            num = 14
        else:
            num = 21

        num_mark = len(x_list)/num

        lbl = self.ex_label(label=label, argl=argl)
#        ax = gca()
#        cur_idx = len(ax.get_lines())

        plots = plot(x_list,y_list,label=lbl, **kwargs)
        ax = gca()
        setp(plots, 'markevery', (1, num_mark))

        title(ttl)


        ax.set_xlabel(x_ax)
        ax.set_ylabel(y_ax)

        if argl != '':
            legend(loc=0, numpoints = 1)
        if shw is True:
            show()

    def ex_twinplot(self, X, Y, **kwargs):
#        ax = gca()

        # If type is tuple, use secondary verticle axis, otherwise plot multiple values on same scale
        if type(Y) == tuple:
            if len(Y)>2:
                raise Exception, "twinx plots only takes two arguments"
            else:
                for i in range(len(Y)):
                    self.ex_plot(X, Y[i], **kwargs)
                    twinx()
        else:
            for i in range(len(Y)):
                self.ex_plot(X, Y[i], **kwargs)

    def ex_subplot(self, X, Y, vert = True, ttls='', argls='', **kwargs):
        """
        Y is a list of curve names,
        vert = vertical subplots if True
        """

        ax = gca()

        num_subplots = len(Y)

        if not len(Y) > 1:
            raise Exception, "Subplot requires at least two Y arguments"

        for i in range(len(Y)):
            argl = ''
            ttl = ''

            # parse out list of arguments and titles
            if len(argls) == len(Y):
                argl = argls[i]
            if len(ttls) == len(Y):
                ttl = ttls[i]

            # based on vert setting, determine subplot command
            if vert == True:
                sub_num = int('%d%d%d' % (num_subplots, 1, i+1))
            else:
                sub_num = int('%d%d%d' % (1, num_subplots, i+1))

            subplot(sub_num)

            # If passed a list of indices, pass to twinplot function
            if hasattr(Y[i], '__iter__'):
                self.ex_twinplot(X, Y[i], ttl=ttl, argl=argl, **kwargs)
            else:
                self.ex_plot(X, Y[i], ttl=ttl, argl=argl, **kwargs)

            ax = gca()

            # Remove redundant axes on subplot
            if vert == True:
                if i+1 != len(Y):
                    ax.set_xlabel('')
            else:
                if i != 0:
                    ax.set_ylabel('')

    def ex_label(self,label,argl):
        """
        return a string of all comments to be
        appended to the legend
        """
        comment = ''
        for i in argl:
            phrase = ''
            if i == 'l':
                phrase = label
            elif i in self._labels.keys():
                phrase = self._labels[i]
            comment += phrase
        return comment


