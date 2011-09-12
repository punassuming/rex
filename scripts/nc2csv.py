#!/usr/bin/env python
'''
script to create a comma-separated list of calculation details that can be put into excel for filtering.
'''

import os
from ase.calculators.jacapo import *
#from Scientific.IO.NetCDF import NetCDFFile as netCDF
import csv

f = open('ncdata.csv','wt')

fieldnames = ['full path',
              'status',
              'max rms force',
              'Total Energy',
              'xc',
              'ft',
              'pw',
              'dw',
              'nkpts']

writer = csv.DictWriter(f,
                        fieldnames=fieldnames,
                        quoting=csv.QUOTE_NONNUMERIC)
headers = {}
for n in fieldnames:
    headers[n] = n
writer.writerow(headers)

for dirp,dirnames,filenames in os.walk('.'):

    for fname in filenames:
        if fname.endswith('.nc'):
            d = {}
            fullpath = os.path.abspath(os.path.join(dirp,fname))

            calc = Jacapo(fullpath)
            atoms = calc.get_atoms()

            d['full path'] = fullpath

            d['status'] = calc.get_status()

            d['pw'] = calc.get_pw()
            d['dw'] = calc.get_dw()
            d['nkpts'] = len(calc.get_bz_k_points())
            d['xc'] = calc.get_xc()
            d['ft'] = calc.get_ft()

            if d['status'] != 'finished':
                writer.writerow(d)
                continue

            d['Total Energy'] = calc.get_potential_energy()

            forces = atoms.get_forces()
            d['max rms force'] = np.max(np.sum(forces**2,axis=1))**0.5

            writer.writerow(d)

f.close()
            
