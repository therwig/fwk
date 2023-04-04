#!/usr/bin/env python3A
from Analysis.eventloop import Module
from Analysis.datamodel import Collection
import ROOT
from numpy import sqrt

class myAnalysis(Module):
    def __init__(self):
        self.sumw=0
        # self.i=0
        self.cuts = None
        self.histFile = None
        self.h = None
        self.r = ROOT.TRandom3(2022)
        self.fillBDT = False
        self.cutflow={
            'all':0,
            'good':0,
        }
        self.doSkim={
            "WZ" : False,
            "Wto3L" : False,
            "WISR" : False,
        }
    def setSkim(self,x):
        if x in self.doSkim:
            self.doSkim[x] = True
            self.cutflow['skim'] = 0
        else:
            print ('!! Failed to set skim:',x)
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
    def smearCMSMet(self, p4, sf=1):
        # http://cms-results.web.cern.ch/cms-results/public-results/publications/JME-18-001/index.html
        # approx 20 GeV in both directions
        return ROOT.TLorentzVector(p4.Px() + self.r.Gaus(0, 20)*sf, p4.Py() + self.r.Gaus(0, 20)*sf,0,0)
    
    def checkCut(self, vardict, cname):
        return eval(self.cuts[cname].format(**vardict))

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        for cut in self.cutflow:
            val, a, g = float(self.cutflow[cut]), self.cutflow['good'], self.cutflow['all']
            print("{} count is {}. {:.5f} of 'all'. {:.5f} of 'good'".format(cut, val, val/a, val/g))
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        if self.out:
          self.out.branch("mu_pt", "F")
          self.out.branch("mu_eta", "F")
          self.out.branch("el1_pt", "F")
          self.out.branch("el1_eta", "F")
          self.out.branch("el2_pt", "F")
          self.out.branch("el2_eta", "F")
          self.out.branch("pt_ee", "F")
          self.out.branch("dR_ee", "F")
          self.out.branch("dPhi_ee", "F")
          self.out.branch("m_ee", "F")
          self.out.branch("minPtFrac_ee", "F")
          self.out.branch("met", "F")
          self.out.branch("mtMu", "F")
          self.out.branch("mtEE", "F")
          self.out.branch("pt3L", "F")
          self.out.branch("dPhi_ee_mu", "F")
          self.out.branch("m_ee_mu", "F")
          self.out.branch("truth_mee", "F")
          self.out.branch("truth_mmunu", "F")
          self.out.branch("truth_meemunu", "F")
          self.out.branch("truth_eParent", "I")
          self.out.branch("truth_eGParent", "I")
    
    def analyze(self, event):
        self.cutflow['all'] += 1
        leps = Collection(event, "Lep")
        allParts = Collection(event, "GenPart")
        el1=None
        el2=None
        mu=None
        nu=None
        el1Gen=None
        for p in allParts:
            if abs(p.pdgId)==11 and (el1Gen==None): el1Gen=p
            if abs(p.pdgId)==14 and (nu==None or nu.pt < p.pt): nu=p
        for l in leps:
            if abs(l.pdgId)==13: mu=l
            elif abs(l.pdgId)==11 and (el1==None): el1=l
            elif abs(l.pdgId)==11: el2=l
            # else: print('bad lepton!')

        if (not el1) or (not el2) or (not mu) or (not nu):
            # print('bad event! (less than 3 leptons found)')
            return False
        self.cutflow['good'] += 1
        if el1.pt < el2.pt:
            l=el2
            el2=el1
            el1=l
        ee = el1.p4()+el2.p4()
        mee = ee.M()
        minPtFrac = el2.pt / ee.Pt()
        mupt = mu.pt

        truth_mmunu = (mu.p4()+nu.p4()).M()
        truth_meemunu = (el1.p4()+el2.p4()+mu.p4()+nu.p4()).M()
        passWISR = (el1.parentPdgId<6 or el2.parentPdgId<6)
        passWZ = (not passWISR) and (truth_mmunu + truth_meemunu > 2*80.3)
        passWto3L = (not passWISR) and (not passWZ)
        if self.doSkim["WISR"] and not passWISR: return False
        if self.doSkim["WZ"] and not passWZ: return False
        if self.doSkim["Wto3L"] and not passWto3L: return False
        if 'skim' in self.cutflow: self.cutflow['skim'] += 1
        
        # Gen MET
        met = event.GenMet
        metP4 = ROOT.TLorentzVector()
        metP4.SetPtEtaPhiM(event.GenMet,event.GenMetPhi,0,0)

        # CMS toy smearing
        el1S = self.smearCMS(el1.p4())
        el2S = self.smearCMS(el2.p4())
        e1pt = el1S.Pt()
        e2pt = el2S.Pt()
        eeS = el1S + el2S
        meeS = eeS.M()
        if meeS!=meeS: meeS = 999
        metP4S = self.smearCMSMet(metP4)
        metS = metP4S.Pt()
        metLP4 = -(eeS + mu.p4())
        metL = metLP4.Pt()
        
        # if self.i<2: print(locals() )
        
        # get other parts of the event
        # allParts = Collection(event, "GenPart")
        # nu=None
        # for l in allParts:
        #     if (l.status==1 and abs(l.pdgId)==14):
        #         nu=l
        # if nu==None: print('missed the neutrino')
        # met = nu.pt

        # adding in the mT(e,e,nu) calculation
        mTMu  = ROOT.mt_2(mu.pt, mu.phi,event.GenMet,event.GenMetPhi)
        mTMuS = ROOT.mt_2(mu.pt, mu.phi,metP4S.Pt(), metP4S.Phi())
        mTMuL = ROOT.mt_2(mu.pt, mu.phi,metLP4.Pt(), metLP4.Phi())
        pTMu  = ROOT.pt_2(mu.pt, mu.phi,event.GenMet,event.GenMetPhi)
        pTMuS = ROOT.pt_2(mu.pt, mu.phi,metP4S.Pt(), metP4S.Phi())
        pTMuL = ROOT.pt_2(mu.pt, mu.phi,metLP4.Pt(), metLP4.Phi())
        diEle = eeS #el1.p4()+el2.p4()
        lep3 = diEle + mu.p4()
        mT  = ROOT.mt_2(diEle.Pt(), diEle.Phi(), event.GenMet,event.GenMetPhi)
        mTS = ROOT.mt_2(diEle.Pt(), diEle.Phi(), metP4S.Pt(), metP4S.Phi())
        mTL = ROOT.mt_2(diEle.Pt(), diEle.Phi(), metLP4.Pt(), metLP4.Phi())
        # mTMu = (mu.p4()+metP4).Mt()
        # mTMuS = (mu.p4()+metP4S).Mt()
        # mT = (el1.p4()+el2.p4()+metP4).Mt()
        # mTS = (el1S+el2S+metP4S).Mt()
        # TODO add in dPhi(ll,MET)
        dPhiLepMet  = abs(ROOT.deltaPhi(diEle.Phi(), event.GenMetPhi))
        dPhiLepMetS = abs(ROOT.deltaPhi(diEle.Phi(), metP4S.Phi()))
        dPhiLepMu   = abs(ROOT.deltaPhi(diEle.Phi(), mu.phi))

        dRee = el1S.DeltaR(el2S)
        pTee = ROOT.pt_2(el1S.Pt(), el1S.Phi(), el2S.Pt(), el2S.Phi())
        
        bdt = event.bdt if self.fillBDT else 100
        
        # smear
        meeAdHoc = self.r.Gaus(mee, 0.010 + 0.060 * mee) # 10 MeV + 60 MeV * (mee/GeV)
        while meeAdHoc<0:
            meeAdHoc = self.r.Gaus(mee, 0.010 + 0.060 * mee)
            
        if self.out:
          self.out.fillBranch("mu_pt", mupt)
          self.out.fillBranch("mu_eta", mu.eta)
          self.out.fillBranch("el1_pt", e1pt)
          self.out.fillBranch("el1_eta", el1S.Eta())
          self.out.fillBranch("el2_pt", e2pt)
          self.out.fillBranch("el2_eta", el2S.Eta())
          self.out.fillBranch("pt_ee", ee.Pt()) 
          # self.out.fillBranch("dR_ee", 2*meeS / ee.Pt()) 
          self.out.fillBranch("dR_ee", dRee ) 
          self.out.fillBranch("dPhi_ee", abs(ROOT.deltaPhi(el1S.Phi(), el2S.Phi())))
          self.out.fillBranch("m_ee", meeS)
          self.out.fillBranch("minPtFrac_ee", minPtFrac)
          self.out.fillBranch("met", metS)
          self.out.fillBranch("mtMu", mTMuL)
          self.out.fillBranch("mtEE", mTL)
          self.out.fillBranch("pt3L", metL)
          self.out.fillBranch("dPhi_ee_mu", dPhiLepMu)
          self.out.fillBranch("m_ee_mu", lep3.M())
          self.out.fillBranch("truth_mee", mee)
          self.out.fillBranch("truth_mmunu", truth_mmunu)
          self.out.fillBranch("truth_meemunu", truth_meemunu)
          self.out.fillBranch("truth_eParent", el1.parentPdgId)
          self.out.fillBranch("truth_eGParent", el1.gparentPdgId)
        
        for cn in self.cuts:
            if not self.checkCut(locals(), cn): continue
            self.h[cn+'_yields'].Fill(0.5)
            self.h[cn+'_bdt'].Fill(bdt)
            self.h[cn+'_mt'].Fill(mT)
            self.h[cn+'_ptee'].Fill(pTee)
            self.h[cn+'_dree'].Fill(dRee)
            self.h[cn+'_dree2'].Fill(dRee)
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
            self.h[cn+'_metS'].Fill(metS)
            self.h[cn+'_metL'].Fill(metL)
            self.h[cn+'_mtS'].Fill(mTS)
            self.h[cn+'_mtL'].Fill(mTL)
            self.h[cn+'_mtMu'].Fill(mTMu)
            self.h[cn+'_mtMuS'].Fill(mTMuS) 
            self.h[cn+'_mtMuL'].Fill(mTMuL) 
            self.h[cn+'_ptMu'].Fill(pTMu)
            self.h[cn+'_ptMuS'].Fill(pTMuS) 
            self.h[cn+'_ptMuL'].Fill(pTMuL) 
            self.h[cn+'_dPhiLepMet'].Fill(dPhiLepMet) 
            self.h[cn+'_dPhiLepMetS'].Fill(dPhiLepMetS) 
            self.h[cn+'_dPhiLepMu'].Fill(dPhiLepMu) 

        return True

