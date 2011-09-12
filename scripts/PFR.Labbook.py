#!/usr/bin/env python

from rex import *
from pylab import *
import plotsize as ps

for prompt in [14,55]:
    ps.set_figsize_in(7,10)

    exp = extype.PFR(prompt=prompt)

    kwargs = {'stage': -1, 'shw':False}

    subplot(411)
    exp.ex_plot('rel_hr','raw_co2',
            ttl=exp.get_param('Name'),
            label='CO2',
            argl='l',
            color='black',
            **kwargs)
    subplot(412)
    exp.ex_plot('rel_hr','raw_he',
            **kwargs)
    twinx()
    exp.ex_plot('rel_hr','raw_h2o',
            color='green',
            lw=2,
            **kwargs)
    subplot(413)
    exp.ex_plot('rel_hr','flux',
            label='Flux',
            argl='l',
            **kwargs)
    subplot(414)
    exp.ex_plot('rel_hr','cov',
            label='Efficiency',
            argl='l',
            **kwargs)
    show()
