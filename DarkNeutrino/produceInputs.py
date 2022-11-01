#/usr/bin/env python3
#import ROOT
from EventFormat import convert

sig_mZd_mNd = [ (mzd,'10') for mzd in ['0p03','0p1','0p3','1','3'] ]
sig_files = ["data/lhe/outS_mZD{}_mND{}.lhe.gz".format(*p) for p in sig_mZd_mNd]
all_files = sig_files + ['data/lhe/outB1M.lhe.gz']

for fname in all_files:
    new_fname = fname.replace('.lhe.gz','.root').replace('/lhe/','/root/')
    print( "Converting {} to {}".format(fname,new_fname) )
    convert(fname,new_fname)
    
# print (all_files)

# run 1: default card, bw cutoff = 50 (7640)
# run 2: set bw cutoff to 10 (227)
# run 3: set bw cutoff to 1000 (336)
# run 4: set bw cutoff to 100 (6382)
# run 5: set bw cutoff to 30 (3841)
# run 6: set bw cutoff to 70 (605)
# run 7: bw cutoff 50, set min mll 10 MeV -> 100 MeV (3878)
# run 8: bw cutoff 50, set min mll 10 MeV -> 10 GeV (1250)

# cp /Users/therwig/work/mc/pedro_neutrinos/eventOuputs/outS_mZD3_mND10/Generation/Events/run_01/unweighted_events.lhe.gz     outS_mZD3_mND10.lhe.gz
# cp /Users/therwig/work/mc/pedro_neutrinos/eventOuputs/outS_mZD1_mND10/Generation/Events/run_01/unweighted_events.lhe.gz     outS_mZD1_mND10.lhe.gz
# cp /Users/therwig/work/mc/pedro_neutrinos/eventOuputs/outS_mZD0.3_mND10/Generation/Events/run_01/unweighted_events.lhe.gz   outS_mZD0p3_mND10.lhe.gz
# cp /Users/therwig/work/mc/pedro_neutrinos/eventOuputs/outS_mZD0.1_mND10/Generation/Events/run_01/unweighted_events.lhe.gz   outS_mZD0p1_mND10.lhe.gz
# cp /Users/therwig/work/mc/pedro_neutrinos/eventOuputs/outS_mZD0.030_mND10/Generation/Events/run_01/unweighted_events.lhe.gz outS_mZD0p030_mND10.lhe.gz

# samples=''
