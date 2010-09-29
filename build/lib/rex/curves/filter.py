#!/usr/bin/env python
import numpy
    # Filtering Methods

def limit(list, limit):
    """
    Limits a list to go only to a maximum and no higher and returns resulting list
    """
    norm = []
    for i in list:
        if i > limit:
            i = limit
        norm.append(i)
    return norm

def smooth(x,window_len=27,window='hanning'):
    """smooth the data using a window with requested size.
    from : http://www.scipy.org/Cookbook/SignalSmooth
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    inumpyut:
        x: the inumpyut signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Inumpyut vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    w = numpy.ones(window_len,'d') if window == 'flat' else eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]


def purge(x,y,diff):
    """
    Cuts erroneous points out of list y and corresponding values in list x
    diff = factor applied to value to determine % change allowed
    """
    newy= []
    newx = []

    j = y[0]
    k = y[0]

    for n,i in enumerate(y):
        if abs(i-k) < i*diff:
            newy.append(y[n])
            newx.append(x[n])
        k = j
        j = i
    return newx, newy

def reduce(x, new_length):
    """
    reduce the size of array x while maintaining the shape of the data
    """
    x = numpy.array(x)
    cur_length = len(x)
    ratio = cur_length / new_length
    new_array = x[numpy.s_[::ratio]]
    return new_array


