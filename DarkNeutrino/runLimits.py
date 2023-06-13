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
from limitHelpers import *
from numpy import sqrt, hypot
from array import array
hnames = GetHNames()

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--plotDir", default='plots', help="Directory in which to save plots")
parser.add_argument("--histDir", default='histograms', help="Directory to read the histograms from")
parser.add_argument("--lumi", default=None, type=float, help="Target luminosity [in 1/fb]")
parser.add_argument("--adhocSigRescale", default=1., type=float, help="Rescale signal yields, for illustration")
parser.add_argument("--flatBkgSyst", default=0.01, type=float, help="Systematic uncertainty")
parser.add_argument("--dumpHists", action="store_true", default=False, help="Dump plots of all histograms")
parser.add_argument("--debugFits", action="store_true", default=False, help="Debug the chi2 fits")
parser.add_argument("--hllhc", action="store_true", default=False, help="Run HL-LHC setup. Otherwise Run 2")
args = parser.parse_args()
    
sqrts = 14 if args.hllhc else 13
lumi  = args.lumi if args.lumi else (4000 if args.hllhc else 150)
args.plotDir += ('/hllhc/' if args.hllhc else '/run2/')

sig_samples = [s for s in samples if not s.isSM]
bkg_samples = [s for s in samples if s.isSM]
sig_files = {s.name: ROOT.TFile(args.histDir+"/outS_{}.root".format(s.name)) for s in sig_samples}
bkg_files = {s.name: ROOT.TFile(args.histDir+"/{}{}.root".format(s.pfx,s.name)) for s in bkg_samples}
sTags = [s.name for s in samples if not s.isSM]
bTags = [s.name for s in samples if s.isSM]

# for inclusive plotting (debugHists)
allTags = bTags+sTags
toStack = list(range(len(bTags)))
sLabs = ['m_{{ZD}},m_{{ND}}=({},{}) GeV'.format(*s.pairs) for s in sig_samples]
allLabs = bTags + sLabs
legSty = ['f']*len(bTags) + ['l']*len(sTags)
legSty2= ['f']*len(bTags) + ['l']*len(sTags)
fColz = [s.col for s in bkg_samples] + [None]*len(sig_samples)
lColz = [None]*len(bkg_samples) + [s.col for s in sig_samples]
# for paper plotting
pap_samples = [s for s in sig_samples if s.isPaper]
papTags = bTags+[s.name for s in pap_samples]
papLabs = bTags + ['m(Z_{{D}}) = {}, m(N_{{D}}) = {} GeV'.format(*s.pairs).replace('p','.') for s in pap_samples]
papSty = ['f']*len(bTags) + ['l']*(len(pap_samples))
fPapColz = [s.col for s in bkg_samples] + [None]*len(pap_samples)
lPapColz = [None]*len(bkg_samples) + [s.col for s in pap_samples]

#paper_yield_selections = ['incl','leps','lepsHT','cuts1','cuts3','cuts5','cutsL1','cutsL3','cutsL5']
paper_yield_selections = [c for c in cuts]
paper_hist_selections = ['dree','mupt','e1pt','e2pt','dPhiLepMu','meeS_logx1','metL','dRLepMu','mtMuL','mtL','ptMuL','e1eta','e2eta','mueta','ht','htc']
paper_incl_hist_selections = ['dree','metL','mupt','meeS_logx1','dPhiLepMu']
logvars=['dree','htc','ht']

h={} # a record of all histograms
for cn in cuts:
    for hname in hnames:
        for s in sig_samples:
            h[(s.name, cn, hname)] = sig_files[s.name].Get(cn+'_'+hname)
            removeOverflow( h[(s.name, cn, hname)] )
            if h[(s.name, cn, hname)] == None:
                print("Missing ", s.name, cn, hname," from ",sig_files[s.name].GetPath())
        for s in bkg_samples:
            h[(s.name, cn, hname)] = bkg_files[s.name].Get(cn+'_'+hname)
            removeOverflow( h[(s.name, cn, hname)] )
            if h[(s.name, cn, hname)] == None:
                print("Missing ", s.name, cn, hname," from ",bkg_files[s.name].GetPath())



