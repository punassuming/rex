#!/usr/bin/env python

from rex.experiment import Experiment
import datetime
import numpy as np
import rex.curves.analysis as analysis
import os.path
from rex.settings import PBR_VOID_SPACE, EXPERIMENT_DB

ADSORPTION = 1
DESORPTION_P = 2
DESORPTION_T = 4

class PFR(Experiment):
    """
    Analysis method that contains all pertinent information
    for NETL-MS data.
    Most information comes from Experiment.__init__() with a few exceptions
    procedure contains all pertinent information needed to calculate additional _curves

    """
    def __init__(self,
            xlfile=EXPERIMENT_DB(),
            sheet='PFR',
            prompt=None,
            debug=0,
            autoload=True):

        self._raw_columns = {
            'time:sec' : [3, 'Time / s'],
            'raw:he' : [4,'He Concentration / %'],
            'raw:h2o' : [5, 'H$_2$O Concentration / %'],
            'raw:co2' : [6, 'CO$_2$ Concentration / %'],
            'int:he' : [7, 'He Intensity [m/z]'],
            'int:h2o' : [8, 'H20 Intensity [m/z]'],
            'int:co2' : [9, 'CO2 Intensity [m/z]']
        }

        self._row_params = {'#' : 0,
                'book' : 4,
                'status' : 7,
                'Name' : 1,
                'date' : 6,
                'time:dry' : 24,
                'Run' : 3,
                'conc:He' : 6,
                'conc:H2O' : 9,
                'conc:CO2' : 10,
                'flow:in' : 11,
                'flow:rxn' : 12,
                'timing:abs' : range(13,18),
                'temp:ads' : 20,
                'temp:des' : 21,
                'temp:spg' : 22,
                'temp:ramp' : 23,
                'comment' : 29,
                'loading' : 27,
                'mass:1' : 25,
                'mass:2' : 26
                }


        # After defining the key parameters, we execute our superclasses init
        # which access excel file, pulls info into self._row, and then parses data into self._data_array
        Experiment.__init__(self,
                xlfile=xlfile,
                sheet=sheet,
                prompt=prompt,
                delim = '\t',
                txt_col = 5,
                debug=debug,
                autoload=autoload)

        if hasattr(self, '_curves'):
            self._curves.add('time:hr', self._curves['time:sec']/3600., 'Time / hr')
            self._curves.add('time:hr', self._curves['time:sec']/3600., 'Time / hr')

            """
            lower case is adsorption
            n = name
            N = new line
            t, T = temp
            r = ramp rate
            D = temp change
            p, P = pressure
            h = water concentration
            b = book number
            """

            self._curves._labels = {
                'N':'\n',
                'b':self._params.get('Book'),
                'n':self._params.get('Name'),
                't':'$\mathrm{T}_{ADS} :$ \t\t$%0.1f\,^{\circ}\mathrm{C}$' % (self._params.get('temp:ads')),
                'T':'$\mathrm{T}_{DES} :$ \t\t$%0.1f\,^{\circ}\mathrm{C}$' % (self._params.get('temp:des')),
                'r':'$\mathrm{Ramp:}$ \t$%s\,^{\circ}\mathrm{C/min}$' % (self._params.get('temp:ramp')),
                'D':'$\Delta\mathrm{T:}$ \t$%0.1f\,^{\circ}\mathrm{C}$' % (self._params.get('temp:des') - self._params.get('temp:ads')),
                'p':'$p_{CO_2}$/$p_0:$ \t$0.1$',
                'P':'p$_{CO_2}$/p$_0:$ \t$0.1$ -> $0.0$',
                'h':'%0.1f%% H$_{2}$O' % (100.0*self._params.get('conc:H2O'))
            }

        if (os.path.isfile(self._pick_file) and autoload is True) or (not os.path.isfile(self._ascii_file)) or (self._params.get('status') == 'No'):
            pass
        else:
            #save parameter information from row of excel file
            row = self._row

            # construct experiment name
            self._params.set('Name', '%s-%s.%s' % (row[1], row[2], row[3]))

            # Flux correction from run 11
            self._params.set('Void', PBR_VOID_SPACE)

            self.prompt = prompt

            date = self._curves._raw[1][0]
            time = self._curves._raw[2][0]

            # Parse date into Year Month Day
            # M/D/Y -> Y, M, D
            init_date = [[int(v) for v in date.split('/')][i] for i in [2,0,1]]

            #Parse time into a list of hour, minutes, and seconds
            init_time = [int(a) for a in time.split()[0].split(':')]
            if time.split()[1] == 'PM' and init_time[0] != 12:
                init_time[0] += 12
            init = init_date + [int(v) for v in init_time]

            # Create datetime object for first point (which we will use as our baseline when evaluating relative time)
            self._init = datetime.datetime(*init)
            rel = []
            # TODO is there a more obvious way / modular to do this?
            for time in self._params.get('timing:abs'):
                rel_abs = list(self._init.timetuple()[0:3]) + [int(v) for v in time.split(':')]
                # print rel_abs
                # create datetime object for each point
                rel_abs = datetime.datetime(*rel_abs)
                rel.append(float((rel_abs - self._init).seconds)/3600.)
            self._params.set('timing:rel',rel)

            # stage needs time:hr to complete
            self.get_stage()

            # save mass settings
            m1 = self._params.get('mass:1')
            m2 = self._params.get('mass:2')

            try:
                self._params.set('mass:dm',float(m1)- float(m2))
            except ValueError:
                pass
            try:
                self._params.set('mass:act',float(m1))
            except ValueError:
                pass
            try:
                self._params.set('mass:act',float(m2))
            except ValueError:
                pass

            self.get_temp()
            self.get_flux()
            self.get_coverage()

            # TODO add additional method abbreviations for quick access: i.e. self.c = self._curves.get

            """
            c, C = coverage (corrected)
            z, Z = trapezoidal capacity
            m, M = mid point capacity (uncorrected)
            i, I = mid point capacity (corrected)
            """

            new_labels = {
                'i':'$\mathrm{Mol}_{ADS}\ :$ \t$%0.2f$ $\mathrm{mol\ }CO_2/kg$' % (abs(self._params.get('capc:ads_mid'))),
                'I':'$\mathrm{Mol}_{DES}\ :$ \t$%0.2f$ $\mathrm{mol\ }CO_2/kg$' % (abs(self._params.get('capc:des_mid'))),
                'm':'$\mathrm{Mol}_{ADS}:$ \t$%0.2f$ $\mathrm{mol\ }CO_2/kg$' % (self._params.get('cap:ads_mid')),
                'M':'$\mathrm{Mol}_{DES}:$ \t$%0.2f$ $\mathrm{mol\ }CO_2/kg$' % (self._params.get('cap:des_mid')),
                'c':'$\mathrm{Eff}_{ADS}:$ \t$%0.2f$ $\mathrm{mol\ }CO_2/\mathrm{mol\ }N$' % (self._params.get('effc:ads')),
                'C':'$\mathrm{Eff}_{DES}:$ \t$%0.2f$ $\mathrm{mol\ }CO_2/\mathrm{mol\ }N$' % (self._params.get('effc:des')),
                'z':'$\mathrm{Mol}_{ADS}:$ \t$%0.2f$ $\mathrm{mol\ }CO_2/kg$' % (self._params.get('cap:ads_trap')),
                'X':'$\mathrm{Mol}_{PDES}:$ \t$%0.2f$ $\mathrm{mol\ }CO_2/kg$' % (self._params.get('cap:desp_trap')),
                'Y':'$\mathrm{Mol}_{TDES}:$ \t$%0.2f$ $\mathrm{mol\ }CO_2/kg$' % (self._params.get('cap:dest_trap'))
            }

            self._curves._labels.update(new_labels)
            self._save()

    def get_stage(self):
        # TODO merge with Labview

        hours = self._curves['time:hr']

        # ads: start/stop des: p/t
        begin_ads, end_ads, begin_des, begin_tdes, end_des = self._params.get('timing:rel')

        self._curves._stage[(begin_ads < hours)&(hours < end_ads)] = ADSORPTION
        self._curves._stage[(begin_des < hours)&(hours < begin_tdes)] = DESORPTION_P
        self._curves._stage[(begin_tdes < hours)&(hours < end_des)] = DESORPTION_T

    def get_temp(self):
        TDes = self._params.get('temp:des')
        TAds = self._params.get('temp:ads')
        TRamp = self._params.get('temp:ramp')

        if TDes > TAds + 10:
            # make temp line along with ramp

            ramp_time = self._params.get('timing:rel')[3]
            #print self._params.get('timing:rel')

            t = []
            #print self._curves['time:hr']
            for time in self._curves['time:hr']:
                if time > ramp_time:
                # check if temp is greater than final temp
                    if TRamp == '-':
                        t.append(TDes)
                    elif t[-1] < TDes:
                        dt = (time - oldtime)*60 # time in minutes @UndefinedVariable
                        t.append(t[-1]+TRamp*dt)
                    else:
                        t.append(t[-1])
                else:
                    t.append(TAds)
                oldtime = time #@UnusedVariable
            self._curves.add('temp', t, 'Temperature [$^{\circ}$C]')

    def get_flux(self):
        """
        This will calculate the total molar flux by integrating
        the area between the curve and the CO2 baseline
        """
        Void = self._params.get('Void')
        FlowRxn = self._params.get('flow:rxn')
        FlowIn = self._params.get('flow:in')
        Flows = [FlowRxn*0.9, FlowIn, FlowIn]

        mid = []
        trap = []
        simp = []
        h2o_mid = []

        stages = [ADSORPTION, DESORPTION_P, DESORPTION_T]

        for i, stage in enumerate(stages):

            time = self._curves.get('time:sec',stage)[0]
            co2 = self._curves.get('raw:co2',stage)[0]/100
            water = self._curves.get('raw:h2o',stage)[0]/100
            n2 = 1 - co2 - water
            flow = Flows[i] / n2

            if len(co2) == 0:
                mid.append([np.array([0,0],float),0.000001])
                trap.append(0.0000001)
                simp.append(0.0000001)
                h2o_mid.append([np.array([0,0],float),0.000001])
                continue

            # determine equilibrium water and co2 values

            co2_init = co2[:2].mean()
            co2_finish = co2[-10:].mean()

            h2o_init = water[:2].mean()
            h2o_finish = water[-10:].mean()

            #co2_equil = max(co2_init, co2_finish)
            #h2o_equil = max(h2o_init, h2o_finish)

            flow_finish = Flows[i] / np.mean(n2[-5:])

            if stage == 1:
                co2_baseline = np.ones(len(co2))* co2_finish
            #elif stage == 2:
                #co2_baseline = np.ones(len(co2)) * co2_init
                #water_baseline = np.ones(len(water)) * water_init
            #elif stage == 4:
                #co2_baseline = np.ones(len(co2)) * co2_finish
                #water_baseline = np.ones(len(water)) * water_finish
            else:
                co2_baseline = np.zeros(len(co2))

            water_baseline = np.linspace(h2o_init, h2o_finish, len(water))

            # TODO Assert error if large difference between initial and finish

            per_dif = abs(co2_init - co2_finish) / (1+co2_finish)
            if per_dif > 1.1:
                print 'Large variance between inital and final values of CO2 \n Difference = %s' % per_dif

            # Calc moles on a kg basis (mol / kg), so divide by mass to get total capacity
            calc = abs(flow * co2 - flow_finish * co2_baseline) / 60 / 24.66
            h2o = abs(flow * water - flow_finish * water_baseline) / 60 / 24.66

            #if i == 0:
                #calc = flow * (co2_baseline - co2) / 60  / 24.66
                #h2o = flow * (water - h2o_equil) / 60 / 24.66
            #else:
                #calc = flow * (co2) / 60 / 24.66
                #h2o = flow * (water - h2o_equil) / 60 / 24.66

            # if we are somehow getting negative fluxes
            calc[calc < 0] = 0
            # correct for mass of sample
            if self._params.has_key('mass:act'):
                calc = calc / self._params.get('mass:act')

            mid.append(analysis.midpoint(time, calc))
            trap.append(analysis.trapezoid(time, calc))
            simp.append(analysis.simpson(time, calc))
            h2o_mid.append(analysis.midpoint(time, h2o))

            self.__check__('stage' , stage)
            self.__check__('midpoint : ' , mid[i][1])
            self.__check__('trapezoid : ' , trap[i])
            self.__check__('simpson : ' , simp[i])

        # In order to make the correction appear correct on the curves, we apply a gain to the entire curve in the stage of interest so that the integral over the total area is adjusted for our correction.  An alternate method would be to take away the values at the beginning only, which makes the curve look odd
        mid_flux = [i[0] for i in mid]
        mid1, mid2, mid3  = [i[1] for i in mid]
        mid_sum  = [i[1] for i in mid]
        mid_sum_correction = [mid1-Void, mid2-Void, mid3]
        mid_gain = [mid_sum_correction[i] / mid_sum[i] for i in range(3)]
        for j, i in enumerate(mid_gain):
            if i < 0:
                mid_gain[j] = 0.01
        mid_correction = [mid_gain[i] * mid_flux[i] for i in range(3)]

        h2o_mid_flux = [i[0] for i in h2o_mid]
        #h2o_mid1, h2o_mid2, h2o_mid3  = [i[1] for i in h2o_mid]
        h2o_mid_sum  = [i[1] for i in h2o_mid]
        #h2o_mid_sum_correction = [h2o_mid1-Void, h2o_mid2-Void, h2o_mid3]
        #h2o_mid_gain = [h2o_mid_sum_correction[i] / h2o_mid_sum[i] for i in range(3)]
        #h2o_mid_correction = [h2o_mid_gain[i] * h2o_mid_flux[i] for i in range(3)]


        # Assign Curves
        self._curves.compose('flux', mid_flux , stages, 'Molar Flow / mol kg$^{-1}$s$^{-1}$')
        self._curves.compose('flux:corr', mid_correction , stages, 'Molar Flow / mol kg$^{-1}$s$^{-1}$')
        self._curves.compose('flux:h2o', h2o_mid_flux , stages, 'Molar Flow / mol kg$^{-1}$s$^{-1}$')

        # Save values in params
        #
        # TODO iterate over values to make more streamlined

        self._params.set('cap:ads_h2o_mid', h2o_mid_sum[0])
        self._params.set('cap:des_h2o_mid', h2o_mid_sum[1] + h2o_mid_sum[2])
        self._params.set('cap:desp_h2o_mid', h2o_mid_sum[1])
        self._params.set('cap:dest_h2o_mid', h2o_mid_sum[2])

        self._params.set('cap:ads_mid', mid_sum[0])
        self._params.set('cap:des_mid', mid_sum[1] + mid_sum[2])
        self._params.set('cap:desp_mid', mid_sum[1])
        self._params.set('cap:dest_mid', mid_sum[2])
        self._params.set('capc:ads_mid' , mid_sum_correction[0])
        self._params.set('capc:des_mid' , mid_sum_correction[1] + mid_sum_correction[2])
        self._params.set('capc:desp_mid' , mid_sum_correction[1])
        self._params.set('capc:dest_mid' , mid_sum_correction[2])

        self._params.set('cap:ads_trap', trap[0])
        self._params.set('cap:des_trap', trap[1] + trap[2])
        self._params.set('cap:desp_trap', trap[1])
        self._params.set('cap:dest_trap', trap[2])
        self._params.set('capc:ads_trap' , trap[0] - Void)
        self._params.set('capc:des_trap' , trap[1] + trap[2] - Void)
        self._params.set('capc:desp_trap' , trap[1] - Void)
        self._params.set('capc:dest_trap' , trap[2])

        self._params.set('cap:ads_simp', simp[0])
        self._params.set('cap:des_simp', simp[1] + simp[2])
        self._params.set('cap:desp_simp', simp[1])
        self._params.set('cap:dest_simp', simp[2])
        self._params.set('capc:ads_simp' , simp[-1] - Void)
        self._params.set('capc:des_simp' , simp[1] + simp[2] - Void)
        self._params.set('capc:desp_simp' , simp[1] - Void)
        self._params.set('capc:dest_simp' , simp[2])

    def get_coverage(self):
        loading = self._params.get('loading')
        if loading != 0:
            cov = []
            covcor = []

            stages = [ADSORPTION, DESORPTION_P + DESORPTION_T]

            summing = [1 ,-1]

            # TODO make iteration more streamlined

            for i, stage in enumerate(stages):

                flux = self._curves.get('flux',stage)[0]
                flux_corr = self._curves.get('flux:corr',stage)[0]

                cov.append(analysis.running_sum(flux, summing[i]) / loading)
                covcor.append(analysis.running_sum(flux_corr, summing[i]) / loading)

            # Save Curves
            self._curves.compose('cov', cov, stages, 'Amine Efficiency')
            self._curves.compose('cov:corr', covcor , stages, 'Amine Efficiency')

            # and save parameter information
            self._params.set('effc:ads', covcor[0].max())
            self._params.set('effc:des', covcor[1].max())
            self._params.set('eff:ads', cov[0].max())
            self._params.set('eff:des', cov[1].max())


