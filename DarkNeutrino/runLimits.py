#!/usr/bin/env python3
import sys, os, argparse
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')
from cfg.histograms import getHists, GetHNames
from cfg.cuts import cuts
from cfg.samples import samples, bkg_names, xsecs, refUm4, refEps, refAd, sig_pairs, sig_tags, sortByND, sortByZD, paper_pairs, paper_tags
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

sig_samples = [s for s in samples if not s.isSM]
bkg_samples = [s for s in samples if s.isSM]
sig_files = {s.name: ROOT.TFile(args.histDir+"/outS_{}.root".format(s.name)) for s in sig_samples}
bkg_files = {s.name: ROOT.TFile(args.histDir+"/bSplit{}.root".format(s.name)) for s in bkg_samples}
sTags = [s.name for s in samples if not s.isSM]
bTags = [s.name for s in samples if s.isSM]

# for inclusive plotting (debugHists)
allTags = bTags+sTags
toStack = list(range(len(bTags)))
sLabs = ['m_{{ZD}},m_{{ND}}=({},{}) GeV'.format(*s.pairs) for s in sig_samples]
allLabs = bTags + sLabs
legSty = ['f']*len(bTags) + ['l']*len(sTags)
fColz = [s.col for s in bkg_samples] + [None]*len(sig_samples)
lColz = [None]*len(bkg_samples) + [s.col for s in sig_samples]
# for paper plotting
pap_samples = [s for s in sig_samples if s.isPaper]
papTags = bTags+[s.name for s in pap_samples]
papLabs = bTags + ['m(Z_{{D}}) = {}, m(N_{{D}}) = {} GeV'.format(*s.pairs) for s in pap_samples]
papSty = ['f']*len(bTags) + ['l']*(len(pap_samples))
fPapColz = [s.col for s in bkg_samples] + [None]*len(pap_samples)
lPapColz = [None]*len(bkg_samples) + [s.col for s in pap_samples]

h={} # a record of all histograms
for cn in cuts:
    for hname in hnames:
        for s in sig_samples: h[(s.name, cn, hname)] = sig_files[s.name].Get(cn+'_'+hname)
        for s in bkg_samples: h[(s.name, cn, hname)] = bkg_files[s.name].Get(cn+'_'+hname)

def plotPaper(name,hs, legPos='R',
              xtitle='', ytitle='', logx=False, logy=False):
# def plot(name, hists, pdir='plots/', labs=[], legtitle='',
#          xtitle='', ytitle='', rescale=None, legstyle='',toptext='',
#          legcoors=(0.7,0.6,0.88,0.9), redrawBkg=False,
#          xlims=None, legcols=1, gridx=False,gridy=False,
#          logx=False, logy=False, ymin=0, ymax=None, colz=None, fcolz=None, dopt='',
#          bsub=False, ratio = False, ratlims=(0.9,1.1)):
    pname = os.path.basename(args.plotDir+'/paper/'+name)
    dname = os.path.dirname(args.plotDir+'/paper/'+name)
    legcoors=[0.6,0.55,0.88,0.9]
    if legPos=='L':
        legcoors[2] = 0.1 + legcoors[2] - legcoors[0]
        legcoors[0] = 0.1
    plot(pname, hs, pdir=dname, legcoors=(0.6,0.55,0.88,0.9),
         toStack=toStack, labs=papLabs, legstyle=papSty,
         fcolz=fPapColz, colz=lPapColz, 
         logx=logx, logy=logy, dopt='hist',
         xtitle=xtitle, ytitle=ytitle)

