#!/usr/bin/env python3
from Analysis.eventloop import Module
from Analysis.datamodel import Collection
import ROOT

class myAnalysis(Module):
    def __init__(self):
        self.sumw=0
        # self.i=0
        self.cuts = None
        self.histFile = None
        self.h = None
        self.r = ROOT.TRandom3(2022)

    def bookHistos(self, hfile, hhelper):
        self.histFile = hfile
        self.h = hhelper
        # print ([x for x in self.h.d])

    def setCuts(self, c):
        self.cuts = c

    def smearCMS(self, p4, sf=1):
        # https://arxiv.org/pdf/1405.6569.pdf, Fig 17 for eta/phi
        # http://cms-results.web.cern.ch/cms-results/public-results/publications/EGM-17-001/CMS-EGM-17-001_Figure_011-a.pdf for pt
        pt=-1
        while not pt >0: pt = p4.Pt() * self.r.Gaus(1, 0.1*sf)
        phi = p4.Phi() + self.r.Gaus(0, 0.002*sf) # in radians for 10 GeV
        # cottheta is a bit better 0.0006 but can just take 0.001 for simplicity
        cottheta = 1./ROOT.TMath.Tan(p4.Theta()) # better never be 0 !
        cottheta += self.r.Gaus(0, 0.002*sf)
        theta = ROOT.TMath.ATan(1./cottheta)
        eta = -ROOT.TMath.Log(ROOT.TMath.Tan(theta/2))
        tlv = ROOT.TLorentzVector()
        tlv.SetPtEtaPhiM(pt, eta, phi, p4.M())
        return tlv
    
    def checkCut(self, vardict, cname):
        return eval(self.cuts[cname].format(**vardict))
        
    def analyze(self, event):
        self.sumw += 1
        leps = Collection(event, "Lep")
        el1=None
        el2=None
        mu=None
        for l in leps:
            if abs(l.pdgId)==13: mu=l
            elif abs(l.pdgId)==11 and (el1==None): el1=l
            elif abs(l.pdgId)==11: el2=l
            else: print('bad lepton!')

        if (not el1) or (not el2) or (not mu):
            print('bad event!')
            return False
        if el1.pt < el2.pt:
            l=el2
            el2=el1
            el1=l
        ee = el1.p4()+el2.p4()
        mee = ee.M()
        minPtFrac = el2.pt / ee.Pt()
        mupt = mu.pt
        e1pt = el1.pt
        e2pt = el2.pt

        # CMS toy smearing
        el1S = self.smearCMS(el1.p4())
        el2S = self.smearCMS(el2.p4())
        meeS = (el1S+el2S).M()
        # if self.i<2: print(locals() )
        
        # get other parts of the event
        allParts = Collection(event, "GenPart")
        nu=None
        for l in allParts:
            if (l.status==1 and abs(l.pdgId)==14):
                nu=l
        if nu==None: print('missed the neutrino')
        met = nu.pt

        # TODO
        # add in mT(e,e,nu) calculation
        mT = (el1S+el2S+nu.p4()).Mt()
        
        # smear
        meeAdHoc = self.r.Gaus(mee, 0.010 + 0.060 * mee) # 10 MeV + 60 MeV * (mee/GeV)
        while meeAdHoc<0:
            meeAdHoc = self.r.Gaus(mee, 0.010 + 0.060 * mee)
        
        for cn in self.cuts:
            if not self.checkCut(locals(), cn): continue
            self.h[cn+'_mt'].Fill(mT)
            self.h[cn+'_mee'].Fill(mee)
            self.h[cn+'_mee_logx1'].Fill(mee)
            self.h[cn+'_mee_logx2'].Fill(mee)
            self.h[cn+'_meeS'].Fill(meeS)
            self.h[cn+'_meeS_logx1'].Fill(meeS)
            self.h[cn+'_meeS_logx2'].Fill(meeS)
            self.h[cn+'_meeAdHoc'].Fill(meeAdHoc)
            self.h[cn+'_meeAdHoc_logx1'].Fill(meeAdHoc)
            self.h[cn+'_meeAdHoc_logx2'].Fill(meeAdHoc)
            self.h[cn+'_mupt'].Fill(mupt)
            self.h[cn+'_e1pt'].Fill(e1pt)
            self.h[cn+'_e2pt'].Fill(e2pt)
            self.h[cn+'_met'].Fill(met)

        return True

