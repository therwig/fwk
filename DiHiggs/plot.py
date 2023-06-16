#!/usr/bin/env python3
import ROOT
from commonRootTools.plotUtils import plot

samples=['GluGluToHHTo4B_node_cHHH'+s for s in ['0','1','2p45','5']]
fs = {s:ROOT.TFile('data/'+s+'.skim.friend.root') for s in samples}
ts = {s:fs[s].Get('Friends') for s in samples}

c = ROOT.TCanvas()

### simple setup
for i, s in enumerate(samples):
    t = ts[s]
    if i==0:
        t.Draw('mhh','mhh>0 && mhh<600 && JetIdx[0]>-1')
    else:
        t.Draw('mhh','mhh>0 && mhh<600 && JetIdx[0]>-1','same')
    
c.SaveAs('test.pdf')

#store many histograms, post-process, and draw
histoDict = {}
for s in samples:
    h  = ROOT.TH1F(s+'_mhh',';m_{hh}[GeV]',40,0,800) # construct
    ts[s].Draw('mhh>>'+s+'_mhh','JetIdx[0]>-1') # fill
    h.Scale(1./h.Integral()) # normalize
    histoDict[s+'_mhh'] = h # save in a dictionary for later access

hists  = [histoDict[s+'_mhh'] for s in samples]
labels = [s.split('_')[-1] for s in samples]

plot('test2',
     hists,
     labs=labels,
     colz=[ROOT.kBlack,ROOT.kBlue,ROOT.kRed,ROOT.kGreen],
     ytitle='event fraction', dopt='hist'
     )

            # plot(cutname+'_'+hname, [h[(t,cutname,hname)] for t in allTags],
            #      toStack=toStack, labs=allLabs, colz=lColz, fcolz=fColz, legstyle=legSty,
            #      xtitle=xtitles[hname], ytitle='event fraction', dopt='hist', logx=doLogX,
            #      pdir=pdir+'/byCut')
