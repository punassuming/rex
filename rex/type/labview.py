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
                'temp:in' : [6, 'Temperature of Inlet [$\degree$C]' ],
                'temp:rxn' : [7, 'Temperature of Reactor [$\degree$C]' ],
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
                'conc:a:co2' : [24, 'CO2 Analyzer' ]
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
                'mass:post' : 32,
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

            if type(m2) is float:
                self._params.set('mass:act',m2)
            elif type(m1) is float:
                self._params.set('mass:act',m1)

            if (type(m2) is float) & (type(m1) is float):
                self._params.set('mass:delta',m2-m1)

            self.cal_curves()

            self.get_flux()
            if type(self._params.get('loading')) is float:
                self.get_coverage()

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

        if h2o_conc.any() < 0 or co2_conc.any() < 0:
            print 'Concentration less than zero, check calibration'

        # Even with the warning, we still want to enforce all concentrations above 0

        co2_conc[co2_conc < 0] = 0.
        h2o_conc[h2o_conc < 0] = 0.

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

    def reset_stage(self):
        """
        Reset stage if timing is modified from the command line
        """
        self._curves._stage.fill(0)
        self.get_stage()


    def get_flux(self):
        """
        This will calculate the total molar flux by integrating
        the area between the curve and the CO2 baseline
        """
        # TODO implement more robust void space  for labview
        # from void calculation of 200CCM (060310_flowtest_200_updated.xlsx)
        
        flow_ads = self._params.get('flow:rxn')

        Void_Ads = 0.0

        Void_Des = 0.037
        if self.prompt in [92,93,94]:
            Void_Ads = 0.037
        elif flow_ads == 100:
            Void_Ads = 0.116
        elif flow_ads == 200:
            Void_Ads = 0.281 # 0.116+0.165 additional losses at higher flow

        co2_mid = []
        h2o_mid = []
        co2_mid_flux, h2o_mid_flux = [],[]
        co2_norm_flux  = []
        dt_time = []
        trap = []
        simp = []
        DT = []
        equil_co2 = []
        co2_baselines = []
        h2o_baselines = []

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
            # if length is 0, add one so we don't crap out the integration
            if len(co2) == 0:
                
                
                co2_mid.append(0.000001)
                co2_norm_flux.append(np.array([0,0],float))
                co2_mid_flux.append(np.array([0,0],float))
                h2o_mid.append(0.000001)
                h2o_mid_flux.append(np.array([0,0],float))
                trap.append(0.0000001)
                simp.append(0.0000001)
                equil_co2.append(-1)
                DT.append(-1)
                h2o_baselines.append(np.array([0,0],float))
                co2_baselines.append(np.array([0,0],float))
                dt_time.append(np.array([0,0],float))
                continue

            # now resample all values to a set dt
            # TODO set all timesteps as constant (5s) in order to plot Desorption P & T swing together

            dt = 5.0

            #time = np.linspace(old_time[0], old_time[-1], len(old_time))
            time = np.arange(old_time[0], old_time[-1], dt)
            # interpolate each curve to match time
            co2 = np.interp(time, old_time, co2)
            water = np.interp(time, old_time, water)
            flow = np.interp(time, old_time, flow)

            DT.append(time[1] - time[0])
            #print 'dt for this calculation is: ', dt

            # Flow Calculations
            # correct for water in stream (recorded on dry basis
            flow = flow * 1 / (1 - water)
            flow_equil = flow[-5:].mean()

            # determine equilibrium co2 and water values
            
            h2o_equil = water[-5:].mean()

            if stage == 1: # or stage == 4:
                co2_equil = max(0.0,co2[-5:].mean())
            # Define special desorption cases (10%)
            elif self.prompt in [92,93,94]:
                co2_equil = 0.1000
            else:
                co2_equil = 0.00002

            # Define baseline curve based on 
            co2_baseline = np.ones(len(co2)) * co2_equil
            h2o_baseline = np.ones(len(co2)) * h2o_equil

            # Calc moles on a kg basis (mol / kg), so divide by mass to get total capacity
            # TODO fix this based on flow diagram

            #print 'flow rate is ', flow_equil
            #print 'Amount (ccm) of CO2 in stream is ', co2_equil

            #print 'flow is ', flow[-10]
            #print 'Amount close to end ', co2[-2]




            if stage == 1:
                co2_calc = abs(flow * co2 - flow_equil * co2_baseline) / 60 / 24.66
            else:
                co2_calc = (flow * co2 - flow_equil * co2_baseline) / 60 / 24.66
                
            if co2_calc.any() < 0:
                print 'CO2 integration is less than zero, check it out'
                co2_calc[co2_calc < 0] = 0.00001

            h2o_calc = abs(flow * water - flow_equil * h2o_baseline) / 60 / 24.66

            # correct for mass of sample
            if self._params.has_key('mass:act'):
                co2_calc = co2_calc / self._params.get('mass:act')
                h2o_calc = h2o_calc / self._params.get('mass:act')

            flux_co2, mid_co2 = analysis.midpoint(time, co2_calc)
            flux_h2o, mid_h2o = analysis.midpoint(time, h2o_calc)
            

            # Calculation Results (for params)
            co2_mid.append(mid_co2)
            h2o_mid.append(mid_h2o)
            
            trap.append(analysis.trapezoid(time, co2_calc))
            simp.append(analysis.simpson(time, co2_calc))

            equil_co2.append(co2_equil)

            # curve composition
            co2_mid_flux.append(flux_co2)
            h2o_mid_flux.append(flux_h2o)
                        
            co2_baselines.append(co2_baseline * 100)
            h2o_baselines.append(h2o_baseline * 100)

            dt_time.append(time)

            # TODO reinterpolate fluxes back to realtime
            
            co2_norm_flux.append(np.interp(old_time, time, flux_co2))


            self.__check__('stage' , stage)
            self.__check__('midpoint : ' , co2_mid[i])
            self.__check__('trapezoid : ' , trap[i])
            self.__check__('simpson : ' , simp[i])

        # In order to make the correction appear correct on the curves, we apply a gain to the entire curve in the stage of interest so that the integral over the total area is adjusted for our correction.  An alternate method would be to take away the values at the beginning only, which makes the curve look odd
        mid_void = [max(co2_mid[0]-Void_Ads,0.000001), max(co2_mid[1]-Void_Des,0.000001), co2_mid[2]]
        mid_correction = [mid_void[i] / co2_mid[i] * co2_norm_flux[i] for i in range(3)]

        # Assign Curves
        self._curves.compose('flux:dt:co2', co2_mid_flux , stages, 'Molar Flux [mol/kg*s]')
        # Reinterpolated flux values (to work with time:hr)
        self._curves.compose('flux:co2', co2_norm_flux , stages, 'Molar Flux [mol/kg*s]')
        self._curves.compose('flux:c:co2', mid_correction , stages, 'Molar Flux [mol/kg*s]')
        self._curves.compose('conc:co2:baseline', co2_baselines, stages, 'Concentration [mol %]')
        self._curves.compose('flux:h2o', h2o_mid_flux , stages, 'Molar Flux [mol/kg*s]')
        self._curves.compose('conc:h2o:baseline', h2o_baselines, stages, 'Concentration [mo %]')
        
        # need a special normalized time to plot all these
        self._curves.compose('time:dt:sec', dt_time, stages, 'Time [s]')
        self._curves.compose('time:dt:hr', [i / 3600. for i in dt_time], stages, 'Time [hr]')

        # Save values in params
        self._params.set('cap:ads_mid', co2_mid[0])
        self._params.set('cap:des_mid', co2_mid[1] + co2_mid[2])
        self._params.set('cap:desp_mid', co2_mid[1])
        self._params.set('cap:dest_mid', co2_mid[2])
        self._params.set('capc:ads_mid' , mid_void[0])
        self._params.set('capc:des_mid' , mid_void[1] + mid_void[2])
        self._params.set('capc:desp_mid' , mid_void[1])
        self._params.set('capc:dest_mid' , mid_void[2])

        self._params.set('cap:ads_trap', trap[0])
        self._params.set('cap:des_trap', trap[1] + trap[2])
        self._params.set('cap:desp_trap', trap[1])
        self._params.set('cap:dest_trap', trap[2])
        self._params.set('capc:ads_trap' , trap[0] - Void_Ads)
        self._params.set('capc:des_trap' , trap[1] + trap[2] - Void_Des)
        self._params.set('capc:desp_trap' , trap[1] - Void_Des)
        self._params.set('capc:dest_trap' , trap[2])

        self._params.set('cap:ads_simp', simp[0])
        self._params.set('cap:des_simp', simp[1] + simp[2])
        self._params.set('cap:desp_simp', simp[1])
        self._params.set('cap:dest_simp', simp[2])
        self._params.set('capc:ads_simp' , simp[0] - Void_Ads)
        self._params.set('capc:des_simp' , simp[1] + simp[2] - Void_Des)
        self._params.set('capc:desp_simp' , simp[1] - Void_Des)
        self._params.set('capc:dest_simp' , simp[2])

        self._params.set('cap:ads_h2o_mid', h2o_mid[0])
        self._params.set('cap:des_h2o_mid', h2o_mid[1] + h2o_mid[2])
        self._params.set('cap:desp_h2o_mid', h2o_mid[1])
        self._params.set('cap:dest_h2o_mid', h2o_mid[2])
        
        self._params.set('co2:equil', equil_co2)
        self._params.set('dt', DT)

    def get_coverage(self):
        loading = self._params.get('loading')
        if loading != 0:
            cov = []
            covcor = []

            stages = [ADSORPTION, DESORPTION_P + DESORPTION_T]
            summing = [1,-1]

            for i, stage in enumerate(stages):
                co2 = self._curves.get('conc:co2',stage)[0]/100
                if len(co2) == 0:
                    cov.append(np.array([0,0],float))
                    covcor.append(np.array([0,0],float))
                    continue

                flux = self._curves.get('flux:dt:co2',stage)[0]
                #flux_corr = self._curves.get('flux:c:co2',stage)[0]


                cov.append(analysis.running_sum(flux, summing[i]) / loading)
                #covcor.append(analysis.running_sum(flux_corr, summing[i]) / loading)



            # Save Curves
            self._curves.compose('cov', cov, stages, 'Amine Efficiency')
            #self._curves.compose('cov:corr', covcor , stages, 'Amine Efficiency')

            # and save parameter information
            #self._params.set('effc:ads', covcor[0].max())
            #self._params.set('effc:des', covcor[1].max())
            self._params.set('eff:ads', cov[0].max())
            self._params.set('eff:des', cov[1].max())



