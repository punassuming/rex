#!/usr/bin/env python
import rex.io as io
from rex.curves import Curve
import os
import pickle
from rex.settings import HEADER_ROW, DATA_BEGIN

class Param(dict):
        # Parameter Methods
    def __init__(self, rows, rowdata={}):
        """ Parse all defined values from excel rows into individual paramters """
        dict.__init__(self)

        for i in rowdata.keys():
            if not hasattr(rowdata[i],'__iter__'):
                self.set(i, rows[rowdata[i]])
            else:
                self.set(i, [rows[x] for x in rowdata[i]])

    def set(self, name, value):
        self[name] = value

    def get(self, name):
        if self.has_key(name):
            return self[name]
        else:
            return 0

class Experiment:
    """
    This class represents the default experimental data super class that
    all individual classes call to

    Variables that can be called to Experiment:
    xlfile = path to excel file
    sheet = name of experimental sheet
    prompt = experimental number (starts with 0)
    delim = either \t or ,
    txt_col = column in row that contains ascii data filename
    debug = whether we should print out variables (0-10, 0 equals NO)
    """

    def __init__(self,
            xlfile='',
            sheet='',
            text='',
            prompt=None,
            delim='\t',
            txt_col = 6,
            autoload=False,
            debug = 0):

        # Debug values from 0 -> 2
        self._debug=debug

        self._xl = xlfile
        self._sh = sheet

        # Figure out which experiment to process and prompt if not specified at startup
        if prompt is None:
            prompt = io.prompted(xlfile, sheet)

        # Get row as list in self._row
        self._get_row_data(prompt)

        # Construct filenames
        path = os.path.dirname(xlfile) + os.sep + self._sh.lower()
        self._ascii_file = path + os.sep + 'data' + os.sep + self._row[txt_col]
        self._fig_dir = path + os.sep + 'figures' + os.sep
        self._pick_file = path + os.sep + 'data' + os.sep + ('%02d-' % prompt) + os.path.splitext(self._row[txt_col])[0] + '.p'
        print self._ascii_file
        # Import saved data (self._param and self._curves) or parse ASCII file
        if os.path.isfile(self._pick_file) and autoload is True:
            self._load()

        elif os.path.isfile(self._ascii_file):
            self._data_array = io.parse_ascii(self._ascii_file , delim)

            # if we have defined _raw_columns then add all of those curves (defined for each exp type)
            if hasattr(self, '_raw_columns'):
                self._curves = Curve(self._data_array,self._raw_columns)
            else:
                self._curves = Curve(self._data_array)

            if hasattr(self, '_row_params'):
                self._params = Param(self._row,self._row_params)
            else:
                self._params = Param([])

            # Ease of use abbr
            self.pg = self._params.get
            self.cg = self._curves.get
            self.pl = self._curves.ex_plot
            self.sub = self._curves.ex_subplot

        else:
            print '%s is not accessible.' % (self._ascii_file)

    # debugging method which accepts object and name and displays text output if init debug > priority
    def __check__(self,name,object,priority=2):
        """    if debug setting > priority, print recevied object    """
        if self._debug > priority:
            print '%s = %s' % (name,object)

    def _get_row_data(self, prompt):
        """ pull relevant info (dependant on excel file) and save as object variables """
        self.__check__('prompt',prompt)
        sht =  io.excel_to_array(filename=self._xl, sheet=self._sh)
        # get all useful information from row
        self._header = [sht[HEADER_ROW][x] for x in range(0,len(sht[:][0]))]
        self._row = [sht[prompt+DATA_BEGIN][x] for x in range(0,len(sht[:][0]))]


    # Pickle Methods
    def _save(self):
        if hasattr(self, '_curves'):
            self.__check__('saving curves', self._pick_file)
            pickle.dump( [self._curves,self._params], open(self._pick_file,'wb') )

    def _load(self):
        if os.path.isfile(self._pick_file):
            self.__check__('loading curves', self._pick_file)
            self._curves, self._params = pickle.load(open(self._pick_file, 'rb'))
