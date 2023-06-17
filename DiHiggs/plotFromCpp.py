#!/usr/bin/env python3
import ROOT
from commonRootTools.plotUtils import plot

samples=['GluGluToHHTo4B_node_cHHH'+s for s in ['0','1','2p45','5']]
fs = {s:ROOT.TFile('data/'+s+'.skim.hist.root') for s in samples}

c = ROOT.TCanvas()

#store many histograms, post-process, and draw
histoDict = {}
for s in samples:
    h = fs[s].Get('hMHH')
    h.Scale(1./h.Integral()) # normalize
    histoDict[s+'_mhh'] = h # save in a dictionary for later access

hists  = [histoDict[s+'_mhh'] for s in samples]
labels = [s.split('_')[-1] for s in samples]

plot('testFromCpp',
     hists,
     labs=labels,
     colz=[ROOT.kBlack,ROOT.kBlue,ROOT.kRed,ROOT.kGreen],
     ytitle='event fraction', dopt='hist'
     )
