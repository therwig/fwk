import numpy as np
from collections import OrderedDict
# reference signal couplings
refEps =  0.00016552945 # alphaEM*eps^2 = 2e-10
refAd  = 0.25
refUm4 = 1.0e-2

class sample(object):
    def __init__(self, name, xs, isSM=False, col=None, isPaper=False, dropLepton=False, pfx=''):
        self.name = name
        self.xs = xs
        self.isSM = isSM
        self.pairs = None
        self.masses = None
        self.col = col
        self.pfx = pfx
        self.isPaper = isPaper or isSM
        self.dropLepton = dropLepton
        

# Currently these are printout out at the LHE-reading step and filled here by hand.
# bTagEff2=0.01 # currently unused
tkIneff=0.05
lepEff=0.85**3
# ttCutEff = 1112.61/95567.74 # rescale the ttbar killing cut (HTc>30) to still use all MC events UNUSED
samples = [ # all LO XS in pb (MG5 default)
    # sample('WISR',  3.76, isSM=True, col=600-10),
    # sample('WZ',    3.76*0.2206, isSM=True, pfx='bSplit', col=432-10),
    # sample('Wto3L', 3.76*0.7794, isSM=True, pfx='bSplit', col=616-10),
    sample('WZ',    3.76, isSM=True, pfx='', col=432-10), # no split
    # sample('WZ',    3.76*0.2206, isSM=True, pfx='', col=432-10),
    # sample('Wto3L', 3.76*0.7794, isSM=True, pfx='', col=616-10),
    # for lost leptons, assume 99% veto efficiency (i.e. tk efficiency), times 2x for each leg
    # sample('ZZ',  0.59 * (2*0.01), isSM=True, dropLepton=True, col=860-9), ## TODO: XS 
    sample('ZZ3L',  0.59 *  65726./483331, isSM=True, col=860-6), ## 
    sample('ZZ4L',  0.59 * 290118./483331 * tkIneff, isSM=True, col=860-9), ## tk veto eff
    # loosest b-jets are 93% (cms) or 85% (atlas)
    # https://indico.cern.ch/event/967689/contributions/4083041/attachments/2130779/3590310/BTagPerf_201028_UL18WPs.pdf
    # essentially all are within eta of 2.5 - Fig 5 of https://arxiv.org/pdf/1012.4230.pdf
    # we can take 1% or so
    sample('ttZ3L',  3.44 * 131757./1e5, isSM=True, col=632+2), ## 
    sample('ttZ4L',  3.44 * 104002./1e5 * tkIneff, isSM=True, col=632-7), ## tk veto eff
    # sample('ttZ3L',  3.44 * 131757./1e5 * bTagEff2, isSM=True, col=632+2), ## 
    # sample('ttZ4L',  3.44 * 104002./1e5 * bTagEff2 * tkIneff, isSM=True, col=632-7), ## tk veto eff

    # generated according to the parameters listed above
    # from the process "p p > w- > mu- vm~ zd" + CC
    #   without the Z' decayed
    sample("mZD0p03_mND0p035" , 1.494),
    sample("mZD0p03_mND0p04" , 1.494, isPaper=True),
    sample("mZD0p03_mND0p05" , 1.494),
    sample("mZD0p03_mND0p06" , 1.494),
    sample("mZD0p03_mND0p07" , 1.491),
    sample("mZD0p03_mND0p1"  , 1.49, isPaper=0),
    sample("mZD0p03_mND0p3"  , 1.489),
    sample("mZD0p03_mND1"  , 1.489, isPaper=True),
    sample("mZD0p03_mND3"  , 1.488),
    sample("mZD0p03_mND10" , 1.448, isPaper=0),

    # mND = 3x mZD
    sample("mZD0p01_mND0p03" , 1.495),
    sample("mZD0p1_mND0p3"   , 1.495),
    sample("mZD1_mND3"       , 1.492),

    # sample("mZD0p002_mND10", 3.07),
    # sample("mZD0p003_mND10" , 1.669),
    # sample("mZD0p01_mND10"  , 1.415),
    sample("mZD0p1_mND10"   , 1.452),
    sample("mZD0p3_mND10"   , 1.452, isPaper=0),
    sample("mZD1_mND10"     , 1.452),
    sample("mZD3_mND10"     , 1.452, isPaper=True),
]

if False:
    _samples=[]
    for s in samples:
        if s.isPaper or s.isSM:
            _samples += [s]
    samples = _samples

# apply k factor, efficiencies
for s in samples:
    s.xs *= lepEff
    if 'ZZ' in s.name:
        s.xs *= 1 # TODO k factor for Z+jets        
        s.xs *= 2 # XS are for Z > mu mu. Double to add "e e".
    elif 'ttZ' in s.name:
        s.xs *= 1 # TODO k factor for ttbar
        # nb: no additional facor for lepton flavors, since top decays are inclusive!
    else:
        s.xs *= 1.37 # k factor for W+jets (and also signal)
        s.xs *= 2 # XS are for W > mu nu. Double to add "e nu".

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
