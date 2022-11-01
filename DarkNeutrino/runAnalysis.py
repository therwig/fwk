import ROOT
from Analysis.eventloop import eventLoop
from Analysis.treeReaderArrayTools import InputTree
import sys

from modules.myAnalysis import myAnalysis
from cfg.histograms import getHists
from cfg.cuts import cuts

sig_mZd_mNd = [ (mzd,'10') for mzd in ['0p03','0p1','0p3','1','3'] ]
sig_files = ["data/root/outS_mZD{}_mND{}.root".format(*p) for p in sig_mZd_mNd]
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

