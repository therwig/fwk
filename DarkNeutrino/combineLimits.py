import sys, os
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')
# if len(sys.argv) < 4:
#     exit('usage: python3 combineLimits.py newDir plotDir1 plotDir2')
    #python3 combineLimits.py combo230523 plots230523_4iab plots230523_150ifb
tag='230526'
pdir = 'plots/{}/comb'.format(tag)
indirs = [s.format(tag) for s in ['plots/{}/run2','plots/{}/hllhc']]

from runLimits import plotSensitivity

##################
# 30 MeV scan
##################
fs = [ ROOT.TFile(d+'/graphs_full_scan_mnd_mz30MeV.root','read') for d in indirs]
g1s = [f.Get('cuts1_meeS_logx2_reach_nd') for f in fs]
g2s = [f.Get('cuts5_meeS_logx2_reach_nd') for f in fs]
gs = []
plotSensitivity('scan_mnd_mz30MeV_noUnc',
                [g1s[0], g2s[0], g1s[1], g2s[1]],
                labs=['150^{fb}, 1 GeV electrons','150^{fb}, 5 GeV electrons',
                      '4^{ab}, 1 GeV electrons','4^{ab}, 5 GeV electrons'],
                xIsMND=True, rangex=(0.03,10), pdir=pdir)

# print (indirs)

# from cfg.histograms import getHists, GetHNames
# from cfg.cuts import cuts
# from cfg.samples import samples, bkg_names, xsecs, refUm4, refEps, refAd, sig_pairs, sig_tags, sortByND, sortByZD, paper_pairs, paper_tags
# from plotUtils import *
# from numpy import sqrt, hypot
# from array import array
