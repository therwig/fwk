import ROOT
import numpy as np
from HistHelper import HistHelper

def getHists(pfxs):
    h = HistHelper()
    for pfx in pfxs:
        h.book(pfx+'_mee',';m(e^{+},e^{-}) [GeV];',100,0,12)
        bins = np.exp(np.linspace(np.log(0.2), np.log(1.2), 80))
        bins = np.exp(np.linspace(np.log(0.01), np.log(15), 80))
        h.bookBins(pfx+'_mee_logx1',';m(e^{+},e^{-}) [GeV];',bins)
        bins = np.exp(np.linspace(np.log(0.001), np.log(15), 430))
        bins = np.exp(np.linspace(np.log(0.01), np.log(15), 330))
        h.bookBins(pfx+'_mee_logx2',';m(e^{+},e^{-}) [GeV];',bins)
        h.book(pfx+'_mupt',';p_{T}(#mu) [GeV]',40,0,80)
        h.book(pfx+'_met',';p_{T}(#nu) [GeV]',40,0,80)
        h.book(pfx+'_e1pt',';p_{T}(e_{1}) [GeV]',40,0,20)
        h.book(pfx+'_e2pt',';p_{T}(e_{2}) [GeV]',40,0,20)
    
    return h

def GetHNames():
    # d = ROOT.gDirectory
    # print(d)
    dummy = getHists([''])
    ret = [x[1:] for x in dummy.d]
    return ret