###
### preliminary: dump signal and background plot shape overlays
pdir=args.plotDir+'/dumps/raw/'
for hname in hnames:
    doLogX = ('logx' in hname)
    for cutname in cuts:
        if args.dumpHists:
            # fix the cut, plot for all processes
            plot(cutname+'_'+hname, [h[(t,cutname,hname)] for t in allTags],
                 toStack=toStack, labs=allLabs, colz=lColz, fcolz=fColz, legstyle=legSty,
                 ytitle='event fraction', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byCut')
        if cutname=='incl' and hname in ['dree','metL','mupt','meeS_logx1']:
            plotPaper('incl/'+hname, [h[(t,cutname,hname)] for t in papTags],
                      ytitle='Event fraction', logx=doLogX,
                      logy=('dree' in hname))
                      
    for t in allTags:
        if args.dumpHists:
            plot(t+'_'+hname, [h[(t,cutname,hname)] for cutname in cuts],
                 labs=[cutname for cutname in cuts], legstyle=legSty,
                 ytitle='event fraction', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byProcess')
###
### Now produce distributions for a common set of signal parameters, run conditions
### Reference constants used for this sample production
for cutname in cuts:
    for hname in hnames:
        for s in samples:
            h[(s.name,cutname,hname)].Scale(args.lumi * s.xs*1e3 * (1 if s.isSM else args.adhocSigRescale))
            
###
### Optionally dump a second set of histograms, now properly normalized
#if args.dumpHists:
pdir=args.plotDir+'/dumps/yields/'
for hname in hnames:
    doLogX = ('logx' in hname)
    for cutname in cuts:
        if args.dumpHists:
            plot(cutname+'_'+hname, [h[(t,cutname,hname)] for t in allTags],
                 toStack=toStack, labs=allLabs, colz=lColz, fcolz=fColz, legstyle=legSty,
                 ytitle='events', dopt='hist', logx=doLogX, logy=1, ymin=0.1,
                 pdir=pdir+'/byCut')
        if cutname in ['lep3','bdtT','cuts'] and hname in ['dree','e2pt','dPhiLepMu','meeS_logx1']:
            plotPaper(cutname+'_yields/'+hname, [h[(t,cutname,hname)] for t in papTags],
                      ytitle='Events', logx=doLogX, legPos=('R' if hname in ['dPhiLepMu'] else 'L'),
                      logy=('dree' in hname))
                
    for t in allTags:
        if args.dumpHists:
            plot(t+'_'+hname, [h[(t,cutname,hname)] for cutname in cuts],
                 labs=[cutname for cutname in cuts], legstyle=legSty,
                 ytitle='events', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byProcess')
if args.dumpHists:
    for cutname in cuts:
        with open(args.plotDir+'/dumps/yields/'+cutname+'.txt','w') as ftxt:
            for t in allTags: ftxt.write( "{} : {:.2f}\n".format(t,h[(t,cutname,'yields')].GetBinContent(1)) )

###
### Now produce the S/B histograms for "limit-setting"
hname='meeS_logx1'
for cutname in cuts:
    # build the total background
    bhists = [h[(t,cutname,hname)] for t in bTags]
    bTotal = bhists[0].Clone('bTotal_'+cutname+'_'+hname); bTotal.Reset()
    for bh in bhists: bTotal.Add(bh)
    h[('bTotal',cutname,hname)] = bTotal
    # calculate S/B
    for sname in sTags:
        s = h[(sname,cutname,hname)]
        sb = s.Clone('sb_'+s.GetName())
        sb.Divide(bTotal)
        srb = s.Clone('srb_'+s.GetName())
        for ibin in range(1,srb.GetNbinsX()+1):
            _s = s.GetBinContent(ibin)
            _b = bTotal.GetBinContent(ibin)
            srb.SetBinContent(ibin, _s/sqrt(_b+(args.flatBkgSyst*_b)**2) if _b else 1e-6)
        # calc here and store
        h[('sb',sname,cutname,hname)] = sb
        h[('srb',sname,cutname,hname)] = srb
        
###
### Plot various limit inputs
pdir=args.plotDir+'/limitInputs/'

### S/B histograms
for cutname in cuts:
    plot('sb_'+cutname+'_'+hname, [h[('sb',t,cutname,hname)] for t in sTags],
         labs=sLabs, 
         ytitle='S/B', dopt='hist', logx=1,
         pdir=pdir)
    plot('srb_'+cutname+'_'+hname, [h[('srb',t,cutname,hname)] for t in sTags],
         labs=sLabs,
         ytitle='S/sqrt(B)', dopt='hist', logx=1,
         pdir=pdir)

# Setup exlcusion graphs for fixed ND and ZD masses
samples_mZD0p03 = [s for s in sig_samples if s.pairs[0]=='0p03'];
samples_mND10   = [s for s in sig_samples if s.pairs[1]=='10'];
gsets={'mZD0p03':{},
       'mND10':{}
       }
    
### event yields per point
for cutname in cuts:
    for scanName, sigSamples in [('mZD0p03',samples_mZD0p03),('mND10',samples_mND10)]:
        xvals, yvals = [], []
        for samp in sigSamples:
            s = h[(samp.name,cutname,hname)]
            mZd, mNd = samp.masses
            xvals.append(mZd if 'mND' in scanName else mNd)
            yvals.append(s.Integral())
        g = ROOT.TGraph(len(xvals),array('d',xvals), array('d',yvals)); sortGraph(g)
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
    for scanName, sigSamples in [('mZD0p03',samples_mZD0p03),('mND10',samples_mND10)]:
        xvals, yvals = [], []
        for samp in sigSamples:
            _srb = h[('srb',samp.name,cutname,hname)]
            mZd, mNd = samp.masses
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
    b = h[('bTotal',cutname,hname)]
    for scanName, sigSamples in [('mZD0p03',samples_mZD0p03),('mND10',samples_mND10)]:
        xvals, yvals = [], []
        for samp in sigSamples:
            _srb = h[('srb',samp.name,cutname,hname)]
            mZd, mNd = samp.masses
            if args.debugFits:
                debugName = "{}/debug/{}_{}_{}_{}".format(pdir,cutname,hname,scanName,samp.name)
                os.system('mkdir -p '+pdir+'/debug')
            else:
                debugName = ''
            if not ('dPhi_meeS_logx1_mND10_mZD0p3_mND10' in debugName): debugName=''
            # make a nominal 'pseudodataset' w/ correct stat errors
            pseudoData = b.Clone("pseudo")
            for i in range(b.GetNbinsX()+2): pseudoData.SetBinError(i, sqrt(pseudoData.GetBinContent(i)))
            sigStrengthExcl = getMuSigInterval(s, pseudoData, flatBkgSyst=args.flatBkgSyst, plotName=debugName)
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
