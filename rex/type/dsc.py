#!/usr/bin/env python
# encoding: utf-8

"""
#
sorbent
exp
run
book
date
file:txt
file:baseline
co2
temp:start
temp:stop
temp:ramp
temp:dry
time:dry
mass:pan
mass:pre
mass:post
mass:act
mass:delta
loading
notes
"""

from rex.experiment import Experiment
from rex.settings import EXPERIMENT_DB
from rex.utils import io
from rex.curves.curve import Curve
from rex.curves.analysis import midpoint
from numpy import mean
import os

class DSC(Experiment):
    """
    Analysis method that contains all pertinent information
    for NETL-DSC data.
    Most information comes from Experiment.__init__() with a few exceptions
    procedure contains all pertinent information needed to calculate additional _curves

    """
    def __init__(self,
            xlfile=EXPERIMENT_DB(),
            sheet='DSC',
            prompt=None,
            debug=0):


        # self._raw_columns = {
        #     'Curve', [column, 'label']
        # }



        Experiment.__init__(self,
                xlfile = xlfile,
                sheet = sheet,
                prompt = prompt,
                delim = '\t',
                txt_col = 6,
                debug = debug)

        self._raw_columns = {
            'time:min' : [0, 'Time (min)'],
            'heat:flow' : [1, 'Heat Flow (mW)'],
            'temp:set' : [3, 'Set Point Temperature ($\degree$C)'],
            'temp:act' : [4, 'Temperature ($\degree$C)'],
            'heat:cal' : [6, 'Heat Flow Calibration']
        }

        self._ascii_file = self._path + os.sep + 'data' + os.sep + self.p.get('txt:file')
        self._baseline_file = self._path + os.sep + 'data' + os.sep + self.p.get('baseline:file')

        self._data_array = remove_with_blanks(
            io.parse_ascii(self._ascii_file , '\t')[1:]
        )

        self._baseline_array = remove_with_blanks(
            io.parse_ascii(self._baseline_file, '\t')[1:]
        )

        # if we have defined _raw_columns then add all of those curves (defined for each exp type)
        if hasattr(self, '_raw_columns'):
            self._curves = Curve(self._data_array,self._raw_columns)
            self._baseline = Curve(self._baseline_array,self._raw_columns)
        else:
            self._curves = Curve(self._data_array)
            self._baseline = Curve(self._baseline_array)

        if hasattr(self, '_curves'):
            self._curves.add('time:sec', self._curves['time:min']*60., 'Time (sec)')
            self._curves.add('time:hr', self._curves['time:sec']/3600., 'Time (hr)')

            self.subtract_baseline()
            self.c = self._curves
            self.pl = self._curves.ex_plot
            self.twin = self._curves.ex_twinplot
            self.sub = self._curves.ex_subplot

    def subtract_baseline(self):
        self._curves.add(
            'heat:sub',
            self._curves['heat:flow'] - self._baseline['heat:flow'],
            'Normalized Heat Flow (mW)')

        # mg and mW cancel out
        # also sampling is at one second
        self._curves.add(
            'heat:cap',
            self._curves['heat:sub']/(
                self._params['mass:act'] * abs(mean(
                    self._curves['temp:act'][:-1]-self._curves['temp:act'][1:]))),
            'Specific Heat (J/(g*$\degree$C))')




def transpose(grid):
    return zip(*grid)

def remove_with_blanks(has_blanks):

    has_blanks = transpose(has_blanks)[86:-69]
    no_blanks = has_blanks

    rows_with_blanks = []

    for i,j in enumerate(has_blanks):
        try:
            [float(l) for l in j]
        except:
            rows_with_blanks.append(i)

    # reverse the order to keep indexing
    for i in reversed(sorted(rows_with_blanks)):
        del no_blanks[i]

    return transpose(no_blanks)
