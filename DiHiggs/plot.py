#!/usr/bin/env python3
import ROOT

samples=['GluGluToHHTo4B_node_cHHH'+s for s in ['0','1','2p45','5']]
fs = [ROOT.TFile('data/'+s+'.skim.friend.root') for s in samples]
ts = [f.Get('Friends') for f in fs]

c = ROOT.TCanvas()

for i, t in enumerate(ts):
    if i==0:
        t.Draw('mhh','mhh>0 && mhh<600 && JetIdx[0]>-1')
    else:
        t.Draw('mhh','mhh>0 && mhh<600 && JetIdx[0]>-1','same')
    
c.SaveAs('test.pdf')
