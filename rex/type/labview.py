#!/usr/bin/env python

from rex.experiment import Experiment
import numpy as np
import rex.curves.analysis as analysis
from rex.settings import * #@UnusedWildImport
import os.path

ADSORPTION = 1
DESORPTION_P = 2
DESORPTION_T = 4

# TODO merge with PFR class and make seperate CMU and NETL subclasses
class LABVIEW(Experiment):
    """
    Analysis method that contains all pertinent information
    CMU packed bed reactor
    Most information comes from Experiment.__init__() with a few exceptions
    procedure contains all pertinent information needed to calculate additional _curves

    """
    def __init__(self,
            xlfile=EXPERIMENT_DB,
            sheet='LABVIEW',
            prompt=None,
            debug=0,
            correct=True,
            autoload=False):

        self._raw_columns = {
                'time:sec' : [0, 'Time (s)' ],
                'flow:dig' : [1, 'Flow (ccm)' ],
                'flow:inert' : [2, 'Total Inert' ],
                'flow:rxn' : [3, 'Flow (ccmTotal Rxn' ],
                'press:in' : [4, 'Pin (psig)' ],
                'press:out' : [5, 'Pout (psig)' ],
                'temp:in' : [6, 'Tin (C)' ],
                'temp:rxn' : [7, 'Trxn (C)' ],
                'ms:14' : [8, '14' ],
                'ms:18' : [9, '18' ],
                'ms:28' : [10, '28' ],
                'ms:32' : [11, '32' ],
                'ms:40' : [12, '40' ],
                'ms:44' : [13, '44' ],
                'int:h2o' : [14, 'H2O' ],
                'int:n2' : [15, 'N2' ],
                'int:o2' : [16, 'O2' ],
                'int:ar' : [17, 'Ar' ],
                'int:co2' : [18, 'CO2' ],
                'conc:a:co2' : [19, 'CO2 Analyzer' ]
                }

        self._row_params = {
                '#' : 0,
                'name' : 1,
                'exp' : 2,
                'run' : 3,
                'book' : 4,
                'water:0' : 10,
                'water:hum' : 11,
                'rxn:0' : 12,
                'rxn:10' : 13,
                'rxn:100' : 14,
                'flow:inert' : 15,
                'flow:rxn' : 16,
                'timing:ads<' : 17,
                'timing:ads>' : 18,
                'timing:des<' : 19,
                'timing:des|' : 20,
                'timing:des>' : 21,
                'time:rel' : range(17,22),
                'temp:ads' : 25,
                'temp:des' : 26,
                'temp:hum' : 27,
                'temp:ramp' : 28,
                'temp:dry' : 29,
                'time:dry' : 30,
                'mass:pre' : 31,
                'pass:post' : 32,
                'loading' : 33,
                'notes' : 35
                }


        # After defining the key parameters, we execute our superclasses init
        # which access excel file, pulls info into self._row, and then parses data into self._data_array
        Experiment.__init__(self,
                delim = ',',
                txt_col = 5,
                xlfile=xlfile,
                sheet=sheet,
                prompt=prompt,
                debug=debug,
                autoload=autoload)

        if hasattr(self, '_curves'):
            self._curves.add('time:hr', self._curves['time:sec']/3600., 'Time [hr]')

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

        # TODO define better checks and do error proofing
        if (os.path.isfile(self._pick_file) and autoload is True) or (not os.path.isfile(self._ascii_file)) or (self._params.get('status') == 'No'):
            pass
        else:
            #save parameter information from row of excel file
            row = self._row

            # construct experiment name
            self._params.set('Name', '%s-%s.%s' % (row[1], row[2], row[3]))

            # Flux correction from run 11
            # self._params.set('Void', PBR_VOID_SPACE)

            self.correct = correct
            self.prompt = prompt

            # find new way to determine stage
            self.get_stage()

            # save mass settings

            m1 = self._params.get('mass:pre')
            m2 = self._params.get('mass:post')


            if m2 is type(float):
                self._params.set('mass:act',m2)
            elif m1 is type(float):
                self._params.set('mass:act',m1)

            if (m2 is type(float)) & (m1 is type(float)):
                self._params.set('mass:delta',m2-m1)

            self.cal_curves()

            self.get_flux()
            #self.get_coverage()

            """
            c, C = coverage (corrected)
            z, Z = trapezoidal capacity
            m, M = mid point capacity (uncorrected)
            i, I = mid point capacity (corrected)
            """

            new_labels = {}

            self._curves._labels.update(new_labels)

            # TODO look into pickle master DB
            # params[prompt][key]
            self._save()

    def cal_curves(self):

        h2o_int = float(self._params.get('water:0')),float(self._params.get('water:hum'))
        co2_int = float(self._params.get('rxn:0')), float(self._params.get('rxn:10')), float(self._params.get('rxn:100'))

        # TODO insert value from excel
        humidity = 2.1
        h2o_val = [0, humidity]
        co2_val = [0,10,100]

        co2_fit = np.polyfit(co2_int, co2_val, 2)
        h2o_fit = np.polyfit(h2o_int, h2o_val, 1)

        # TODO implement error checks for negative concentrations
        co2_conc = np.polyval(co2_fit, self._curves.get('int:co2')[0])
        h2o_conc = np.polyval(h2o_fit, self._curves.get('int:h2o')[0])

        n2_conc = 1 - co2_conc - h2o_conc

        self._curves.add('conc:co2', co2_conc, 'Concentration [%]')
        self._curves.add('conc:h2o', h2o_conc, 'Concentration [%]')
        self._curves.add('conc:n2', n2_conc, 'Concentration [%]')


    def get_stage(self):

        hours = self._curves['time:hr']

        # ads: start/stop des: p/t
        begin_ads, end_ads, begin_des, begin_tdes, end_des = self._params.get('time:rel')

        self._curves._stage[(begin_ads < hours)&(hours < end_ads)] = ADSORPTION
        self._curves._stage[(begin_des < hours)&(hours < begin_tdes)] = DESORPTION_P
        self._curves._stage[(begin_tdes < hours)&(hours < end_des)] = DESORPTION_T


    def get_flux(self):
        """
        This will calculate the total molar flux by integrating
        the area between the curve and the CO2 baseline
        """
        # TODO implement void space at for labview
        Void = 0

        mid_array = []
        trap = []
        simp = []
        h2o_array = []
        co2_baselines = []
        water_baselines = []

        stages = [ADSORPTION, DESORPTION_P, DESORPTION_T]

        old_flow = self._curves.get('flow:dig')[0]
        co2 = self._curves.get('conc:co2')[0]/100

        # correct for mass flow meter correction with CO2
        flows = old_flow / ((1- co2) + co2 / 1.1717)
        self._curves.add('flow:act', flows, 'Flow [sccm]')

        for i, stage in enumerate(stages):

            old_time = self._curves.get('time:sec',stage)[0]
            co2 = self._curves.get('conc:co2',stage)[0]/100
            water = self._curves.get('conc:h2o',stage)[0]/100
            flow = self._curves.get('flow:act',stage)[0]

            # now resample all values to a set dt

            time = np.linspace(old_time[0], old_time[-1], len(old_time))
            co2 = np.interp(time, old_time, co2)
            water = np.interp(time, old_time, water)
            flow = np.interp(time, old_time, flow)

            """
            pylab testing
            #import pylab

            #pylab.plot(time,co2, new_time, new_co2)
            #pylab.savefig('%s-CO2.png' % stage)
            #pylab.clf()
            #pylab.plot(time,flow, new_time, new_flow)
            #pylab.savefig('%s-flow.png' % stage)
            #pylab.clf()
            #pylab.plot(time,water, new_time, new_water)
            #pylab.savefig('%s-H2O.png' % stage)
            #pylab.clf()
            #self._curves.get('raw:',stage)[0]
            """

            # correct for water in stream (recorded on dry basis
            flow = flow * 100 / (100 - water)

            # if length is 0, add one so we don't crap out the integration
            if len(co2) == 0:
                mid_array.append([np.array([0,0],float),0.000001])
                h2o_array.append([np.array([0,0],float),0.000001])
                trap.append(0.0000001)
                simp.append(0.0000001)
                continue

            # determine equilibrium co2 and water values

            #co2_init = co2[:2].mean() / (100-water[:2].mean())
            #co2_finish = co2[-20:].mean() / (100-water[-20:].mean())

            flow_finish = flow[-20:].mean()

            co2_init = co2[:2].mean()
            co2_finish = co2[-20:].mean()


