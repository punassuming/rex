#!/usr/bin/env python
# encoding: utf-8


from rex.utils.tropmi import *

def save_all_params():
# Save params and results from all 200 runs
    for i in range(200):
        print(i)
        append_params(i)

def create_xls():
    params = load_params()

    arrays = []

    for key in params:
        
        c = params[key]

        c['cap:des-ads'] = c['cap:des_mid'] - c['cap:ads_mid']
        c['cap:des-ads:mass'] = (c['cap:des_mid'] - c['cap:ads_mid']) * c['mass:act']
        c['cap:des:ads'] = c['cap:des_mid'] / (c['cap:ads_mid']+0.00000001)
        c['cap:desp:dest'] = c['cap:desp_mid'] / (c['cap:dest_mid']+0.00000001)

        c['co2:ads:equil'], c['co2:desp:equil'], c['co2:dest:equil'] = c['co2:equil']

        del c['co2:equil']

        arrays.append([c[val] for val in sorted(c.keys())])

    arrays.insert(0,sorted(params[4].keys()))

    wb = xw.Workbook(encoding='utf')
    ws = wb.add_sheet('data')

    for r, lst in enumerate(arrays):
        for c, cell in enumerate(lst):
            # print cell, r, c
            if type(cell) is list : cell = str(cell)
            ws.write(r,c,cell)

    wb.save('2102_0228_results.xls')

# dump_params(range=[8])
# save_all_params()
# create_xls()


