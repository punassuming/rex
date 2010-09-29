#!/usr/bin/env python

from rex.experiment import Experiment


HEADER_ROW = 3
DATA_BEGIN = 5
EXPERIMENT_DB = '/home/walesi/data/experiment.xls'

class TGA(Experiment):
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

        delim = ',' #@UnusedVariable

        self._raw_columns = {'time:sec' : [0, 'Relative Time [s]'],
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
                debug = debug)

        # save information from Excel file
        self._curves.add('time:hr', self._curves['time:sec']/3600., 'Time / hr')


        # Construct experiment name

