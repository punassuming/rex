#!/usr/bin/env python

from rex.experiment import Experiment

HEADER_ROW = 3
DATA_BEGIN = 5
EXPERIMENT_DB = '/home/walesi/data/experiment.xls'


class TGMS(Experiment):
    """
    Analysis method that contains all pertinent information
    for NETL-TGMS data.
    Most information comes from Experiment.__init__() with a few exceptions
    procedure contains all pertinent information needed to calculate additional _curves

    """
    def __init__(self,
            xlfile=EXPERIMENT_DB,
            sheet='TGMS',
            prompt=None,
            debug=0):


#        self._raw_columns = {'Curve', [column, 'label']
#                }

        self._raw_columns = {'rel_sec' : [0, 'Relative Time [s]'],
                'mass' : [1, 'Mass [mg]'],
                'temp' : [2, 'Temperature [C]'],
                'change' : [3, 'Weight Change [%]']
                }

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

        self.init_param(row_params)

        # construct experiment name
        self.set_param('Name', '%s-%s.%i' % (row[1], row[2], row[3]))

        # initial date and time (for reference)
        dcol = 1 # date column in txt file @UnusedVariable
        tcol = 2 # time column in txt file @UnusedVariable

        # we do all plots based off relative time
        self.add_curve('rel_hr',[float(sec)/3600 for sec in self._curves['rel_sec']], 'Relative Time [hr]')

        self._labels = {}


