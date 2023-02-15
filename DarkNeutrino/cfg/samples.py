import numpy as np

# reference signal coupling parameters
refEps =  0.00016552945 # alphaEM*eps^2 = 2e-10
refAd  = 0.25
refUm4 = 1.0e-2

# list of masses generated
sig_pairs = [ (mzd,'10') for mzd in ['0p03','0p1','0p3','1','3'] ]
sig_pairs+= [ ('0p03',mnd) for mnd in ['0p1','0p3','1','3'] ]
# and some associated helpers
sig_tags = {p:"mZD{}_mND{}".format(*p) for p in sig_pairs}
def num(myStr): return float(myStr.replace('p','.'))
sig_masses = {p: (num(p[0]),num(p[1])) for p in sig_pairs}

# Currently these are printout out at the LHE-reading step and filled here by hand.
xsecs={ # all in pb (MG5 default)
    'b': 1.4758064474251178,
    # generated according to the parameters listed above
    # based on the process "p p > w- > mu- vm~"
    "mZD0p03_mND0p1" : 0.21567405402742099,
    "mZD0p03_mND0p3" : 0.21543524959280136,
    "mZD0p03_mND1" : 0.21547111240421904,
    "mZD0p03_mND3" : 0.21480848532452002,
    "mZD0p03_mND10" : 0.20945157574000003,
    "mZD0p1_mND10" : 0.20967051814520002,
    "mZD0p3_mND10" : 0.14754557280233,
    "mZD1_mND10" : 0.14266838948370802,
    "mZD3_mND10" : 0.115890748779982,
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
