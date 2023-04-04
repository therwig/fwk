#!/usr/bin/env python3
import sys, os, argparse
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')

from Analysis.eventloop import eventLoop
from Analysis.treeReaderArrayTools import InputTree
from Analysis.output import FriendOutput, FullOutput
from modules.myAnalysis import myAnalysis

from cfg.samples import sig_pairs, sig_tags
from cfg.histograms import getHists
from cfg.cuts import cuts

ROOT.gROOT.ProcessLine(".L functions.cc")

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--signals", default=None, help="Comma-separated list of signal points to run")
parser.add_argument("--doBackground", action="store_true", default=False, help="Convert the background")
parser.add_argument("--doSkims", action="store_true", default=False, help="Split the background by skimming")
# parser.add_argument("--bkgs", default=None, help="Comma-separated list of backgrounds to run") #TODO
parser.add_argument("--maxEvents", default=100000, type=int, help="Maximum events to process")
parser.add_argument("--fullOutput", action="store_true", default=False, help="Write fill output instead of friends")
parser.add_argument("--bdtTag", default='', help="BDT tag to consider")
args = parser.parse_args()

good_pairs = sig_pairs
if not (args.signals is None):
    good_pairs = [p for p in sig_pairs if sig_tags[p] in args.signals.split(',')]

bkgSkims = ["WZ", "Wto3L", "WISR"]

class job(object):
    def __init__(self, fname, skimName=''):
        self.fname = fname
        self.skim = bool(len(skimName))
        self.sfx = skimName

jobs = [job("data/root/outS_{}.root".format(sig_tags[p])) for p in good_pairs]
if args.doBackground:
    if args.doSkims:
        for skim in bkgSkims: jobs += [job('data/root/bSplit.root',skim)]
    else:
        jobs += [job('data/root/bSplit.root')]

for j in jobs:
    print(j.fname, j.skim, j.sfx)

# exit(0)

# for tag in args.bdtTag.split(','):
#     for fn in all_files:
#         friendName = fn.replace('/root/','/bdt/'+tag+'/')
        
def runJob(j):
    fname = j.fname
    print ("Going to analyze the input file: ", fname)
    ifile = ROOT.TFile.Open(fname,'read')
    itree = ifile.Get('Events')
    if len(args.bdtTag):
        itree.AddFriend('Friends', fname.replace('/root/','/bdt/'+args.bdtTag+'/'))
        otree=None
        ofile=None
    else:
        ofile = ROOT.TFile.Open(fname.replace('/root/','/friends/'),'recreate')
        if args.fullOutput:
            otree = FullOutput(ifile, itree, ofile)
        else:
            otree = FriendOutput(ifile, itree, ofile)
    if (itree.GetEntries() > args.maxEvents) and args.maxEvents>0:
        print("Warning! Truncating {:.0f}k entry file ({}) after {:.0f}k entries.".format(itree.GetEntries()/1e3, fname, args.maxEvents/1e3))
    itree = InputTree(itree)

    myAna = myAnalysis()
    if len(args.bdtTag): myAna.fillBDT = True
    if j.skim: myAna.setSkim(j.sfx)
        
    hname = fname.replace('data/root','histograms/'+args.bdtTag).replace('.root',j.sfx+'.root')
    os.system('mkdir -p histograms/'+args.bdtTag)
    hfile = ROOT.TFile.Open(hname,'recreate')
    myAna.bookHistos(hfile, getHists([c for c in cuts]) )
    myAna.setCuts(cuts)
    
    (nall, npass, timeLoop) = eventLoop(inputFile=ifile, outputFile=ofile, inputTree=itree, wrappedOutputTree=otree,
                                        modules=[ myAna ], progress=(100000, sys.stdout), filterOutput=False,
                                        maxEvents=args.maxEvents, # optionally truncate large background sample
                                        )

    # scale the outputs to the number of entries processed
    # sumw = myAna.sumw if myAna.sumw else 1
    # sumw = myAna.cutflow['skim'] if j.skim else myAna.cutflow['good']
    sumw = myAna.cutflow['good'] # denominator is all good events. so skim efficiency is auto-included!
    if not sumw: sumw = 1
    print('sumw is ', sumw)
    for hn in myAna.h.d:
        myAna.h.d[hn].Scale(1./sumw)

    if otree:
        otree.write()
        ofile.Close()
    
    hfile.Write()
    hfile.Close()
    ifile.Close()
    return sumw

# from multiprocessing import Pool
# pool = Pool(4)
# if __name__ == '__main__':
#     ret = dict(pool.map(runJob, jobs))
#     print (ret)
    
for j in jobs:
    runJob(j)
