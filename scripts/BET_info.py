from glob import *
import re
entries = []
headentries = []
for files in glob('*[Aa][vV].txt'):
    data = open(files,'r').readlines()

    dic = {}
    headdict = {}

    for i in data[20:]:
        
        dic['name'] = files
        sep = [j for j in i.split('  ') if j != '']
        if len(sep) != 2: continue
        if 'less than' in sep[0]: sep[0] = 'Total pore volume for pores with Radius'
        header = sep[0]
        sep[0] = ''.join(re.split(r'(?<!\ )[a-z]+|\ ',sep[0]))
        dic[sep[0]]=round(float(sep[1].split()[0]),3)
        headdict[sep[0]] = header
    entries.append(dic)
    headentries.append(headdict)

import xlwt as wt

xl_file = 'bet_results.xls'
wb = wt.Workbook(encoding='utf')

ws = wb.add_sheet('bet results')

#set to landscape for printing
#print headdict

all_headers = sorted(headentries, key=lambda x : len(x.keys()))[-1]
#print all_headers

ws.portrait = 0
for c,dic in enumerate(sorted(entries, key=lambda x : x['name'])):
    print dic['name']
    ws.write(0,c+1,dic.pop('name'))
    for r, keys in enumerate(sorted(all_headers.keys())):
        #print keys
        #print all_headers.get(keys)
        if c == 0 : ws.write(r+1,0,all_headers[keys])
        # don't worry if value is not there
        if dic.get(keys) is not None: ws.write(r+1,c+1,dic.get(keys))

        #print dic
wb.save('bet233.xls')

