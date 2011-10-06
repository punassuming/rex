#!/usr/bin/env python
import rex.io as io
from rex.curves import Curve
import os
from rex.settings import HEADER_ROW, DATA_BEGIN, KEY_ROW
from fnmatch import fnmatch

try:
    import cPickle as pickle
except:
    import pickle

class Param(dict):
        # Parameter Methods
    def __init__(self, rows, rowdata={}, xl_keys=[]):
        """ Parse all defined values from excel rows into individual paramters """
        dict.__init__(self)

        # if defining values from _row_params
        for i in rowdata.keys():
            if not hasattr(rowdata[i],'__iter__'):
                self.set(i, rows[rowdata[i]])
            else:
                self.set(i, [rows[x] for x in rowdata[i]])

        for i, j in enumerate(xl_keys):
            if j is not None and j != '' and j != 0:
                self.set(j, rows[i])
                # TODO add label attribute to each j and save header
                # information
                # print '%i > %s: %s' % (i,j,rows[i])

    def set(self, name, value):
        self[name] = value

    # define wildcard matching for params
    def __getitem__(self, name):
        if self.has_key(name):
            return dict.__getitem__(self,name)
        elif '*' in name:
            new_dict = {}
            for key in self.match(name):
                new_dict[key] = dict.__getitem__(self,key)
            return new_dict
        else:
            #return 0
            return None

    def match(self, pattern='*'):
        available=[]
        for key in self.keys():
            if fnmatch(key,pattern):
                available.append(key)
        keys = sorted(available)
        return keys

    def report(self, pattern='*'):
        for key in self.match(pattern):
            print "%-17s > %25s" % (key, self[key])

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

        # Get row, header, and key values
        self._get_row_data(prompt)

        # define filenames associated with experiment
        # TODO find way to get txt_col information from SS directly
        path = os.path.dirname(xlfile) + os.sep + self._sh.lower()
        self._ascii_file = path + os.sep + 'data' + os.sep + self._row[txt_col]
        self._fig_dir = path + os.sep + 'figures' + os.sep
        self._pick_file = path + os.sep + 'data' + os.sep + ('%02d-' % prompt) + os.path.splitext(self._row[txt_col])[0] + '.p'

        self.__check__('File name: ',self._ascii_file)

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
                self._params = Param(self._row,row_data=self._row_params, xl_keys=self._keys)
            else:
                self._params = Param(self._row,xl_keys=self._keys)

            # Ease of use abbr
            self.p = self._params
            self.c = self._curves
            self.pl = self._curves.ex_plot
            self.twin = self._curves.ex_twinplot
            self.sub = self._curves.ex_subplot

        else:
            print '%s is not accessible.' % (self._ascii_file)

    # Debugging Method: which accepts object and name and displays text output if init debug > priority
    def __check__(self,name,object,priority=2):
        """        if debug setting > priority, print recevied object    """
        if self._debug > priority:
            print '%s = %s' % (name,object)


    # IO Methods
    def _get_row_data(self, prompt):
        """ pull relevant info (dependant on excel file) and save as object variables """
        self.__check__('prompt',prompt)
        sht =    io.excel_to_array(filename=self._xl, sheet=self._sh)
        # get all useful information from row
        self._header = [sht[HEADER_ROW][x] for x in range(0,len(sht[:][0]))]
        self._keys = [sht[KEY_ROW][x] for x in range(0,len(sht[:][0]))]
        self._row = [sht[prompt+DATA_BEGIN][x] for x in range(0,len(sht[:][0]))]
        # print self._header
        # print self._keys
        # print self._row

    # Pickle Methods
    def _save(self):
        if hasattr(self, '_curves'):
            self.__check__('saving curves', self._pick_file)
            pickle.dump( [self._curves,self._params], open(self._pick_file,'wb') )

    def _load(self):
        if os.path.isfile(self._pick_file):
            self.__check__('loading curves', self._pick_file)
            self._curves, self._params = pickle.load(open(self._pick_file, 'rb'))
