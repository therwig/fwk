#!/usr/bin/env python3
import sys, os, argparse
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')
from cfg.histograms import getHists, GetHNames
from cfg.cuts import cuts
from cfg.samples import xsecs, refUm4, refEps, refAd, sig_pairs, sig_tags, sortByND, sortByZD
from plotUtils import *
from numpy import sqrt
from array import array
hnames = GetHNames()

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--plotDir", default='plots', help="Directory in which to save plots")
parser.add_argument("--histDir", default='histograms', help="Directory to read the histograms from")
parser.add_argument("--lumi", default=150., type=float, help="Target luminosity [in 1/fb]")
parser.add_argument("--adhocSigRescale", default=1., type=float, help="Rescale signal yields, for illustration")
parser.add_argument("--flatBkgSyst", default=0.01, type=float, help="Systematic uncertainty")
parser.add_argument("--dumpHists", action="store_true", default=False, help="Dump plots of all histograms")
parser.add_argument("--debugFits", action="store_true", default=False, help="Debug the chi2 fits")
args = parser.parse_args()

sig_files = {p: ROOT.TFile(args.histDir+"/outS_{}.root".format(sig_tags[p])) for p in sig_pairs}
# bkg_file = ROOT.TFile('histograms/outB1M.root','read')
bkg_file = ROOT.TFile(args.histDir+'/bSplit.root','read')

h={}
for cn in cuts:
    for hname in hnames:
        for pt in sig_pairs:
            h[("mZD{}_mND{}".format(*pt), cn, hname)] = sig_files[pt].Get(cn+'_'+hname)
        h[("b", cn, hname)] = bkg_file.Get(cn+'_'+hname)

# plotting helpers
procTags = ['b'] + [sig_tags[p] for p in sig_pairs]
procLabs = ['Bkgd'] + ['m_{{ZD}},m_{{ND}}=({},{}) GeV'.format(*pt) for pt in sig_pairs]
legsty=['f']+['l' for x in sig_pairs]

