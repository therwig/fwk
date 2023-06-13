#!/usr/bin/env python3
import ROOT, argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("input", help="Input ROOT file path")
parser.add_argument("-o", "--output", default='', help="Output file path")
args = parser.parse_args()
if len(args.output)==0: args.output = args.input.replace('.root','.skim.root')
print('Converting {} to {}'.format(args.input,args.output))
df = ROOT.RDataFrame("Events", args.input)

# load the column names, and select those to save
goodCollections = ['GenJet','GenPart']
allColumns = list(map(str,df.GetColumnNames()))
toSave=[]
for coll in goodCollections:
    toSave.append('n'+coll)
    toSave += [c for c in allColumns if c.split('_')[0]==coll]
    
print('Saving columns:', toSave)
df.Snapshot('Events', args.output, toSave)

