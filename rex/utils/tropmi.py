'''
File: tropmi.y
Author: Rich Alesi
Description: Common functions to use with REX
Last Change: 2012 Feb 28
'''
#===============================================
# import section

from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter
from pylab import plot, legend, xlabel, gca, figure, xlim, ylim, twinx, ylabel, subplot, gcf, scatter, show, savefig, clf, subplots_adjust, title, figtext
from rex import type as rtype
from rex.curves.rc import set_figsize_in, set_mode, set_figsize
from rex.curves.insitu import stack_plots, bnw
from rex.settings import DATA_DIR
from rex.utils.tropmi import *
import glob
import matplotlib.pyplot as plt
import os,sys
import pickle
import rex.type as rtype
import xlrd as xr
import xlwt as xw

def script_stats():
    print "CWD: ",os.getcwd()
    print sys.path[0]
    print "Script: ",sys.argv[0]
    print "Script: ",sys.argv[0]
    print ".EXE: ",os.path.dirname(sys.executable)
    print "Script dir: ", os.path.realpath(os.path.dirname(sys.argv[0]))
    pathname, scriptname = os.path.split(sys.argv[0])
    print "Relative script dir: ",pathname
    print "Script dir: ", os.path.abspath(pathname)

#===============================================
# pylab quick methods

def dd():
    # quick method to draw when using ion()
    draw();draw()

def s():
    show()

def c():
    clf()

def figroot():
    return os.path.splitext(os.path.split(sys.argv[0])[1])[0]


def save(name):
    # method to save figure based on name
    root = figroot()
    for ext in ['png','svg','eps']:
        if not os.path.isdir(ext):
            os.mkdir(ext)
        try:
            savefig(ext+os.sep+root+'.'+name+'.'+ext, bbox_inches='tight', dpi=300)
        except:
            savefig(ext+os.sep+root+'.'+name+'.'+ext, dpi=300)

def fig_label(name):
    figtext(0.03,0.96, name,size=12,weight='bold',ha='left',va='top')

def disable_axis(ax, which):
    # disable top, bottom, right or left axes
    for axis in which:
        ax.axis[axis].set_visible(False)

class FixedOrderFormatter(ScalarFormatter):
    """Formats axis ticks using scientific notation with a constant order of 
    magnitude"""
    def __init__(self, order_of_mag=0, useOffset=True, useMathText=False):
        self._order_of_mag = order_of_mag
        ScalarFormatter.__init__(self, useOffset=useOffset, 
                                 useMathText=useMathText)
    def _set_orderOfMagnitude(self, range):
        """Over-riding this to avoid having orderOfMagnitude reset elsewhere"""
        self.orderOfMagnitude = self._order_of_mag

  
ll = {'loc':0, 'numpoints':1, 'frameon':False}
att = {'markersize': 8.0, 'markeredgewidth': 1.0, 'markevery': 10, 'alpha': 1.0}
tt = {'ha':'center','ma' :'center','va':'center'}


"""
IDEAS

vertical lines                 | axvline(x=0.5, lw=1,linestyle=':', color='black' )
remove top ticks               | gca().axis["top"].major_ticks.set_visible(False)
2 column legend                | markerscale=0.8, ncol=2, mode='expand'
set up size of axes            | axes([0.15,0.1,0.75,0.8])
subplot(211) or (112)          | up/down or left/right
pull from csv                  | capacities, temp, press = [ csv2rec('capacities.csv')[i] for i in ['capacity','temp','press'] ]
determine time to half filling | print times[cumulative >= cumulative[-1]/2][0]
iterating with subplots        | subplot('13%d' % (k+1))


# parsing through parameter db
if 'OC2' in par[i].get('name') and 40 < par[i].get('temp:ads') and 55> par[i].get('temp:ads'):


# add second data set to top axis
ax1 = ax.twiny()
new_temp = ['%2.1f' % i for i in fil.reduce(DBN._curves.get('temp',stage=6)[0],10).tolist()]
ax1.set_xlabel('Temperature / $^{\circ}$C')
ax1.xaxis.set_major_locator(MaxNLocator(10))
ax1.set_xticklabels(new_temp)
for i, label in enumerate(ax1.xaxis.get_ticklabels()):
    # label is a Text instance
    if i == 0:
        label.set_color('white')

    Changing the order of magnitude of axis
    ax.yaxis.set_major_formatter(FixedOrderFormatter(-2))
"""

