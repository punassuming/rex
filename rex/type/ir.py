#!/usr/bin/env python

from rex.experiment import Experiment
import rex.io as io
from rex.curves import Curve

from rex.settings import EXPERIMENT_DB

HEADER_ROW = 3
DATA_BEGIN = 5

class IR(Experiment):
    """
    Analysis method that contains all pertinent information
    for NETL-MS data.
    Most information comes from Experiment.__init__() with a few exceptions
    procedure contains all pertinent information needed to calculate additional _curves

    """
    def __init__(self,
            xlfile=EXPERIMENT_DB,
            sheet='IR',
            prompt=None,
            debug=0):

        Experiment.__init__(self,
                xlfile = xlfile,
                sheet = sheet,
                prompt = prompt,
                delim = '\t',
                txt_col = 8,
                debug = debug)

        # save information from Excel file
        row = self._row

        self._raw_columns = {'wave_uc' : [0, 'Wavenumber [cm-1]'],
                'wave' : [1, 'Wavenumber [cm-1]'],
                'trans' : [2, 'Transmitance'],
                'abs' : [3, 'Absorbance [A.U]'],
                'n_trans' : [4, 'Transmitance [%]'],
                'n_absl' : [5, 'Absorbance [%]']
            }

        self._data_array = io.parse_jdx(self._ascii_file)
        self._curves = Curve(self._data_array,self._raw_columns)

        # important parameter in excel file
        self._row_params = {
            }

        # construct experiment name
        self._params.set('Name', '%s-%s.%s' % (row[1], row[2], row[3]))

        self._curves._labels = {'N':'\n',
            'n':self._params.get('Name'),
                }


