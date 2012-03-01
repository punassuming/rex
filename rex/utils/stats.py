#!/usr/bin/env python
import numpy

def mean(x):
    return numpy.mean(x)

# variance and covariance
def ss(x, y = None):
    if y is None:
        ssx = 0
        for i in x:
            ssx += ( i - mean(x) ) **2
        return len(x) * ssx
    else:
        ssxy = 0
        for i in range(len(x)):
            if x[i] is None or y[i] is None or len(x) != len(y):
                pass
            else:
                ssxy += (x[i] - mean(x) ) * ( y[i] - mean(y) )
        return len(x) * ssxy


def var(x):
    return ss(x)

def stdev(x):
    return ss(x) ** 0.5

def leastsqr(x,y):
    b = ss(x,y) / ss(x)
    R2 = ss(x,y)**2 / ss(x) / ss(y)
    SSR = ss(y) + b**2 * ss(x) - 2 * b * ss(x,y)
    SSE = b**2 * ss(x)
    R2alt = SSR / ss(y) #@UnusedVariable
    return b, R2, SSR, SSE
