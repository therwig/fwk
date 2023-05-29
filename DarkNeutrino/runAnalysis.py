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

from cfg.samples import sig_pairs, sig_tags, samples
from cfg.histograms import getHists
from cfg.cuts import cuts

ROOT.gROOT.ProcessLine(".L functions.cc")

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--signals", default=None, help="Comma-separated list of signal points to run")
parser.add_argument("--backgrounds", default=None, help="Comma-separated list of backgrounds to run")
parser.add_argument("--doBackground", action="store_true", default=False, help="Convert the background")
parser.add_argument("--oldBackground", action="store_true", default=False, help="Use the old background sample, pre-skimming")
parser.add_argument("--doSkims", action="store_true", default=False, help="Split the background by skimming")
# parser.add_argument("--bkgs", default=None, help="Comma-separated list of backgrounds to run") #TODO
parser.add_argument("--maxEvents", default=100000, type=int, help="Maximum events to process")
parser.add_argument("--fullOutput", action="store_true", default=False, help="Write fill output instead of friends")
parser.add_argument("--bdtTag", default='', help="BDT tag to consider")
args = parser.parse_args()

if args.doSkims: # override all else
    args.signals = ''
    args.doBackground = True
    args.fullOutput = True
    args.maxEvents = -1

good_pairs = sig_pairs
if not (args.signals is None):
    good_pairs = [p for p in sig_pairs if sig_tags[p] in args.signals.split(',')]
    if len(good_pairs)==0:
        print( 'found no matching pairs. Try one of:', [sig_tags[p] for p in sig_pairs])
bkgSkims = ["WZ", "Wto3L"]
# make a skim of the original root file

class job(object):
    def __init__(self, fname, skimName='', bdtTag='', dropLepton=False):
        self.fname = fname
        self.skim = bool(len(skimName))
        self.sfx = skimName
        self.oftree = fname.replace('root/','friends/')
        self.ofhist = fname.replace('data/root/','histograms/'+bdtTag)
        self.ofhist = self.ofhist.replace('.root',self.sfx+'.root')
        self.ifbdt = fname.replace('data/root/','data/bdt/'+bdtTag+'/')
        self.dropLepton = dropLepton

jobs = [job("data/root/outS_{}.root".format(sig_tags[p]),bdtTag=args.bdtTag) for p in good_pairs]
bName = 'bSplit'
if args.doBackground:
    if args.doSkims:
        for skim in bkgSkims:
            jobs += [job('data/root/'+bName+'.root',skim, bdtTag=args.bdtTag)]
            jobs[-1].oftree = jobs[-1].oftree.replace(bName, skim)
    else:
        if args.oldBackground:
            jobs += [job('data/root/'+bName+'.root',bdtTag=args.bdtTag)]
        else:
            for s in samples:
                if not s.isSM: continue
                if args.backgrounds and not (s.name in args.backgrounds.split(',')): continue
                jobs += [job('data/root/'+s.name+'.root', dropLepton=s.dropLepton, bdtTag=args.bdtTag)]
                
for j in jobs:
    print('job',j.fname, j.skim, j.sfx, j.oftree, j.ofhist, j.dropLepton)

# for tag in args.bdtTag.split(','):
#     for fn in all_files:
#         friendName = fn.replace('/root/','/bdt/'+tag+'/')

def runJob(j):
    fname = j.fname
    print ("Going to analyze the input file: ", j.fname)
    ifile = ROOT.TFile.Open(j.fname,'read')
    itree = ifile.Get('Events')
    if len(args.bdtTag):
        itree.AddFriend('Friends', j.ifbdt)
        otree=None
        ofile=None
    else:
        ofile = ROOT.TFile.Open(j.oftree,'recreate')
        if args.fullOutput:
            otree = FullOutput(ifile, itree, ofile)
            print( "making full output", j.oftree)
        else:
            otree = FriendOutput(ifile, itree, ofile)
            print( "making friend output", j.oftree)
    if (itree.GetEntries() > args.maxEvents) and args.maxEvents>0:
        print("Warning! Truncating {:.0f}k entry file ({}) after {:.0f}k entries.".format(itree.GetEntries()/1e3, fname, args.maxEvents/1e3))
    itree = InputTree(itree)

    myAna = myAnalysis()
    if len(args.bdtTag): myAna.fillBDT = True
    if j.dropLepton: myAna.dropLepton = True
    if j.skim: myAna.setSkim(j.sfx)
        
    os.system('mkdir -p histograms/'+args.bdtTag)
    hfile = ROOT.TFile.Open(j.ofhist,'recreate')
    myAna.bookHistos(hfile, getHists([c for c in cuts]) )
    myAna.setCuts(cuts)

    (nall, npass, timeLoop) = eventLoop(inputFile=ifile, outputFile=ofile, inputTree=itree, wrappedOutputTree=otree,
                                        modules=[ myAna ], progress=(100000, sys.stdout), filterOutput=j.skim,
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
