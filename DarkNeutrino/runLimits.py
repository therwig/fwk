import ROOT
from cfg.histograms import getHists, GetHNames
from cfg.cuts import cuts
from cfg.samples import xsecs
from plotUtils import *
from numpy import sqrt
from array import array
hnames = GetHNames()

sig_mZd_mNd = [ (mzd,'10') for mzd in ['0p03','0p1','0p3','1','3'] ]
sig_files = {p: ROOT.TFile("histograms/outS_mZD{}_mND{}.root".format(*p),'read') for p in sig_mZd_mNd}
bkg_file = ROOT.TFile('histograms/outB1M.root','read')

h={}
for cn in cuts:
    for hname in hnames:
        for pt in sig_mZd_mNd:
            h[("mZD{}_mND{}".format(*pt), cn, hname)] = sig_files[pt].Get(cn+'_'+hname)
        h[("b", cn, hname)] = bkg_file.Get(cn+'_'+hname)
# print(h)

# helpers
procTags = ['b'] + ['mZD{}_mND{}'.format(*pt) for pt in sig_mZd_mNd]
procLabs = ['Bkgd'] + ['m_{{ZD}},m_{{ND}}=({},{}) GeV'.format(*pt) for pt in sig_mZd_mNd]
legsty=['f']+['l' for x in sig_mZd_mNd]

### preliminary: dump signal and background plot overlays
runDumps=0
if runDumps:
    pdir='plots/dumps/'
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

### Now produce the S/B plots and so on
lumi = 150 # in fb
refEps=1.0
refAd=1.0
refUm4=1.0e-4

hname='mee_logx1'
for cutname in cuts:
    b = h[('b',cutname,hname)]
    b.Scale(lumi*xsecs['b']*1e3)
    for sig in procTags[1:]:
        s = h[(sig,cutname,hname)]
        s.Scale(lumi*xsecs[sig]*1e3) # /fb * pb
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
gs={}
for cutname in cuts:
    srbTarget=2
    xvals, yvals = [],[]
    for t in procTags[1:]:
        _srb = h[('srb',t,cutname,hname)]
        mZd = float(t.split('_')[0][3:].replace('p','.'))
        # exit(0)
        # mZd = 1 #float(_srb.GetName().split('_'))
        refReach = _srb.GetMaximum()
        maxReach = (sqrt(srbTarget/refReach) * refUm4 if refReach else 1.)
        print (mZd, refUm4, maxReach)
        xvals.append(mZd)
        yvals.append(maxReach)
    # print(len(xvals),xvals, yvals)                                                                                                                          
    g = ROOT.TGraph(len(xvals),array('d',xvals), array('d',yvals))
    g.SetName(cutname+'_'+hname+'_reach')
    # if 'yields_pz5' in g.GetName() and 'lx2' in g.GetName():
    gs[g.GetName()] = g
    
plotGraphs('reach', [gs[x] for x in gs],
           xtitle='m(Z_{d}) [MeV]', ytitle='Um4',
           legcoors=(0.7,0.6,0.88,0.9),
           xlims=None, ymin=0, ymax=None, legcols=1,
           logy=True, logx=True, colz=None, styz=None, dopt='AL*')