#            co2_equil = min(co2_init, co2_finish)

            water_init = water[:2].mean()
            water_finish = water[-20:].mean()

#            water_equil = min(water_init, water_finish)

            if stage == 1:
                co2_baseline = np.linspace(co2_init, co2_finish, len(co2))

                """
                Possible correction for non uniform baselines

                #elif stage == 2:
                    #co2_baseline = np.ones(len(co2)) * co2_init
                    #water_baseline = np.ones(len(water)) * water_init
                #elif stage == 4:
                    #co2_baseline = np.ones(len(co2)) * co2_finish
                    #water_baseline = np.ones(len(water)) * water_finish
                """

            else:
                co2_baseline = np.zeros(len(co2))

            water_baseline = np.linspace(water_init, water_finish, len(water))

            per_dif = abs(co2_init - co2_finish) / (1 + co2_finish)
            if per_dif > 1.2:
                print 'Large variance between inital and final values of CO2 \n Difference = %s' % per_dif

            # Calc moles on a kg basis (mol / kg), so divide by mass to get total capacity
            # TODO fix this based on flow diagram
            calc = abs(flow * co2 - flow_finish * co2_baseline) / 60 / 24.66
            h2o_calc = abs(flow * water - flow_finish * water_baseline) / 60 / 24.66

            # correct for mass of sample
            if self._params.has_key('mass:act'):
                calc = calc / self._params.get('mass:act')
                h2o_calc = h2o_calc / self._params.get('mass:act')

            mid_array.append(analysis.midpoint(time, calc))
            h2o_array.append(analysis.midpoint(time, h2o_calc))
            trap.append(analysis.trapezoid(time, calc))
            simp.append(analysis.simpson(time, calc))

            co2_baselines.append(co2_baseline * 100)
            water_baselines.append(water_baseline * 100)

            self.__check__('stage' , stage)
            self.__check__('midpoint : ' , mid_array[i][1])
            self.__check__('trapezoid : ' , trap[i])
            self.__check__('simpson : ' , simp[i])

        # In order to make the correction appear correct on the curves, we apply a gain to the entire curve in the stage of interest so that the integral over the total area is adjusted for our correction.  An alternate method would be to take away the values at the beginning only, which makes the curve look odd
        mid_flux = [i[0] for i in mid_array]
        mid  = [i[1] for i in mid_array]
        mid_sum_correction = [mid[0]-Void, mid[1]-Void, mid[2]]
        mid_gain = [mid_sum_correction[i] / mid[i] for i in range(3)]
        mid_correction = [mid_gain[i] * mid_flux[i] for i in range(3)]

        h2o_mid_flux = [i[0] for i in h2o_array]
        h2o_mid  = [i[1] for i in h2o_array]

        # Assign Curves
        self._curves.compose('flux:co2', mid_flux , stages, 'Molar Flux [mol/kg*s]')
        self._curves.compose('flux:c:co2', mid_correction , stages, 'Molar Flux [mol/kg*s]')
        self._curves.compose('conc:co2:baseline', co2_baselines, stages, 'Concentration [mol %]')
        self._curves.compose('flux:h2o', h2o_mid_flux , stages, 'Molar Flux [mol/kg*s]')
        self._curves.compose('conc:h2o:baseline', water_baselines, stages, 'Concentration [mo %]')



        # Save values in params
        self._params.set('cap:ads_mid', mid[0])
        self._params.set('cap:des_mid', mid[1] + mid[2])
        self._params.set('cap:desp_mid', mid[1])
        self._params.set('cap:dest_mid', mid[2])
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
        self._params.set('capc:ads_simp' , simp[0] - Void)
        self._params.set('capc:des_simp' , simp[1] + simp[2] - Void)
        self._params.set('capc:desp_simp' , simp[1] - Void)
        self._params.set('capc:dest_simp' , simp[2])

        self._params.set('cap:ads_h2o_mid', h2o_mid[0])
        self._params.set('cap:des_h2o_mid', h2o_mid[1] + h2o_mid[2])
        self._params.set('cap:desp_h2o_mid', h2o_mid[1])
        self._params.set('cap:dest_h2o_mid', h2o_mid[2])

    def get_coverage(self):
        loading = self._params.get('loading')
        if loading != 0:
            cov = []
            covcor = []

            stages = [ADSORPTION, DESORPTION_P + DESORPTION_T]
            summing = [1,-1]

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



