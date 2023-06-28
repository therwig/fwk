#!/usr/bin/env python3A
from Analysis.eventloop import Module
from Analysis.datamodel import Collection
import ROOT
from numpy import sqrt, hypot

def findFirst(p, particles):
    while p.genPartIdxMother>=0 and particles[p.genPartIdxMother].pdgId == p.pdgId:
        p = particles[p.genPartIdxMother]
    return p
def pickJets(bjets):
    massMap = {}
    for i in range(len(bjets)):
        for j in range(i+1,len(bjets)):
            massMap[(i,j)] = (bjets[i].p4()+bjets[j].p4()).M()
    dM, idxs = 9e9, []
    for i1 in range(len(bjets)):
      for i2 in range(i1+1,len(bjets)):
        for i3 in range(i2+1,len(bjets)):
          for i4 in range(i3+1,len(bjets)):
            for j in range(3):
              if j==0: m1, m2 = massMap[(i1,i2)], massMap[(i3,i4)]
              if j==1: m1, m2 = massMap[(i1,i3)], massMap[(i2,i4)]
              if j==2: m1, m2 = massMap[(i1,i4)], massMap[(i2,i3)]
              # print ('try', abs(m1-125) + abs(m2-125), dM, idxs)
              if abs(m1-125) + abs(m2-125) < dM:
                  dM = abs(m1-125) + abs(m2-125)
                  idxs = (i1, i2, i3, i4)
    return idxs, dM
                  
class myAnalysis(Module):
    def __init__(self):
        self.counter=0

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        if self.out:
          self.out.branch("nBJets", "I")
          self.out.branch("nBQuarks", "I")
          self.out.branch("bquark_metric", "F")
          self.out.branch("bjet_metric", "F")
          # self.out.branch("truth_eParent", "I")
          
    def analyze(self, event):
        jets = Collection(event, "GenJet")
        bjets = [j for j in jets if j.hadronFlavour==5]
        allParts = Collection(event, "GenPart")
        for i, p in enumerate(allParts): p.idx = i
        bquarks = [allParts[i] for i in set([findFirst(p,allParts).idx for p in allParts if abs(p.pdgId)==5])]
        higgs_bquarks = [b for b in bquarks if b.genPartIdxMother>=0 and allParts[b.genPartIdxMother].pdgId==25]
        # print([(b.idx, allParts[b.genPartIdxMother].idx) for b in higgs_bquarks])

        if len(bjets)<4: return False
        bquark_idxs, bquark_metric = pickJets(higgs_bquarks)
        bjet_idxs, bjet_metric = pickJets(bjets)
        # print( idxs)
        
        self.out.fillBranch("nBJets", len(bjets))
        self.out.fillBranch("nBQuarks", len(bquarks))
        self.out.fillBranch("bquark_metric", bquark_metric)
        self.out.fillBranch("bjet_metric", bjet_metric)
        
        return True

