#!/usr/bin/env python

import pdb
from rex.experiment import Experiment
import rex.io as io
import datetime
import numpy as np

class TGAW(Experiment):
    """
    Analysis method that contains all pertinent information
    for TGA in Fauth / Hedges Lab.
    Most information comes from Experiment.__init__() with a few exceptions
    procedure contains all pertinent information needed to calculate additional _curves

    """
    def __init__(self,
            xlfile=EXPERIMENT_DB,
            sheet='TGA',
            prompt=None,
            debug=0):

        delim = ','

        self._raw_columns = {'rel_sec' : [0, 'Relative Time [s]'],
                'mass' : [1, 'Mass [mg]'],
                'temp' : [2, 'Temperature [C]'],
                'change' : [3, 'Weight Change [%]']
                }

        # After defining the key parameters, we execute our superclasses init
        # which access excel file, pulls info into self._row, and then parses data into self._data_array
        Experiment.__init__(self,
                xlfile = xlfile,
                sheet = sheet,
                prompt = prompt,
                delim = ',',
                txt_col = 6,
                dat = None,
                debug = debug)

        # save information from Excel file
        row = self._row

        row_params = {
                }

        self.add_curve('rel_hr',[float(sec)/3600 for sec in self._curves['rel_sec']], 'Relative Time [hr]')

        # Construct experiment name
        self.set_param('Name', '%s-%s.%s' % (row[1], row[2], row[3]))

        self._labels = {'N':'\n',
        'n':self.get_param('Name')}


