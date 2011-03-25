#!/usr/bin/env python

import xlwt as xw
import xlrd as xr
import os.path
#from rex.settings import *

def prompted(xlfile, sheet):
  """
  Prompt for experimental information and return selected experiment (file is excel file name + path)
  """

  array = excel_to_array(filename=xlfile, sheet=sheet)
  entries = []
  listing = []

  for y,x in enumerate(range(5,len(array[:][0]))):
    if array[x][0] == '':
      # break upon coming to blank line
      break
    # list pertinent information for each experiment
    entries.append(u'%s-%s.%s  -  %s' % (array[x][0],
        array[x][1], str(array[x][2])[0],
        array[x][(len(array[0][:]) - 2)]))
    listing.append(y)
    #Print out listing of #) entries
    print "%s) %s" % (listing[y], entries[y])

  # Prompt for entry
  prompt = input("Choose selection ")
  if prompt > y:
    exit()
  return prompt


def parse_ascii(ascii, delim='\t', header=True):
  """    Parse all information from csv or tab delimited data and return as array """

  whole = open(ascii).readlines()

  # find number of cols in middle and only save information from sections that have that many columns
  ncols = len(whole[-10].split(delim))

  # initialize data_array matrix
  data_array = []
  for i in range(0,ncols):
    data_array.append([])

  for line in whole:
    line_split = line.split(delim)
    if len(line_split) == ncols:
      if header is True:
        header = False
      else:
        for i, split in enumerate(line_split):
          data_array[i].append(split)
  return data_array

def parse_jdx(file):
  """ Open jdx file and process parameters to obtain transmittance and frequency """
  import re

  file = open(file).readlines()

  x = [] ; y = []

  dx = None
  yfact = 1

  for line in file:
    if re.search('DELTAX',line) is not None:
      dx = float(line.split('=')[-1])
    if re.search('##YFACTOR',line) is not None:
      yfact = float(line.split('=')[-1])
    # Actual Data ( x y y y y y y y )
    if re.search('##',line) is None and dx:
      iline = map(float, line.split())
      xis = [iline[0]]
      yis = iline[1:]
      for i in range(len(yis)-1): #@UnusedVariable
        xis.append(xis[-1] + dx)
      x.extend(xis)
      y.extend(yis)

  xc = [xi*0.9613 for xi in x]
  tran = [yi*yfact for yi in y]
  refl = [1/yi for yi in y]
  n_tran = [yi/max(tran) for yi in tran]
  n_refl = [yi/max(refl) for yi in refl]

  return [x, xc, tran, refl, n_tran, n_refl]

def array_to_excel(data, filename, sheet='data'):
  """
  save information stored in array to file

  data -- list
  filename -- string
  """
  wb = xw.Workbook(encoding='utf')

  ws = wb.add_sheet(sheet)

  #set to landscape for printing
  ws.portrait = 0

  for r,lst in enumerate(data):
    for c,cell in enumerate(lst):
      ws.write(r,c,cell)

  wb.save(filename)

def excel_to_array(filename, sheet):
  """
  Pull information from excel and put into array of lists
  """
  if not os.path.exists(filename):
    raise Exception('Excel file does not exist.')

  wb = xr.open_workbook(filename=filename, encoding_override='latin')
  ws = wb.sheet_by_name(sheet)

  array = []

  for i in range(0,ws.nrows):
    row = []
    for j in range(0,ws.ncols):
      row.append(ws.cell_value(i,j))
    array.append(row)

  return array

"""
def make_results (in_dir, out_file="d:/merged_output.xls"):

  xls_files = glob.glob(in_dir + "*.xls")
  sheet_names = []
  merged_book = xlwt.Workbook()

  [sheet_names.append(os.path.basename(v)[:-4]) for k, v in enumerate(xls_files)]
  for k, xls_file in enumerate(xls_files):
  if len (sheet_names[k]) <= 31:
  book = xlrd.open_workbook(xls_file)
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

"""
