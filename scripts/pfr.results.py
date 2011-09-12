#!/usr/bin/env python
from rex import *
import sys
from pylab import *
import plotsize as ps

data =[]
for arg in range(0,71):

    TEST = type.PFR(prompt=arg, autoload = False)
    print arg
    if hasattr(TEST,'_params'):
        """
        for kk, stage in enumerate([1, 6]):
            print arg

                plot_suffix = str(TEST._fig_dir) + "wb/" + '%02d' % (arg) + '-' + TEST._params.get('Name')

                ps.set_figsize_in(8,10.5)
                if TEST._params.get('status') == 'No':
                    args = [('nNr','T'),('nNb','t')],
                    TEST._curves.ex_subplot('time:hr',('raw:he',['raw:h2o','raw:co2']),
                        vert = True,
                        ttls = ('Helium Flow - %d' % (arg),
                            'Water and CO2'),
                        argls = args[kk],
                        stage=stage,
                        color='black')
                    gcf().get_axes()[0].set_ybound(80,100)
                    gcf().get_axes()[1].set_ybound(0,15)

                else:
                    args = [('nNr','T','INZ','C'),('nNb','t','iNz','c')],
                    TEST._curves.ex_subplot('time:hr',
                            ('raw:he',
                                ['raw:h2o','raw:co2'],
                                'flux',
                                'cov'),
                            vert = True,
                            ttls = ('Helium Flow - %d' % (arg),
                                'Water and CO2',
                                'Molar Flux',
                                'Coverage'),
                            argls = args[kk],
                            stage=stage,
                            color='black')
                    gcf().get_axes()[0].set_ybound(80,100)
                    gcf().get_axes()[1].set_ybound(0,15)
                    gcf().get_axes()[2].set_ybound(0,0.006)
                    gcf().get_axes()[3].set_ybound(0,0.5)
                ax = gca()
                text(0.5, 0, TEST._params.get('Comment'),
                       horizontalalignment='center',
                       verticalalignment='bottom',
                       transform = ax.transAxes, fontsize=8)

                savefig('%s.%i.png' % (plot_suffix, stage))
                clf()
        """
        row = []

        header = sort(TEST._params.keys())
        for key in sort(TEST._params.keys()):
            row.append(str((TEST._params[key])))
        data.append(row)

data.insert(0, header)

io.array_to_excel(data, 'new_results.xls', sheet='pfr')

