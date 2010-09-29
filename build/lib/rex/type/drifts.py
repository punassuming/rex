#!/usr/bin/env python

from rex.experiment import Experiment
import rex.io as io

HEADER_ROW = 3
DATA_BEGIN = 5
EXPERIMENT_DB = '/home/walesi/data/experiment.xls'

class DRIFTS(Experiment):
    """
    Analysis method that contains all pertinent information
    for NETL-MS data.
    Most information comes from Experiment.__init__() with a few exceptions
    procedure contains all pertinent information needed to calculate additional _curves

    """
    def __init__(self,
            xlfile=EXPERIMENT_DB,
            sheet='DRIFTS',
            prompt=None,
            debug=0):

        Experiment.__init__(self,
                xlfile = xlfile,
                sheet = sheet,
                prompt = prompt,
                delim = '\t',
                txt_col = 8,
                dat = None,
                debug = debug)

        # save information from Excel file
        row = self._row

        self._raw_columns = {'wave_uc' : [0, 'Wavenumber [cm-1]'],
                'wave' : [1, 'Wavenumber [cm-1]'],
                'trans' : [2, 'Transmitance'],
                'refl' : [3, 'Reflectance'],
                'n_trans' : [4, 'Transmitance [%]'],
                'n_refl' : [5, 'Reflectance [%]']
            }

        self._data_array = io.parse_jdx(self._ascii_file)

        self._add_raw_curves()

        # important parameter in excel file
        row_params = {
            }

        self.init_param(row_params)

        # construct experiment name
        self.set_param('Name', '%s-%s.%i' % (row[1], row[2], row[3]))

        self._labels = {'N':'\n',
            'n':self.get_param('Name'),
                }

