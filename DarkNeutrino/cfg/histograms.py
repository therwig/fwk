import ROOT
import numpy as np
from HistHelper import HistHelper

def getHists(pfxs):
    h = HistHelper()
    for pfx in pfxs:
        h.book(pfx+'_yields',';',1,0,1)
        h.book(pfx+'_bdt',';',100,-40,15)
        h.book(pfx+'_mtMu',';m_{T}(MET,#mu) [GeV];',40,0,120)
        h.book(pfx+'_mtMuS',';m_{T}(MET,#mu) [GeV];',40,0,120)
        h.book(pfx+'_mtMuL',';m_{T}(MET_{lep},#mu) [GeV];',40,0,120)
        h.book(pfx+'_mt',';m_{T}(MET,e^{+},e^{-}) [GeV];',40,0,120)
        h.book(pfx+'_mtS',';m_{T}(MET,e^{+},e^{-}) [GeV];',40,0,120)
        h.book(pfx+'_mtL',';m_{T}(MET_{lep},e^{+},e^{-}) [GeV];',40,0,120)
        h.book(pfx+'_dree',';dR(e^{+},e^{-}) [GeV];',40,0,4)
        h.book(pfx+'_dree2',';dR(e^{+},e^{-}) [GeV];',40,0,0.4)
        h.book(pfx+'_mee',';m(e^{+},e^{-}) [GeV];',40,0,4)
        h.book(pfx+'_meeS',';m(e^{+},e^{-}) [GeV];',40,0,4)
        h.book(pfx+'_meeAdHoc',';m(e^{+},e^{-}) [GeV];',40,0,4)
        bins = np.exp(np.linspace(np.log(0.2), np.log(1.2), 81))
        bins = np.exp(np.linspace(np.log(0.01), np.log(15), 51))
        bins = np.exp(np.linspace(np.log(0.01), np.log(15), 31))
        h.bookBins(pfx+'_mee_logx1',';m(e^{+},e^{-}) [GeV];',bins)
        h.bookBins(pfx+'_meeS_logx1',';m(e^{+},e^{-}) [GeV];',bins)
        h.bookBins(pfx+'_meeAdHoc_logx1',';m(e^{+},e^{-}) [GeV];',bins)
        bins = np.exp(np.linspace(np.log(0.001), np.log(15), 431))
        bins = np.exp(np.linspace(np.log(0.01), np.log(15), 331))
        # bins = np.exp(np.linspace(np.log(0.01), np.log(15), 50))
        h.bookBins(pfx+'_mee_logx2',';m(e^{+},e^{-}) [GeV];',bins)
        h.bookBins(pfx+'_meeS_logx2',';m(e^{+},e^{-}) [GeV];',bins)
        h.bookBins(pfx+'_meeAdHoc_logx2',';m(e^{+},e^{-}) [GeV];',bins)
        h.book(pfx+'_mupt',';p_{T}(#mu) [GeV]',40,0,80)
        h.book(pfx+'_met',';p_{T,miss} [GeV]',40,0,80)
        h.book(pfx+'_metS',';p_{T,miss} [GeV]',40,0,80)
        h.book(pfx+'_metL',';p_{T}(#mu,e^{+},e^{-}) / MET_{lep} [GeV]',40,0,80)
        h.book(pfx+'_e1pt',';p_{T}(e_{1}) [GeV]',40,0,40)
        h.book(pfx+'_e2pt',';p_{T}(e_{2}) [GeV]',40,0,40)
        
        h.book(pfx+'_dPhiLepMet',';d#phi(ll,MET)',32,0,3.2)
        h.book(pfx+'_dPhiLepMetS',';d#phi(ll,MET)',32,0,3.2)
        h.book(pfx+'_dPhiLepMu',';d#phi(ll,#mu)',32,0,3.2)
    
    return h

def GetHNames():
    # d = ROOT.gDirectory
    # print(d)
    dummy = getHists([''])
    ret = [x[1:] for x in dummy.d]
    return ret