#===============================================
# misc. functions

def intoList(not_list):
    # enforce list type
    if type(not_list) is not list:
        not_list = [not_list]
    return not_list

def no_nones(list1,list2):
    # remove indices containing None from two lists of same length
    if len(list1) != len(list2):
        print 'lists must be same length'
        return 0, 0
    for i in range(len(list1)):
        if list1[i] is None:
            list1.pop(i)
            list2.pop(i)
    for i in range(len(list2)):
        if list2[i] is None:
            list1.pop(i)
            list2.pop(i)
    return list1, list2

def get_values(xs, ys, location = 1400, bound=3):
    # xs and ys are indices and value pairs
    # returns list of values from all ys, where xs are within bound
    values = []

    for i in range(len(xs)):
        x = xs[i]
        y = ys[i]

        # find the index @ location for each curve
        values.append(y[(location - bound < x) & ( x > location + bound)][0])
    return values


def align_array(xs, ys, location = 1400, bound=3):

    if len(xs) != len(ys):
        print "Error on common array size between X and Y"
        exit()

    index = []
    for i in range(len(xs)):
        # find the index @ location for each curve
        index.append((location - bound < xs[i]) & ( xs[i] > location + bound))

        values = ys[i][index[-1]][0]
        if i == 0:
            baseline = values
        offset = values - baseline
        ys[i] = ys[i] - offset

    return xs, ys

#===============================================
# rex quick plotting functions

class lv(rtype.LABVIEW):
    def __init__(self, i):
        rtype.LABVIEW.__init__(self, prompt=i)

def load_params(name='lv_params'):
    # unpickle params db as list
    # i.e. params = load_params()
    return pickle.load(open(DATA_DIR()+os.sep+name+'.db','rb'))

def append_params(i, name='lv_params'):
    par = load_params(name=name)
    try:
        pfr = lv(i)
        par[i] = pfr._params
        pickle.dump(par, open(DATA_DIR()+os.sep+name+'.db','wb'))
    except:
        pass
    return par

def dump_params(range=range(200), name='lv_params'):
    par = {}
    for i in range:
        print 'pfr prompt ', i
        # try:
        pfr = lv(i)
        par[i] = pfr._params
        # except:
            # pass
    # TODO show progress bar on screen
    pickle.dump(par, open(DATA_DIR()+os.sep+name+'.db','wb'))
    return par

def lpl(prompts, X, Y, stage, argl=''):
    # argl can be based on ex_label, or a key in params
    argl = intoList(argl)
    for j, i in enumerate(intoList(prompts)):
        pfr = lv(prompt=i)
        pfr.pl(X,Y, 
                label=(pfr.pg(argl[j]) or argl[j]), 
                argl='l', 
                stage=stage)

def flux(prompts, stage, argl=''):
    argl = intoList(argl)
    for j, i in enumerate(intoList(prompts)):
        pfr = lv(prompt=i)
        pfr.pl('time:dt:hr','flux:co2', 
                label=(pfr.pg(argl[j]) or argl[j]), 
                argl='l', 
                stage=stage)

def conc(prompts, stage, argl=''):
    argl = intoList(argl)
    for j, i in enumerate(intoList(prompts)):
        pfr = lv(prompt=i)
        pfr.pl('time:hr','conc:co2', 
                label=(pfr.pg(argl[j]) or argl[j]), 
                argl='l', 
                stage=stage)

def temp(prompts, stage, argl=''):
    argl = intoList(argl)
    for j, i in enumerate(intoList(prompts)):
        pfr = lv(prompt=i)
        pfr.pl('time:hr','temp:rxn', 
                label=(pfr.pg(argl[j]) or argl[j]), 
                argl='l', 
                stage=stage)

