import sys, os
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')
from cfg.histograms import getHists, GetHNames
from cfg.cuts import cuts
from cfg.samples import xsecs, refUm4, refEps, refAd, sig_pairs, sig_tags
from plotUtils import *
from numpy import sqrt
from array import array
hnames = GetHNames()

sig_files = {p: ROOT.TFile("histograms/outS_{}.root".format(sig_tags[p])) for p in sig_pairs}
bkg_file = ROOT.TFile('histograms/outB1M.root','read')

h={}
for cn in cuts:
    for hname in hnames:
        for pt in sig_pairs:
            h[("mZD{}_mND{}".format(*pt), cn, hname)] = sig_files[pt].Get(cn+'_'+hname)
            # print(("mZD{}_mND{}".format(*pt), cn, hname), h[("mZD{}_mND{}".format(*pt), cn, hname)])
        h[("b", cn, hname)] = bkg_file.Get(cn+'_'+hname)
        # print(("b", cn, hname), h[("b", cn, hname)])

# plotting helpers
procTags = ['b'] + [sig_tags[p] for p in sig_pairs] #['mZD{}_mND{}'.format(*pt) for pt in sig_pairs]
procLabs = ['Bkgd'] + ['m_{{ZD}},m_{{ND}}=({},{}) GeV'.format(*pt) for pt in sig_pairs]
legsty=['f']+['l' for x in sig_pairs]


