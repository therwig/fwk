import numpy as np
from collections import OrderedDict
# reference signal couplings
refEps =  0.00016552945 # alphaEM*eps^2 = 2e-10
refAd  = 0.25
refUm4 = 1.0e-2

class sample(object):
    def __init__(self, name, xs, isSM=False, col=None, isPaper=False):
        self.name = name
        self.xs = xs
        self.isSM = isSM
        self.pairs = None
        self.masses = None
        self.col = col
        self.isPaper = isPaper or isSM

# Currently these are printout out at the LHE-reading step and filled here by hand.
samples = [ # all in pb (MG5 default)
    sample('WISR',  3.76, isSM=True, col=600-10), # skim eff is included in the hist normalization!
    sample('WZ',    3.76, isSM=True, col=432-10),
    sample('Wto3L', 3.76, isSM=True, col=616-10),
    # generated according to the parameters listed above
    # from the process "p p > w- > mu- vm~ zd" + CC
    #   without the Z' decayed
    sample("mZD0p03_mND0p07" , 1.491),
    sample("mZD0p03_mND0p1"  , 1.49, isPaper=True),
    sample("mZD0p03_mND0p3"  , 1.489),
    sample("mZD0p03_mND1"  , 1.489, isPaper=True),
    sample("mZD0p03_mND3"  , 1.488),
    sample("mZD0p03_mND10" , 1.448, isPaper=True),

    # sample("mZD0p002_mND10", 3.07),
    # sample("mZD0p003_mND10" , 1.669),
    sample("mZD0p01_mND10"  , 1.415),
    sample("mZD0p1_mND10"   , 1.452),
    sample("mZD0p3_mND10"   , 1.452, isPaper=True),
    sample("mZD1_mND10"     , 1.452),
    sample("mZD3_mND10"     , 1.452, isPaper=True),
]
# apply k factor
for s in samples: s.xs *= 1.37

COLZ=[632,600,8,6,7,9]+list(range(40,50))
iCol=0
for s in samples:
    if not s.col:
        s.col = COLZ[iCol]
        iCol = min(iCol+1, len(COLZ)-1)

# some helpers
bkg_names = [s.name for s in samples if s.isSM]
def num(myStr): return float(myStr.replace('p','.'))
for s in samples:
    if s.isSM: continue
    s.pairs = (s.name.split('_')[0][3:], s.name.split('_')[1][3:])
    s.masses = (num(s.pairs[0]), num(s.pairs[1]))
sig_pairs= [s.pairs for s in samples if not s.isSM]
sig_tags = {s.pairs:s.name for s in samples if not s.isSM}
sig_masses = {s.pairs:s.masses for s in samples if not s.isSM} 

# selected mass points for paper plots
paper_pairs = [('0p03','0p1'), ('0p03','1')] + [ (mzd,'10') for mzd in ['0p03','0p3','3'] ]
paper_tags = {s.pairs:s.name for s in samples if (s.pairs in paper_pairs and not s.isSM)}
paper_masses = {s.pairs:s.masses for s in samples if (s.pairs in paper_pairs and not s.isSM)}

def sortByKeyMass(aDict, keyMass):
    massToKey = {float(k.split('_')[keyMass][3:].replace('p','.')) : k for k in aDict}
    masses = [m for m in massToKey]
    masses.sort()
    toRet = OrderedDict()
    for m in masses: toRet[massToKey[m]] = aDict[massToKey[m]]
    return toRet
def sortByZD(aDict): return sortByKeyMass(aDict, keyMass=0)
def sortByND(aDict): return sortByKeyMass(aDict, keyMass=1)

# legacy
xsecs={s.name : s.xs for s in samples} # all in pb (MG5 default)