def tpd(prompts, stage, argl=''):
    argl = intoList(argl)
    for j, i in enumerate(intoList(prompts)):
        pfr = lv(prompt=i)
        pfr.pl('temp:rxn','conc:co2', 
                label=(pfr.pg(argl[j]) or argl[j]), 
                argl='l', 
                stage=stage)

#===============================================
# excel methods

def params_to_xls(prompts, filename='test.xls'):
    arrays = []
    for i in range(prompts):
        pfr = lv(prompt=i)
        header = sorted(pfr._params.keys())
        arrays.append([pfr._params[val] for val in sorted(pfr._params.keys())])

    arrays.insert(0,header)

    wb = xw.Workbook(encoding='utf')
    ws = wb.add_sheet('data')
    for r, lst in enumerate(arrays):
        for c, cell in enumerate(lst):
            print cell, r, c
            if type(cell) is list : cell = str(cell)
            ws.write(r,c,cell)
    wb.save(filename)


def labbook(prompt):
    pfr = lv(prompt=prompt)
    for kk, stage in enumerate([1, 6]):
        plot_suffix = str(pfr._fig_dir) + "wb/" + '%02d' % (prompt) + '-' + pfr._params.get('Name')

        set_figsize_in(8,10.5)
        if pfr._params.get('status') == 'No':
            args = [('nNr','T'),('nNb','t')],
            pfr._curves.ex_subplot('time:hr',('flow:act',['conc:h2o','conc:co2','conc:a:co2']),
                vert = True,
                ttls = ('Flow - %d' % (prompt),
                    'Water and CO2'),
                argls = args[kk],
                stage=stage,
                color='black')
            # gcf().get_axes()[0].set_ybound(80,100)
            gcf().get_axes()[1].set_ybound(0,15)

        else:
            args = [('nNr','T','INZ','C'),('nNb','t','iNz','c')],
            pfr._curves.ex_subplot('time:hr',
                ('flow:act',
                    ['conc:h2o','conc:co2','conc:a:co2'],
                    'flux:co2',
                    'eff:co2'),
                vert = True,
                ttls = ('Flow - %d' % (prompt),
                    'Water and CO2',
                    'Molar Flux',
                    'Coverage'),
                argls = args[kk],
                stage=stage,
                color='black')
            # gcf().get_axes()[0].set_ybound(80,100)
            gcf().get_axes()[1].set_ybound(0,15)
            gcf().get_axes()[2].set_ybound(0,0.006)
            gcf().get_axes()[3].set_ybound(0,0.5)
        ax = gca()
        text(0.5, 0, pfr._params.get('Comment'),
               horizontalalignment='center',
               verticalalignment='bottom',
               transform = ax.transAxes, fontsize=8)

        savefig('%s.%i.png' % (plot_suffix, stage))
        clf() 

def make_results(in_dir, out_file="d:/merged_output.xls"):

    xls_files = glob.glob(in_dir + "*.xls")
    sheet_names = []
    merged_book = xw.Workbook()

    [sheet_names.append(os.path.basename(v)[:-4]) for k, v in enumerate(xls_files)]
    for k, xls_file in enumerate(xls_files):
        if len (sheet_names[k]) <= 31:
            book = xr.open_workbook(xls_file)
            ws = merged_book.add_sheet(sheet_names[k])
            for sheetx in range(book.nsheets):
                sheet = book.sheet_by_index(sheetx)
                for rx in range(sheet.nrows):
                    for cx in range(sheet.ncols):
                        ws.write(rx, cx, sheet.cell_value(rx, cx))
        else:
            print "File name too long: <%s.xls> (maximum is 31 chars) " % (sheet_names[k])
            print "File <%s.xls> is *not* included in the merged xls file." % (sheet_names[k])
    merged_book.save(out_file)

    print "---> Merged xls file written to %s using the following source files: " % (out_file)
    for k, v in enumerate(sheet_names):
        if len(v) <= 31: print "\t", str(k+1).zfill(3), "%s.xls" % (v)

