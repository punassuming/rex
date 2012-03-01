

from rex import *
from rex.utils.tropmi import *
from pylab import *

# lv(159).p.report('capc*')
# lv(160).p.report('capc*')

# lv(159).c.ex_plot('time:hr','flow:act',stage=1)
# lv(160).c.ex_plot('time:hr'time:hr'flow:act', stage =1)

figure()

lv(96).c.ex_plot('time:hr','conc:co2',stage=6)
lv(96).c.ex_plot('time:hr','conc:a:co2', stage=6)

show()

