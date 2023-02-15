import sys, os
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')

from Analysis.eventloop import eventLoop
from Analysis.treeReaderArrayTools import InputTree
from modules.myAnalysis import myAnalysis
from cfg.samples import sig_pairs, sig_tags
from cfg.histograms import getHists
from cfg.cuts import cuts

sig_files = ["data/root/outS_{}.root".format(sig_tags[p]) for p in sig_pairs]
all_files = sig_files + ['data/root/outB1M.root']

for fname in all_files:
    print ("Going to analyze the input file: ", fname)
    ifile = ROOT.TFile.Open(fname,'read')
    itree = ifile.Get('Events')
    itree = InputTree(itree)

    myAna = myAnalysis()
    hname = fname.replace('data/root','histograms')
    hfile = ROOT.TFile.Open(hname,'recreate')
    myAna.bookHistos(hfile, getHists([c for c in cuts]) )
    myAna.setCuts(cuts)
    
    (nall, npass, timeLoop) = eventLoop(inputFile=ifile, outputFile=None, inputTree=itree, wrappedOutputTree=None,
                                        modules=[ myAna ], progress=(100000, sys.stdout), filterOutput=False,
                                        maxEvents=100000, # optionally truncate large background sample
                                        )

    # scale the outputs to the number of entries processed
    sumw = myAna.sumw if myAna.sumw else 1
    for hn in myAna.h.d:
        myAna.h.d[hn].Scale(1./sumw)
    
    
    hfile.Write()
    hfile.Close()
    ifile.Close()

