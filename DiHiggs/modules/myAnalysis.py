#!/usr/bin/env python3A
from Analysis.eventloop import Module
from Analysis.datamodel import Collection
import ROOT
from numpy import sqrt, hypot

class myAnalysis(Module):
    def __init__(self):
        self.counter=0

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        if self.out:
          self.out.branch("sumJet_pt", "F")
          # self.out.branch("truth_eParent", "I")
    
    def analyze(self, event):
        jets = Collection(event, "GenJet")
        allParts = Collection(event, "GenPart")
        #print( len(jets), len(allParts))
        self.out.fillBranch("sumJet_pt", sum([j.pt for j in jets]))
        
        return True

