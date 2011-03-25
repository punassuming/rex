#!/usr/bin/env python
import numpy as np
# Integration Methods


def midpoint(X,Y):
    # Rectangular Midpoint Method returns integral components 
    # and total integration (sum)
    list = []
    for i in range(1, len(Y)):
        dt = (X[i] - X[i-1])
        list.append(max(Y[i] * dt,0))
    # Append additional value to make list size consistent
    list.append(list[-1])

    return np.array(list), sum(list)

def trapezoid(X,Y):
    sum = 0
    for i in range(len(X)-1):
        area_i=0.5*(X[i+1]-X[i])*(Y[i+1]+Y[i])
        sum = sum + area_i
    return sum

def simpson(X,Y):
    n = len(X)
    h = (X[-1]-X[0])/(n-1)

    sum = Y[0]

    for i in range(len(X)-1):
        if (i+1)%2 == 0:
            sum = sum + Y[i+1]*2.0
        else:
            sum = sum + Y[i+1]*4.0
    sum = sum + Y[-1]

    integral = sum * h / 3.0

    return integral

def running_sum(Y, dir = 1):
    """
    grab list and recursively add each item to the previous
    dir = 1 is a rising sum, dir = -1 is a falling sum
    """
    Y = np.array(Y)

    if dir == 1:
        new_array = Y.cumsum()
    else:
        new_array = (Y.cumsum() - Y.sum().max()) * -1
    return new_array


def per_diff(X,Y):
    """ determine percent difference between X and Y """
    return 2 * abs(X - Y) / (X + Y)
