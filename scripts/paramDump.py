from rex import *
import pickle
    
db_path = '/home/walesi/data/'
par = {}
for i in range(154):
    try:
        pfr = type.LABVIEW(prompt=i)
        par[i] = pfr._params
    except:
        pass

    # TODO show progress bar on screen

pickle.dump(par, open(db_path+'lv_params.db','wb'))

