#!/usr/bin/env python3
import sys, os, argparse
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')

from Analysis.eventloop import eventLoop
from Analysis.treeReaderArrayTools import InputTree
from Analysis.output import FriendOutput, FullOutput
from modules.myAnalysis import myAnalysis

ROOT.gROOT.ProcessLine(".L functions.cc")

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--option", default='', help="Option tag to consider")
args = parser.parse_args()

ifile = ROOT.TFile.Open('data/GluGluToHHTo4B_node_cHHH1.skim.root','read')
itree = ifile.Get('Events')
ofile = ROOT.TFile.Open('myAnaOutput.root','recreate')
otree = FriendOutput(ifile, itree, ofile)
itree = InputTree(itree)

myAna = myAnalysis()
(nall, npass, timeLoop) = eventLoop(inputFile=ifile, outputFile=ofile, inputTree=itree, wrappedOutputTree=otree,
                                    modules=[ myAna ], progress=(100000, sys.stdout), #filterOutput=0,
                                    # maxEvents=100, #args.maxEvents, # optionally truncate large background sample
                                    )

if otree:
    otree.write()
    ofile.Close()

ifile.Close()