###
### preliminary: dump signal and background plot shape overlays
pdir=args.plotDir+'/dumps/raw/'
for hname in hnames:
    doLogX = ('logx' in hname)
    for cutname in cuts:
        if args.dumpHists:
            # fix the cut, plot for all processes
            #print(cutname,hname, [ (t, h[(t,cutname,hname)]) for t in allTags] )
            plot(cutname+'_'+hname, [h[(t,cutname,hname)] for t in allTags],
                 toStack=toStack, labs=allLabs, colz=lColz, fcolz=fColz, legstyle=legSty,
                 ytitle='event fraction', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byCut')
        # if cutname in ['incl','lep3'] and hname in paper_incl_hist_selections:
        #     plotPaper(cutname+'/'+hname, [h[(t,cutname,hname)] for t in papTags],
        #               ytitle='Event fraction', logx=doLogX,
        #               logy=('dree' in hname and 'incl' in cutname))
        #     if 'dPhiLepMu' in hname: # plot both log and lin scales
        #         plotPaper(cutname+'/'+hname+'Log', [h[(t,cutname,hname)] for t in papTags],
        #                   ytitle='Event fraction', logx=doLogX,
        #                   logy=True)

    for t in allTags:
        if args.dumpHists:
            plot(t+'_'+hname, [h[(t,cutname,hname)] for cutname in cuts],
                 labs=[cutname for cutname in cuts], #legstyle=legSty,
                 ytitle='event fraction', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byProcess')
###
### Now produce distributions for a common set of signal parameters, run conditions
### Reference constants used for this sample production
for cutname in cuts:
    for hname in hnames:
        for s in samples:
            h[(s.name,cutname,hname)].Scale(lumi * sqrts/13. * s.xs*1e3 * (1 if s.isSM else args.adhocSigRescale))
from cfg.samples import sample
remaps = [
    ( sample('W', 1, isSM=True, col=432-10), ['WZ']),
    ( sample('Z', 1, isSM=True, col=860-6), ['ZZ3L','ZZ4L']),
    ( sample('Top', 1, isSM=True, col=632+2), ['ttZ3L','ttZ4L']),
]
toComb = {}
newSamples=[]
for pair in remaps:
    newSamples.append( pair[0] )
    for proc in pair[1]:
        toComb[proc] = pair[0].name
        
for ic, cutname in enumerate(cuts):
    for ihn, hname in enumerate(hnames):
        for s in samples:
            if s.name in toComb:
                oldKey = (s.name,cutname,hname)
                newKey = (toComb[s.name],cutname,hname)
                if newKey in h:
                    h[newKey].Add( h[oldKey] )
                else:
                    h[newKey] = h[oldKey].Clone()
            else:
                if not (ic or ihn): newSamples.append(s)
                
#ugly way of doing this for now
if True:
    samples = newSamples
    sig_samples = [s for s in samples if not s.isSM]
    bkg_samples = [s for s in samples if s.isSM]
    sTags = [s.name for s in samples if not s.isSM]
    bTags = [s.name for s in samples if s.isSM]
    
    # for inclusive plotting (debugHists)
    allTags = bTags+sTags
    toStack = list(range(len(bTags)))
    sLabs = ['m_{{ZD}},m_{{ND}}=({},{}) GeV'.format(*s.pairs) for s in sig_samples]
    allLabs = bTags + sLabs
    legSty = ['f']*len(bTags) + ['l']*len(sTags)
    legSty2= ['f']*len(bTags) + ['l']*len(sTags)
    fColz = [s.col for s in bkg_samples] + [None]*len(sig_samples)
    lColz = [None]*len(bkg_samples) + [s.col for s in sig_samples]
    # for paper plotting
    pap_samples = [s for s in sig_samples if s.isPaper]
    papTags = bTags+[s.name for s in pap_samples]
    papLabs = bTags + ['m(Z_{{D}}) = {}, m(N_{{D}}) = {} GeV'.format(*s.pairs).replace('p','.') for s in pap_samples]
    papSty = ['f']*len(bTags) + ['l']*(len(pap_samples))
    fPapColz = [s.col for s in bkg_samples] + [None]*len(pap_samples)
    lPapColz = [None]*len(bkg_samples) + [s.col for s in pap_samples]

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
        if cutname in paper_yield_selections and hname in paper_hist_selections:
            for doNorm in [0,1]:
                pname = cutname+'/'+hname if doNorm else cutname+'_yields/'+hname
                plotPaper(pname, [h[(t,cutname,hname)] for t in papTags],
                          ytitle='Events', logx=doLogX, legPos=('R' if hname in ['dPhiLepMu'] else 'L'),
                          logy=0, doNorm=doNorm, pdir=args.plotDir)
                if hname in logvars:
                    plotPaper(pname+'Log', [h[(t,cutname,hname)] for t in papTags],
                              ytitle='Events', logx=doLogX, legPos=('R' if hname in ['dPhiLepMu'] else 'L'),
                              logy=1, doNorm=doNorm, pdir=args.plotDir)
        # # also plot the unit-normalized variants
        # if cutname in ['incl','lep3'] and hname in paper_incl_hist_selections:
        #     plotPaper(cutname+'/'+hname, [h[(t,cutname,hname)] for t in papTags],
        #               ytitle='Event fraction', logx=doLogX,
        #               logy=('dree' in hname and 'incl' in cutname))
        #     if 'dPhiLepMu' in hname: # plot both log and lin scales
        #         plotPaper(cutname+'/'+hname+'Log', [h[(t,cutname,hname)] for t in papTags],
        #                   ytitle='Event fraction', logx=doLogX,
        #                   logy=True)
                
    for t in allTags:
        if args.dumpHists:
            plot(t+'_'+hname, [h[(t,cutname,hname)] for cutname in cuts],
                 labs=[cutname for cutname in cuts], #legstyle=legSty,
                 ytitle='events', dopt='hist', logx=doLogX,
                 pdir=pdir+'/byProcess')
if args.dumpHists:
    for cutname in cuts:
        with open(args.plotDir+'/dumps/yields/'+cutname+'.txt','w') as ftxt:
            for t in allTags: ftxt.write( "{} : {:.2f}\n".format(t,h[(t,cutname,'yields')].GetBinContent(1)) )

MinB = 5 # assume we can't reduce B to < 5

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
            _b = max(bTotal.GetBinContent(ibin), MinB)
            srb.SetBinContent(ibin, _s/sqrt(_b+(args.flatBkgSyst*_b)**2) if _b else 1e-6)
        # calc here and store
        h[('sb',sname,cutname,hname)] = sb
        h[('srb',sname,cutname,hname)] = srb
        sb.Scale(1./args.adhocSigRescale)
        srb.Scale(1./args.adhocSigRescale)

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
samples_mZD0p03 = [s for s in sig_samples if s.pairs[0]=='0p03']
samples_mND10   = [s for s in sig_samples if s.pairs[1]=='10']
samples_ratio3  = [s for s in sig_samples if abs(float(s.masses[1])/s.masses[0]-3.15)<0.2]
# for s in samples_ratio3: print (s.masses)
gsets={'mZD0p03': {},
       'mND10'  : {},
       'mNDratio3' : {},
       }
    
### event yields per point
for cutname in cuts:
    for scanName, sigSamples in [('mZD0p03',samples_mZD0p03),('mND10',samples_mND10),('mNDratio3',samples_ratio3)]:
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
gsets['mNDratio3'] = {}
for cutname in cuts:
    srbTarget=2 # "two sigma exclusion"
    for scanName, sigSamples in [('mZD0p03',samples_mZD0p03),('mND10',samples_mND10),('mNDratio3',samples_ratio3)]:
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

eps2Min, eps2Max = 1e-9, 1e-3
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

uncerts=[
    uncert('lepEff',   forS=True,  forB=True, sf=3*0.05),
    uncert('fakeBkg',  forS=False, forB=True, sf=0.333), # scales 1.5 down to 1.0
    uncert('massRes',  forS=True,  forB=True, isSF=False, upName='meeSup_logx2', dnName='meeSdn_logx2'),
]
# also include a common Bkg scale factor to be applied, related to the uncs
bkg_sf = 1.5 # for fake contrib

# Optimal window with scan over fine mass plot
gsets['mZD0p03'] = {}
gsets['mND10'] = {}
gsets['mNDratio3'] = {}
hnameNom='meeS_logx2'
OptimalSigs={}
for cutname in cuts:
    ranNominal=False
    for unc in uncerts:
        print('Running limits for:', cutname, unc.name)
        for uncVar in ['','up','dn']:
            # don't need to re-run the nominal scenario for each syst
            if uncVar=='' and ranNominal: continue
            ranNominal=True
            uncSfx = '_{}_{}'.format(unc.name,uncVar) if len(uncVar) else ''
            hname = hnameNom
            if (not unc.isSF) and unc.forB:
                if uncVar == 'up': hname = unc.upName
                elif uncVar == 'dn': hname = unc.dnName
            # build background hist
            bhists = [h[(t,cutname,hname)] for t in bTags]
            bTotal = bhists[0].Clone('bTotal_'+cutname+'_'+hname); bTotal.Reset()
            for bh in bhists: bTotal.Add(bh)
            h[('bTotal',cutname,hname)] = bTotal
            bTotal.Scale(bkg_sf)
            if unc.isSF and unc.forB:
                if uncVar=='up': bTotal.Scale(1+unc.sf)
                elif uncVar=='dn': bTotal.Scale(1-unc.sf)
            # calculate significance
            for samp in sig_samples:
                hname = hnameNom
                # if len(uncVar) and cutname=='incl' and unc.name=='massRes':
                #     print( ' A-->', hname, unc.isSF, unc.forS, (not unc.isSF) and unc.forS)
                if (not unc.isSF) and unc.forS:
                    if uncVar == 'up': hname = unc.upName
                    elif uncVar == 'dn': hname = unc.dnName
                s = h[(samp.name,cutname,hname)].Clone()
                if unc.isSF and unc.forS:
                    if uncVar=='up': s.Scale(1+unc.sf)
                    elif uncVar=='dn': s.Scale(1-unc.sf)
                # if len(uncVar) and cutname=='incl' and unc.name=='massRes':
                #     print( ' B-->', hname, s.Integral(), bTotal.Integral())
                NBINS = s.GetNbinsX()
                best, bestRange = 0, (0,0)
                for binWindow in range(2,50):
                    for loBin in range(1,NBINS-binWindow):
                        _s = s.Integral(loBin,loBin+binWindow) / args.adhocSigRescale # must undo for sig calc
                        _b = max(bTotal.Integral(loBin,loBin+binWindow), MinB)
                        sig = _s/sqrt(_b+(args.flatBkgSyst*_b)**2) if _b else 1e-6
                        if sig > best:
                            best = sig
                            bestRange = (loBin,loBin+binWindow)
                OptimalSigs[(samp.name,cutname,hname,uncSfx,'mc')] = best
                wid = s.GetBinLowEdge(bestRange[1]+1)-s.GetBinLowEdge(bestRange[0])
                ####
                # also calculate an alternate significance, just based on the local background desity and signal % resolution
                # muon resolution is always better than electron, so we can use the density interval from above
                #   calculate significance from a +/-2sigma window size. yields are 95% of total.
                resolution = 0.02
                if 'meeSup_logx2' == hname: resolution = 0.01
                if 'meeSdn_logx2' == hname: resolution = 0.03
                nB = max(bTotal.Integral(bestRange[0],bestRange[1]) * 4*resolution*samp.masses[0]/wid if wid else 0, MinB)
                OptimalSigs[(samp.name,cutname,hname,uncSfx,'toy')] = 0.95 * s.Integral()/args.adhocSigRescale / sqrt(nB)
                # print( bestRange[0],bestRange[1],  )
                
                #print( 100 * wid / samp.masses[0] )
                # print("{} {} {} {} {:.2f} {:.2f} {:.1f}".format(cutname, samp.name, bestRange[1], bestRange[0],
                #                                              best, wid, 100 * wid / samp.masses[0] ))
                
                ####
                # also calculate an alternate significance, just based on the local background desity and signal % resolution
                # centerBin = bTotal.FindBin(samp.masses[0])
                # loBin = centerBin; hiBin = centerBin
                # while (bTotal.GetBinLowEdge(hiBin+1) - bTotal.GetBinLowEdge(loBin)) < samp.masses[0] * 0.15:
                #     loBin -= 1; hiBin += 1
                # bDensity = bTotal.Integral(loBin,hiBin) / ( bTotal.GetBinLowEdge(hiBin+1) - bTotal.GetBinLowEdge(loBin) )
                # # calculate significance from a +/-2sigma window size. yields are 95% of total.
                # resolution = 0.02
                # if 'meeSup_logx2' == hname: resolution = 0.01
                # if 'meeSdn_logx2' == hname: resolution = 0.03
                # windowSize = samp.masses[0] * 4*resolution
                # nB = max(windowSize*bDensity,MinB)
                # nS = 0.95 * s.Integral()
                # OptimalSigs[(samp.name,cutname,hname,uncSfx,'toy')] = nS / sqrt(nB)
                #print("  {} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}".format(loBin,hiBin, bTotal.Integral(loBin,hiBin), bDensity, windowSize,
                                                                                 # nS,nB,nS / sqrt(nB)))
                #print(samp.masses[0],  OptimalSigs[(samp.name,cutname,hname,uncSfx,'toy')] / OptimalSigs[(samp.name,cutname,hname,uncSfx,'mc')] if OptimalSigs[(samp.name,cutname,hname,uncSfx,'mc')] else 0)
                    
                
            srbTarget=2 # "two sigma exclusion"
            for scanName, sigSamples in [('mZD0p03',samples_mZD0p03),('mND10',samples_mND10),('mNDratio3',samples_ratio3)]:
                for strategy in ['mc','toy']:
                    xvals, yvals = [], []
                    for samp in sigSamples:
                        mZd, mNd = samp.masses
                        refReach = OptimalSigs[(samp.name,cutname,hname,uncSfx,strategy)]
                        maxReach = (srbTarget/refReach * refUm4*refUm4 if refReach else 1.)
                        xvals.append(mZd if 'mND' in scanName else mNd)
                        yvals.append(maxReach)
                    g = ROOT.TGraph(len(xvals),array('d',xvals), array('d',yvals))
                    sortGraph(g)
                    g.SetName(cutname+'_'+hname+'_'+strategy+'_reach_'+('zd' if 'mND' in scanName else 'nd')+uncSfx)
                    gsets[scanName][g.GetName()] = g
                # print('adding gset:',scanName,g.GetName())
hname = hnameNom
eps2Min, eps2Max = 1e-9, 1e-3
pdir=args.plotDir+'/limits'
for strat in ['mc','toy']:
    pdir=args.plotDir+'/limits'
    plotGraphs('sig_'+strat+'_reach_zd', [gsets['mND10'][x] for x in gsets['mND10'] if strat in x and not (x.endswith('_up') or x.endswith('_dn'))],
               xtitle='m(Z_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
               legcoors=(0.7,0.6,0.88,0.9),
               xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
               logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
    plotGraphs('sig_'+strat+'_reach_nd', [gsets['mZD0p03'][x] for x in gsets['mZD0p03'] if strat in x and not (x.endswith('_up') or x.endswith('_dn'))],
               xtitle='m(N_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
               legcoors=(0.7,0.6,0.88,0.9),
               xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
               logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
    for cutname in cuts:
        pdir=args.plotDir+'/limits/uncertsByCut/'
        plotGraphs(cutname+'_sig_'+strat+'_reach_zd', [gsets['mND10'][x] for x in gsets['mND10'] if strat in x and x.startswith(cutname+'_')],
                   xtitle='m(Z_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
                   legcoors=(0.7,0.6,0.88,0.9),
                   xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
                   logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
        plotGraphs(cutname+'_sig_'+strat+'_reach_nd', [gsets['mZD0p03'][x] for x in gsets['mZD0p03'] if strat in x and x.startswith(cutname+'_')],
                   xtitle='m(N_{d}) [MeV]', ytitle='|U_{#mu 4}|^{2}',
                   legcoors=(0.7,0.6,0.88,0.9),
                   xlims=None, ymin=eps2Min, ymax=eps2Max, legcols=1,
                   logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
    

pdir=args.plotDir+'/limits'

c = ROOT.TCanvas()
c.SetLogy(); c.SetLogx()
brEl = text2graph('external_lines/br.txt', delimiter=',');
brMu = text2graph('external_lines/br.txt', delimiter=',', cols=[0,2]); brMu.SetLineStyle(2)
brEl.SetTitle(';m(Z_{D}) [GeV];BR(Z_{D} #rightarrow ee/#mu#mu)')
brEl.Draw('AL')
brMu.Draw('L same')
c.SaveAs('br.pdf')

# first do the mZD0p03 scan, with 100% BR to electrons
# plotting all cuts
#for strat in ['mc','toy']:
strat = 'mc'
eStra='mc'
mStra='toy'
gs = [gsets['mZD0p03']['{}_{}_{}_reach_nd'.format(cut, hnameNom,eStra)] for cut in ['cuts1','cuts5']]
plotSensitivity('scan_mnd_mz30MeV_noUnc', gs, labs=['1 GeV electrons', '5 GeV electrons'], xIsMND=True, rangex=(0.03,10), pdir=args.plotDir)
gs = []
for cut in ['cuts1','cuts5']:
    gUps = [ gsets['mZD0p03'][gn] for gn in gsets['mZD0p03'] if gn.endswith('_up') and '{}_{}_{}_reach_nd'.format(cut, hnameNom, eStra) in gn ]
    gDns = [ gsets['mZD0p03'][gn] for gn in gsets['mZD0p03'] if gn.endswith('_up') and '{}_{}_{}_reach_nd'.format(cut, hnameNom, eStra) in gn ]
    gs.append( makeUncFromMany( gUps+gDns ) )
    gs[-1].SetName('{}_{}_reach_nd'.format(cut, hnameNom))
    # gUp = gsets['mZD0p03']['{}_{}_reach_nd_up'.format(cut, hnameNom)]
    # gDn = gsets['mZD0p03']['{}_{}_reach_nd_dn'.format(cut, hnameNom)]
    # gs.append( makeUnc(gUp,gDn) )
plotSensitivity('scan_mnd_mz30MeV', gs, labs=['1 GeV electrons', '5 GeV electrons'], xIsMND=True,rangex=(0.03,10), pdir=args.plotDir)

# scan ZD with mND = 3 * mZ, using correct BRs to e/mu
combinations = {
    'e5m3' : ('cuts5','cuts3'),
    'e1m3' : ('cuts1','cuts3'),
}
for combName in combinations:
    cutEl, cutMu = combinations[combName]
    sfxs = ['','_up','_dn']
    _sets = gsets['mNDratio3']
    gEl, gElUp, gElDn = splitErrGraph(makeUncFromMany([_sets[gn] for gn in _sets if gn.endswith('_up') and '{}_{}_{}_reach_zd'.format(cutEl, hnameNom, eStra) in gn]))
    gMu, gMuUp, gMuDn = splitErrGraph(makeUncFromMany([_sets[gn] for gn in _sets if gn.endswith('_up') and '{}_{}_{}_reach_zd'.format(cutMu, hnameNom, mStra) in gn]))
    # gEl, gElUp, gElDn = [gsets['mNDratio3']['{}_{}_reach_zd'.format(cutEl, hnameNom)+sfx] for sfx in sfxs]
    # gMu, gMuUp, gMuDn = [gsets['mNDratio3']['{}_{}_reach_zd'.format(cutMu, hnameNom)+sfx] for sfx in sfxs]
    gEl, gElUp, gElDn = ApplyBR(gEl, isEl=1), ApplyBR(gElUp, isEl=1), ApplyBR(gElDn, isEl=1)
    gElUnc = makeUnc(gElUp,gElDn)
    gMu, gMuUp, gMuDn = ApplyBR(gMu, isEl=0), ApplyBR(gMuUp, isEl=0), ApplyBR(gMuDn, isEl=0)
    gMuUnc = makeUnc(gMuUp,gMuDn)
    gComb, gCombUp, gCombDn = CombSig(gEl,gMu), CombSig(gElUp,gMuUp), CombSig(gElDn,gMuDn)
    gCombUnc = makeUnc(gCombUp,gCombDn)
    gEl.SetName(combName+'_elNoUnc')
    gMu.SetName(combName+'_muNoUnc')
    gComb.SetName(combName+'_combNoUnc')
    gElUnc.SetName(combName+'_el')
    gMuUnc.SetName(combName+'_mu')
    gCombUnc.SetName(combName+'_comb')
    plotSensitivity('scan_mzd_'+combName+'_mz30MeV_noUnc', [gEl, gMu, gComb], xIsMND=False,
                    labs=['Electron','Muon','Combined'],rangex=(0.03,3), pdir=args.plotDir)
    plotSensitivity('scan_mzd_'+combName+'_mz30MeV', [gElUnc, gMuUnc, gCombUnc], xIsMND=False,
                    labs=['Electron','Muon','Combined'],rangex=(0.03,3), pdir=args.plotDir)

