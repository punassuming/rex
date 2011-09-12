from rex import *
from pylab import *
import pickle
    
db_path = '~/data/'
cur = []; par = []
for i in range(140):
    try:
        pfr = type.LABVIEW(prompt=i)
        cur.append(pfr._curves)
        par.append(pfr._params)
    except:
        pass
    
pickle.dump(cur, open(db_path+'lv_curves.db','wb'))
pickle.dump(par, open(db_path+'lv_params.db','wb'))


# now try to parse out objects in params
for i in par:
    if OC2 in i.get('name'):
        print i.get('temp:ads')
        
for i in par:
    if 'OC2' in i.get('name'):
        print i.get('temp:ads')
        
for i in par:
    if 'OC2' in i.get('name') and 40 < i.get('temp:ads') and 55> i.get('temp:ads'):
        print i.get('name')
        
for i in par:
    if 'OC2' in i.get('name') and 40 < i.get('temp:ads') and 55> i.get('temp:ads'):
        print i.get('notes')
        
for i in range(len(par)):
    if 'OC2' in par[i].get('name') and 40 < par[i].get('temp:ads') and 55> par[i].get('temp:ads'):
        cur[i].ex_plot('time:min','conc:co2',stage=6)
        
show()
from pylab import *
show()
par2 = pickle.load(open('params.db','w'))
par2 = pickle.load(open('params.db'))
par2 = pickle.load(('params.db','r'))
par2 = pickle.load(open('params.db','r'))
_ip.system("ls -F ")
_ip.system("ls -F -la")
cur2 = pickle.load(open('curves.db','rb'))
import pickle as pick2
cur3 = pick2.load(open('curves.db','rb'))
cur2 = pickle.load(open('curves.db','rb'))
par
import pickle
pickle.dump(par, open('params.db','wb'))
pickle.dump(cur, open('curves.db','wb'))
_ip.system("ls -F -la")
import cPickle as cpick
cpick.dump(cur, open('curves2.db','wb'))
cur2 = pickle.load(open('curves2.db','rb'))
cur2 = cpick.load(open('curves2.db','rb'))
_ip.system("ls -F ")
_ip.system("ls -F -la")
exit()