### preliminary: dump signal and background plot shape overlays
runDumps=0
if runDumps:
    pdir='plots/dumps/raw/'
    for hname in hnames:
        doLogX = ('logx' in hname)
        for cutname in cuts:
            # fix the cut, plot for all processes
            # print( [h[(t,cutname,hname)] for t in procTags] )
            plot(cutname+'_'+hname, [h[(t,cutname,hname)] for t in procTags],
                 labs=procLabs, fcolz=[18], legstyle=legsty,
                 ytitle='event fraction', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byCut')
        for t in procTags:
            plot(t+'_'+hname, [h[(t,cutname,hname)] for cutname in cuts],
                 labs=[cutname for cutname in cuts], fcolz=[18], legstyle=legsty,
                 ytitle='event fraction', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byProcess') 

### Now produce distributions for a common set of signal parameters, run conditions
### Reference constants used for this sample production
lumi = 150 # in 1/fb
adhocSigRescale=1 #e-6 to rescale parameters, for example
for cutname in cuts:
    for hname in hnames:
        b = h[('b',cutname,hname)]
        b.Scale(lumi*xsecs['b']*1e3) # 1e3 b/c xs is in pb
        for sig in procTags[1:]:
            s = h[(sig,cutname,hname)]
            s.Scale(lumi*xsecs[sig]*1e3*adhocSigRescale) # 1e3 b/c xs is in pb
### Plotting
if runDumps:
    pdir='plots/dumps/yields/'
    for hname in hnames:
        doLogX = ('logx' in hname)
        for cutname in cuts:
            plot(cutname+'_'+hname, [h[(t,cutname,hname)] for t in procTags],
                 labs=procLabs, fcolz=[18], legstyle=legsty,
                 ytitle='events', dopt='hist', logx=doLogX, logy=1, ymin=0.1,
                 pdir=pdir+'/byCut')
        for t in procTags:
            plot(t+'_'+hname, [h[(t,cutname,hname)] for cutname in cuts],
                 labs=[cutname for cutname in cuts], fcolz=[18], legstyle=legsty,
                 ytitle='events', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byProcess')


### Now produce the S/B plots and so on
hname='meeS_logx1'
for cutname in cuts:
    b = h[('b',cutname,hname)]
    for sig in procTags[1:]:
        s = h[(sig,cutname,hname)]
        sb = s.Clone('sb_'+s.GetName())
        sb.Divide(b)
        srb = s.Clone('srb_'+s.GetName())
        for ibin in range(1,srb.GetNbinsX()+1):
            _s = s.GetBinContent(ibin)
            _b = b.GetBinContent(ibin)
            srb.SetBinContent(ibin, _s/sqrt(_b if _b else 1.))
        # calc here and store
        h[('sb',sig,cutname,hname)] = sb
        h[('srb',sig,cutname,hname)] = srb
        
pdir='plots/limits/'
for cutname in cuts:
    plot(cutname+'_sb_'+hname, [h[('sb',t,cutname,hname)] for t in procTags[1:]],
         labs=procLabs[1:], 
         ytitle='S/B', dopt='hist', logx=1,
         pdir=pdir)
    plot(cutname+'_srb_'+hname, [h[('srb',t,cutname,hname)] for t in procTags[1:]],
         labs=procLabs[1:], 
         ytitle='S/sqrt(B)', dopt='hist', logx=1,
         pdir=pdir)

# find limits by rescaling
procTags_mZD0p03 = [sig_tags[p] for p in sig_pairs if p[0]=='0p03']; #procTags_mZD0p03.sort()
procTags_mND10 = [sig_tags[p] for p in sig_pairs if p[1]=='10']; #procTags_mND10.sort()
gsets={'mZD0p03':{},
       'mND10':{}
       }
gs1={}
gs2={}
for cutname in cuts:
    srbTarget=2
    for scanName, sigTags in [('mZD0p03',procTags_mZD0p03),('mND10',procTags_mND10)]:
        xvals, yvals = [],[]
        for t in sigTags:
            _srb = h[('srb',t,cutname,hname)]
            mZd = float(t.split('_')[0][3:].replace('p','.'))
            mNd = float(t.split('_')[1][3:].replace('p','.'))
            refReach = _srb.GetMaximum()
            maxReach = (srbTarget/refReach * refUm4*refUm4 if refReach else 1.)
            # print (mZd, refUm4, refReach, )
            xvals.append(mZd if 'mND' in scanName else mNd)
            yvals.append(maxReach)
        g = ROOT.TGraph(len(xvals),array('d',xvals), array('d',yvals))
        g.SetName(cutname+'_'+hname+'_reach_'+('zd' if 'mND' in scanName else 'nd'))
        # if 'yields_pz5' in g.GetName() and 'lx2' in g.GetName():
        gsets[scanName][g.GetName()] = g

    # for t in procTags[1:]:
    #     _srb = h[('srb',t,cutname,hname)]
    #     mZd = float(t.split('_')[0][3:].replace('p','.'))
    #     mNd = float(t.split('_')[1][3:].replace('p','.'))
    #     # exit(0)
    #     # mZd = 1 #float(_srb.GetName().split('_'))
    #     refReach = _srb.GetMaximum()
    #     maxReach = (srbTarget/refReach * refUm4*refUm4 if refReach else 1.)
    #     # print (mZd, refUm4, refReach, )
    #     xvals.append(mZd)
    #     xvals2.append(mNd)
    #     yvals.append(maxReach)
  
    # g = ROOT.TGraph(len(xvals),array('d',xvals), array('d',yvals))
    # g.SetName(cutname+'_'+hname+'_reach_zd')
    # # if 'yields_pz5' in g.GetName() and 'lx2' in g.GetName():
    # gs1[g.GetName()] = g
    # g = ROOT.TGraph(len(xvals),array('d',xvals2), array('d',yvals))
    # g.SetName(cutname+'_'+hname+'_reach_nd')
    # # if 'yields_pz5' in g.GetName() and 'lx2' in g.GetName():
    # gs2[g.GetName()] = g
eps2Min, eps2Max = 1e-7, 1e-4
    
plotGraphs('reach_zd', [gsets['mND10'][x] for x in gsets['mND10']],
           xtitle='m(Z_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*')
plotGraphs('reach_nd', [gsets['mZD0p03'][x] for x in gsets['mZD0p03']],
           xtitle='m(N_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*')

### Produce the chi2 limits directly from the yield plots
from fitSignal import getMuSigInterval
gsets['mZD0p03_chi2'] = {}
gsets['mND10_chi2'] = {}
hname='meeS_logx1'
print( procTags_mZD0p03) 
print( procTags_mND10) 
# for cutname in cuts:
#     b = h[('b',cutname,hname)]
#     for sig in procTags[1:]:
#         s = h[(sig,cutname,hname)]
#         refChi2 = getMuSigInterval(s, b)
#         print( cutname, sig, refChi2)
for cutname in cuts:
    nSigmaTarget=2 #TODO pass to chi2 interval fn (make configurable)
    b = h[('b',cutname,hname)]
    for scanName, sigTags in [('mZD0p03',procTags_mZD0p03),('mND10',procTags_mND10)]:
        xvals, yvals = [],[]
        for t in sigTags:
            s = h[(sig,cutname,hname)]
            sigStrengthExcl = getMuSigInterval(s, b)
            mZd = float(t.split('_')[0][3:].replace('p','.'))
            mNd = float(t.split('_')[1][3:].replace('p','.'))
            # print( cutname, scanName, t, sigStrengthExcl)
            # _srb = h[('srb',t,cutname,hname)]
            # mZd = float(t.split('_')[0][3:].replace('p','.'))
            # mNd = float(t.split('_')[1][3:].replace('p','.'))
            # refReach = _srb.GetMaximum()
            maxReach = (sigStrengthExcl * refUm4*refUm4)
            # print (mZd, refUm4, refReach, )
            print (mZd if 'mND' in scanName else mNd, maxReach, mZd, mNd)
            xvals.append(mZd if 'mND' in scanName else mNd)
            yvals.append(maxReach)
        g = ROOT.TGraph(len(xvals),array('d',xvals), array('d',yvals))
        g.SetName(cutname+'_'+hname+'_reach_'+('zd' if 'mND' in scanName else 'nd'))
        # if 'yields_pz5' in g.GetName() and 'lx2' in g.GetName():
        gsets[scanName][g.GetName()] = g
plotGraphs('reach_chi2_zd', [gsets['mND10'][x] for x in gsets['mND10']],
           xtitle='m(Z_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*')
plotGraphs('reach_chi2_nd', [gsets['mZD0p03'][x] for x in gsets['mZD0p03']],
           xtitle='m(N_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*')

