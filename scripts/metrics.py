

from rex.utils.tropmi import *
import matplotlib.pyplot as plt
from rex.curves.rc import set_mode


set_mode('present')

testing = [
    
]



def stage_timing():
    pfr = lv(i)

    f = plt.figure()


    pfr.c.ex_twinplot('time:hr',['conc:a:co2','conc:co2'])
    plt.legend(['%s: Analyzer' %(i),'MS'])

    plt.fill_between(pfr.c['time:hr'][pfr.c._stage==1],0,10,facecolor='blue',alpha=0.3)
    plt.fill_between(pfr.c['time:hr'][pfr.c._stage==2],0,10,facecolor='green',alpha=0.3)
    plt.fill_between(pfr.c['time:hr'][pfr.c._stage==4],0,10,facecolor='red',alpha=0.3)

    f.text(.5, .95,i, horizontalalignment='center')
    # plt.legend(['ADS'+pfr.p["cap:ads_mid"],'DES'+pfr.p["cap:des_mid])

def co2_analyzer():

    pfr = lv(i)

    f = plt.figure()


    plt.subplot(141)
    pfr.c.ex_twinplot('time:min',['conc:a:co2','conc:co2'],stage=1)
    plt.subplot(142)
    pfr.c.ex_twinplot('time:min',['conc:a:co2','conc:co2'],stage=6)
    plt.legend(['%s: Analyzer' %(i),'MS'])
    plt.subplot(143)
    pfr.c.ex_plot('time:min','int:co2',stage=1)
    plt.subplot(144)
    pfr.c.ex_plot('time:min','int:co2',stage=6)

    f.text(.5, .95,i, horizontalalignment='center')
    # plt.legend(['ADS'+pfr.p["cap:ads_mid"],'DES'+pfr.p["cap:des_mid])

def test_list():
    for i in testing:
    # for i in range(x*10,(x+1)*10):
        try:
            print i
            # co2_analyzer()
            # stage_timing()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            pass

        show()
    # break


pfr = lv(151)
print pfr.p['cap:des_mid']
figure()
# pfr.c.ex_plot('time:hr','conc:co2',stage=7)
pfr.c.ex_twinplot('time:hr',['ms:28','ms:44'],stage=7)
# pfr.c.ex_twinplot('time:hr',['conc:n2','conc:co2'],stage=7)
# legend(['N$_2$','CO$_2$'])
# ylim(ymin=0)
ylabel('Intensity (arb. units)')
ax = gca()
import matplotlib.pyplot as plt
# plt.yscale('log')

show()

