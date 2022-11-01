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

    def bookHistos(self, hfile, hhelper):
        self.histFile = hfile
        self.h = hhelper
        # print ([x for x in self.h.d])

    def setCuts(self, c):
        self.cuts = c

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

        # if self.i<2: print(locals() )
        
        # get other parts of the event
        allParts = Collection(event, "GenPart")
        nu=None
        for l in allParts:
            if (l.status==1 and abs(l.pdgId)==14):
                nu=l
        if nu==None: print('missed the neutrino')
        met = nu.pt
        
        for cn in self.cuts:
            if not self.checkCut(locals(), cn): continue
            self.h[cn+'_mee'].Fill(mee)
            self.h[cn+'_mee_logx1'].Fill(mee)
            self.h[cn+'_mee_logx2'].Fill(mee)
            self.h[cn+'_mupt'].Fill(mupt)
            self.h[cn+'_e1pt'].Fill(e1pt)
            self.h[cn+'_e2pt'].Fill(e2pt)
            self.h[cn+'_met'].Fill(met)

        return True

