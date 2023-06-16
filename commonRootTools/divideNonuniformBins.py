import ROOT
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("rootFile", help="")
parser.add_argument("numeratorName", help="")
parser.add_argument("denominatorName", help="")
args = parser.parse_args()

f = ROOT.TFile(args.rootFile,'r')
n = f.Get(args.numeratorName)
d = f.Get(args.denominatorName)

for nx in range(1,n.GetNbinsX()+1):
    for ny in range(1,n.GetNbinsY()+1):
        x = n.GetXaxis().GetBinCenter(nx)
        y = n.GetYaxis().GetBinCenter(ny)
        dx = d.GetXaxis().FindBin(x)
        dy = d.GetYaxis().FindBin(y)
        dval = d.GetBinContent(dx,dy)
        if dval: n.SetBinContent(nx, ny, n.GetBinContent(nx, ny)/dval)


c = ROOT.TCanvas()
c.SetTopMargin(0.05)
c.SetBottomMargin(0.15)
c.SetLeftMargin(0.16)
c.SetRightMargin(0.12)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPaintTextFormat('1.2f')
n.Draw('colz text')
n.SetTitle(';lepton p_{T} [GeV]; H_{T} GeV')
c.SaveAs('ratio_'+args.numeratorName+'.pdf')
    
f.Close()
