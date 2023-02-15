#/usr/bin/env python3
#import ROOT
import argparse
from EventFormat import convert, convertHepMC
from cfg.samples import sig_pairs, sig_tags

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--signals", default=None, help="Comma-separated list of signal points to run")
parser.add_argument("--doBackground", action="store_true", default=False, help="Convert the background")
parser.add_argument("--hepmc", action="store_true", default=False, help="Use HepMC inputs")
args = parser.parse_args()

good_pairs = sig_pairs
if not (args.signals is None):
    good_pairs = [p for p in sig_pairs if sig_tags[p] in args.signals.split(',')]

if len(good_pairs): print("Converting the signal mass points")
for p in good_pairs:
    if args.hepmc:
        fname = "data/hepmc/outS_{}.hepmc.gz".format(sig_tags[p])
        new_fname = fname.replace('.hepmc.gz','.root').replace('/hepmc/','/root/')
        print( " Converting {} to {}".format(fname,new_fname) )
        convertHepMC(fname,new_fname)
    else:
        fname = "data/lhe/outS_{}.lhe.gz".format(sig_tags[p])
        new_fname = fname.replace('.lhe.gz','.root').replace('/lhe/','/root/')
        print( " Converting {} to {}".format(fname,new_fname) )
        convert(fname,new_fname)

if args.doBackground:
    print("Converting the W background events")
    fname='data/lhe/outB1M.lhe.gz'
    new_fname = fname.replace('.lhe.gz','.root').replace('/lhe/','/root/')
    print( "Converting {} to {}".format(fname,new_fname) )
    convert(fname,new_fname)
    
if len(good_pairs): print("Printing out the signal mass point cross section values (in pb)")
import subprocess
for p in good_pairs:
    fname = "data/lhe/outS_{}.lhe.gz".format(sig_tags[p])
    proc = subprocess.run(["zgrep", "Integrated", fname], capture_output=True)
    xs = proc.stdout.rstrip().split()[-1].decode()
    print( '"{}" : {},'.format(sig_tags[p],xs))



    
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
