#!/usr/bin/env python
# encoding: utf-8

from rex import *
from rex.utils.tropmi import *


netl = type.PFR(prompt=20)

print netl._params.keys()

figure()

netl._curves.ex_plot('time:hr','raw:co2')


labv = type.LABVIEW(prompt=165)


print labv.p.keys()

labv.c.ex_plot('time:hr','conc:co2')

show()
