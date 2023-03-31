import numpy as np
from collections import OrderedDict
# reference signal coupling parameters
refEps =  0.00016552945 # alphaEM*eps^2 = 2e-10
refAd  = 0.25
refUm4 = 1.0e-2

# list of masses generated
sig_pairs = [ (mzd,'10') for mzd in ['0p002','0p003','0p01','0p03','0p1','0p3','1','3'] ]
sig_pairs = [ (mzd,'10') for mzd in ['0p01','0p03','0p1','0p3','1','3'] ]
sig_pairs+= [ ('0p03',mnd) for mnd in ['0p07','0p1','0p3','1','3'] ]
# sig_pairs = [ ('0p03','0p07') ] 
# and some associated helpers
sig_tags = {p:"mZD{}_mND{}".format(*p) for p in sig_pairs}
def num(myStr): return float(myStr.replace('p','.'))
sig_masses = {p: (num(p[0]),num(p[1])) for p in sig_pairs}

def sortByKeyMass(aDict, keyMass):
    massToKey = {float(k.split('_')[keyMass][3:].replace('p','.')) : k for k in aDict}
    masses = [m for m in massToKey]
    masses.sort()
    toRet = OrderedDict()
    for m in masses: toRet[massToKey[m]] = aDict[massToKey[m]]
    return toRet
def sortByZD(aDict): return sortByKeyMass(aDict, keyMass=0)
def sortByND(aDict): return sortByKeyMass(aDict, keyMass=1)
    
    # keys = [k for k in aDict]

# Currently these are printout out at the LHE-reading step and filled here by hand.
xsecs={ # all in pb (MG5 default)
    'b': 3.76,
    # generated according to the parameters listed above
    # from the process "p p > w- > mu- vm~ zd" + CC
    #   without the Z' decayed
    "mZD0p03_mND0p07" : 1.491,
    "mZD0p03_mND0p1"  : 1.49,
    "mZD0p03_mND0p3"  : 1.489,
    "mZD0p03_mND1"  : 1.489,
    "mZD0p03_mND3"  : 1.488,
    "mZD0p03_mND10" : 1.448,

    # "mZD0p002_mND10" : 3.07,
    "mZD0p003_mND10" : 1.669,
    "mZD0p01_mND10"  : 1.415,
    "mZD0p1_mND10"   : 1.452,
    "mZD0p3_mND10"   : 1.452,
    "mZD1_mND10"     : 1.452,
    "mZD3_mND10"     : 1.452,
    # # fix ND=10 GeV. Scan ZD
    # 'mZD0p03_mND10' : 0.5998,
    # 'mZD0p1_mND10'  : 0.6017,
    # 'mZD0p3_mND10'  : 0.6017,
    # 'mZD1_mND10'    : 0.6017,
    # 'mZD3_mND10'    : 0.601 ,
    # # fix ZD=30 MeV. Scan ND
    # 'mZD0p03_mND0p1' : 0.6166,
    # 'mZD0p03_mND0p3' : 0.617 ,
    # 'mZD0p03_mND1'   : 0.6172,
    # 'mZD0p03_mND3'   : 0.616 ,
}
# apply k factor
for n in xsecs: xsecs[n] = 1.37 * xsecs[n]

WmuNu = 6198 # pb (generate p p > w- > mu- vm~)
# Usqr / (np.power(1-np.power(mN/mW,2),2) * (1+np.power(mN/mW,2)/2))


# overwrite xsecs (don't do this by default)
# these numbers assume Umu4 = 1
def overwriteOldXSecs():
    mW=80.3
    for p in sig_pairs:
        mZd, mNd = sig_masses[p]
        # xs = xsecs['b'] # start with inclusive 'W > mu nu' rate
        xs = WmuNu # start with inclusive 'W > mu nu' rate
        # xs = xs * np.power(0.25,2) * np.power(1e-4,2) * np.power(1-np.power(mNd/mW,2),2) * (1+np.power(mNd/mW,2)/2) # start with inclusive 'W > mu nu' rate
        xs = xs * np.power(1-np.power(mNd/mW,2),2) * (1+np.power(mNd/mW,2)/2) # start with inclusive 'W > mu nu' rate
        xsecs[sig_tags[p]] = xs
    
    print("new signal cross sections (overwritten) are:",xsecs)