###
### preliminary: dump signal and background plot shape overlays
if args.dumpHists:
    pdir=args.plotDir+'/dumps/raw/'
    for hname in hnames:
        doLogX = ('logx' in hname)
        for cutname in cuts:
            # fix the cut, plot for all processes
            plot(cutname+'_'+hname, [h[(t,cutname,hname)] for t in procTags],
                 labs=procLabs, fcolz=[18], legstyle=legsty,
                 ytitle='event fraction', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byCut')
        for t in procTags:
            plot(t+'_'+hname, [h[(t,cutname,hname)] for cutname in cuts],
                 labs=[cutname for cutname in cuts], fcolz=[18], legstyle=legsty,
                 ytitle='event fraction', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byProcess') 

###
### Now produce distributions for a common set of signal parameters, run conditions
### Reference constants used for this sample production
for cutname in cuts:
    for hname in hnames:
        b = h[('b',cutname,hname)]
        b.Scale(args.lumi*xsecs['b']*1e3) # 1e3 b/c xs is in pb
        for sig in procTags[1:]:
            s = h[(sig,cutname,hname)]
            s.Scale(args.lumi*xsecs[sig]*1e3*args.adhocSigRescale) # 1e3 b/c xs is in pb

###
### Optionally dump a second set of histograms, now properly normalized
if args.dumpHists:
    pdir=args.plotDir+'/dumps/yields/'
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
    for cutname in cuts:
        with open(args.plotDir+'/dumps/yields/'+cutname+'.txt','w') as ftxt:
            for t in procTags: ftxt.write( "{} : {:.2f}\n".format(t,h[(t,cutname,'yields')].GetBinContent(1)) )

###
### Now produce the S/B histograms for "limit-setting"
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
            srb.SetBinContent(ibin, _s/sqrt(_b+(args.flatBkgSyst*_b)**2) if _b else 1e-6)
        # calc here and store
        h[('sb',sig,cutname,hname)] = sb
        h[('srb',sig,cutname,hname)] = srb
        
###
### Plot various limit inputs
pdir=args.plotDir+'/limitInputs/'

# Setup exlcusion graphs for fixed ND and ZD masses
procTags_mZD0p03 = [sig_tags[p] for p in sig_pairs if p[0]=='0p03']; #procTags_mZD0p03.sort()
procTags_mND10 = [sig_tags[p] for p in sig_pairs if p[1]=='10']; #procTags_mND10.sort()
gsets={'mZD0p03':{},
       'mND10':{}
       }
gs1={}
gs2={}


### S/B histograms
for cutname in cuts:
    plot('sb_'+cutname+'_'+hname, [h[('sb',t,cutname,hname)] for t in procTags[1:]],
         labs=procLabs[1:], 
         ytitle='S/B', dopt='hist', logx=1,
         pdir=pdir)
    plot('srb_'+cutname+'_'+hname, [h[('srb',t,cutname,hname)] for t in procTags[1:]],
         labs=procLabs[1:], 
         ytitle='S/sqrt(B)', dopt='hist', logx=1,
         pdir=pdir)
    
### event yields per point
for cutname in cuts:
    for scanName, sigTags in [('mZD0p03',procTags_mZD0p03),('mND10',procTags_mND10)]:
        xvals, yvals = [],[]
        for t in sigTags:
            s = h[(t,cutname,hname)]
            mZd = float(t.split('_')[0][3:].replace('p','.'))
            mNd = float(t.split('_')[1][3:].replace('p','.'))
            xvals.append(mZd if 'mND' in scanName else mNd)
            yvals.append(s.Integral())
        g = ROOT.TGraph(len(xvals),array('d',xvals), array('d',yvals))
        sortGraph(g)
        g.SetName(cutname+'_'+hname+'_evtYields_'+('zd' if 'mND' in scanName else 'nd'))
        gsets[scanName][g.GetName()] = g
plotGraphs('yields_zd', [gsets['mND10'][x] for x in gsets['mND10']],
           xtitle='m(Z_{d}) [MeV]', ytitle='Events',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
plotGraphs('yields_nd', [gsets['mZD0p03'][x] for x in gsets['mZD0p03']],
           xtitle='m(N_{d}) [MeV]', ytitle='Events',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
    

# Find limits, rescaling signal to achieve S/sqrt(B)=2
gsets['mZD0p03'] = {}
gsets['mND10'] = {}
for cutname in cuts:
    srbTarget=2 # "two sigma exclusion"
    for scanName, sigTags in [('mZD0p03',procTags_mZD0p03),('mND10',procTags_mND10)]:
        xvals, yvals = [],[]
        for t in sigTags:
            _srb = h[('srb',t,cutname,hname)]
            mZd = float(t.split('_')[0][3:].replace('p','.'))
            mNd = float(t.split('_')[1][3:].replace('p','.'))
            refReach = _srb.GetMaximum()
            maxReach = (srbTarget/refReach * refUm4*refUm4 if refReach else 1.)
            xvals.append(mZd if 'mND' in scanName else mNd)
            yvals.append(maxReach)
        g = ROOT.TGraph(len(xvals),array('d',xvals), array('d',yvals))
        sortGraph(g)
        g.SetName(cutname+'_'+hname+'_reach_'+('zd' if 'mND' in scanName else 'nd'))
        gsets[scanName][g.GetName()] = g

eps2Min, eps2Max = 1e-8, 1e-3
pdir=args.plotDir+'/limits'
plotGraphs('srb_reach_zd', [gsets['mND10'][x] for x in gsets['mND10']],
           xtitle='m(Z_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
plotGraphs('srb_reach_nd', [gsets['mZD0p03'][x] for x in gsets['mZD0p03']],
           xtitle='m(N_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)

### Produce the chi2 limits directly from the yield plots
from fitSignal import getMuSigInterval
gsets['mZD0p03_chi2'] = {}
gsets['mND10_chi2'] = {}
hname='meeS_logx1' # histogram for signal extraction

for cutname in cuts:
    nSigmaTarget=2 #TODO pass to chi2 interval fn (make configurable)
    b = h[('b',cutname,hname)]
    for scanName, sigTags in [('mZD0p03',procTags_mZD0p03),('mND10',procTags_mND10)]:
        xvals, yvals = [],[]
        for t in sigTags:
            s = h[(t,cutname,hname)]
            if args.debugFits:
                debugName = "{}/debug/{}_{}_{}_{}".format(pdir,cutname,hname,scanName,t)
                os.system('mkdir -p '+pdir+'/debug')
            else:
                debugName = ''
            if not ('dPhi_meeS_logx1_mND10_mZD0p3_mND10' in debugName): debugName=''
            # make a nominal 'pseudodataset' w/ correct stat errors
            pseudoData = b.Clone("pseudo")
            for i in range(b.GetNbinsX()+2): pseudoData.SetBinError(i, sqrt(pseudoData.GetBinContent(i)))
            sigStrengthExcl = getMuSigInterval(s, pseudoData, flatBkgSyst=args.flatBkgSyst, plotName=debugName)
            mZd = float(t.split('_')[0][3:].replace('p','.'))
            mNd = float(t.split('_')[1][3:].replace('p','.'))
            maxReach = (sigStrengthExcl * refUm4*refUm4)
            xvals.append(mZd if 'mND' in scanName else mNd)
            yvals.append(maxReach)
        g = ROOT.TGraph(len(xvals),array('d',xvals), array('d',yvals))
        sortGraph(g)
        g.SetName(cutname+'_'+hname+'_reach_'+('zd' if 'mND' in scanName else 'nd'))
        gsets[scanName][g.GetName()] = g

plotGraphs('chi2_reach_zd', [gsets['mND10'][x] for x in gsets['mND10']],
           xtitle='m(Z_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
plotGraphs('chi2_reach_nd', [gsets['mZD0p03'][x] for x in gsets['mZD0p03']],
           xtitle='m(N_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
