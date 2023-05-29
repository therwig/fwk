#!/usr/bin/env python3
import sys, os
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')
from cfg.samples import *
from numpy import sqrt, hypot
from array import array

samplesByName = {s.name : s for s in samples if not s.isSM and 'mND10' in s.name}
sig_dfs = {sn: ROOT.RDataFrame("Friends", "data/friends/outS_{}.root".format(sn)) for sn in samplesByName}

ROOT.gInterpreter.Declare('''
#include "TMath.h"
typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double> > PtEtaPhiMVector;
PtEtaPhiMVector smear(PtEtaPhiMVector i, int flag){
  float pt = -1;
  // float res=0.001;
  // if(flag==1) res = min(0.025, max(0.03 - 0.01*log10(i.Pt()) ,0.01)); // barrel
  // if(flag==2) res = min(0.08, max(0.16 - 0.18*log10(i.Pt()) ,0.02)); // endcap
  // while(pt<0) pt = i.Pt() * gRandom->Gaus(1, res); // worst endcap /barrel bin
  while(pt<0) pt = i.Pt() * gRandom->Gaus(1, flag==2 ? 0.08 : 0.025); // worst endcap /barrel bin
  float phi = i.Phi() + gRandom->Gaus(0, flag==2 ? 0.0025 : 0.001); //eta variations
  float eta = 1./TMath::Tan(i.Theta()); // cvt to cottheta
  eta += gRandom->Gaus(0, flag==2 ? 0.002 : 0.0005); // cottheta variations
  eta = TMath::ATan(1./eta); // theta
  eta = -TMath::Log(TMath::Tan(eta/2)); // cvt to eta
  PtEtaPhiMVector o(pt, eta, phi, i.M());
  return o;
}
PtEtaPhiMVector smearMu(PtEtaPhiMVector i, int flag){
  float pt = -1;
  while(pt<0) pt = i.Pt() * gRandom->Gaus(1, 0.01); // worst endcap /barrel bin
  float phi = i.Phi() + gRandom->Gaus(0, flag==2 ? 0.0008 : 0.0003); //eta variations
  float eta = 1./TMath::Tan(i.Theta()); // cvt to cottheta
  eta += gRandom->Gaus(0, flag==2 ? 0.001 : 0.0005); // cottheta variations
  eta = TMath::ATan(1./eta); // theta
  eta = -TMath::Log(TMath::Tan(eta/2)); // cvt to eta
  PtEtaPhiMVector o(pt, eta, phi, i.M());
  return o;
}
float mass_2(float pt1, float eta1, float phi1, float m1, float pt2, float eta2, float phi2, float m2, int i=0, bool isEl=true) {
  PtEtaPhiMVector p41(pt1,eta1,phi1,m1);
  PtEtaPhiMVector p42(pt2,eta2,phi2,m2);
  // 0 no smear, 1=lo, 2=hi
  if (i) p41 = isEl ? smear(p41,i) : smearMu(p41,i);
  if (i) p42 = isEl ? smear(p42,i) : smearMu(p42,i);
  return (p41+p42).M();
}
''')

def rmsX(h,x=68):
    vals = array('d',101*[0])
    q = array('d',[0.01*i for i in range(101)])
    h.GetQuantiles(101,vals,q)
    # print (vals)
    # print (q)
    ret=9e99
    for lo in range(100-x):
        # print(lo, lo+x, vals[lo], vals[lo+x])
        if vals[lo+x] - vals[lo] < ret:
            ret = vals[lo+x] - vals[lo]
    return ret
    
fo = ROOT.TFile('mass.root','recreate')

smears=['mee1','mee2'] #,'mmm1','mmm2']

hs = {smear : {} for smear in smears}
gs = {} #{smear : {} for smear in smears}



for name in sig_dfs:
    m = samplesByName[name].masses[0]
    df = sig_dfs[name]
    df = df.Filter('m_ee>0.0001')
    df = df.Define("mee1", "mass_2(truth_el1_pt,truth_el1_eta,truth_el1_phi,0.000511,truth_el2_pt,truth_el2_eta,truth_el2_phi,0.000511,1,1)")
    df = df.Define("mee2", "mass_2(truth_el1_pt,truth_el1_eta,truth_el1_phi,0.000511,truth_el2_pt,truth_el2_eta,truth_el2_phi,0.000511,2,1)")
    m = samplesByName[name].masses[0]
    # unused
    # don't give a mass for now, since it screws up the kinematics (should still be a fine approximation...)
    r = 1 - (0.105 / m)
    df = df.Define("mmm0", "mass_2(truth_el1_pt,truth_el1_eta,truth_el1_phi,0.105,truth_el2_pt,truth_el2_eta,truth_el2_phi,0.105,0,0)")
    df = df.Define("mmm1", "mass_2(truth_el1_pt,truth_el1_eta,truth_el1_phi,0.105,truth_el2_pt,truth_el2_eta,truth_el2_phi,0.105,1,0)".format(r=r))
    df = df.Define("mmm2", "mass_2(truth_el1_pt,truth_el1_eta,truth_el1_phi,0.105,truth_el2_pt,truth_el2_eta,truth_el2_phi,0.105,2,0)".format(r=r))
    # df = df.Define("mmm1", "mass_2(truth_el1_pt*{r},truth_el1_eta,truth_el1_phi,0.105,truth_el2_pt*{r},truth_el2_eta,truth_el2_phi,0.105,1,0)".format(r=r))
    # df = df.Define("mmm2", "mass_2(truth_el1_pt*{r},truth_el1_eta,truth_el1_phi,0.105,truth_el2_pt*{r},truth_el2_eta,truth_el2_phi,0.105,2,0)".format(r=r))

    for smear in smears:
        if 'mmm' in smear and m < 0.25: continue
        hs[smear][name] = df.Histo1D(('{}_{}'.format(smear,m),';mass',2000,0,3*m), smear)

for smear in smears:
    x, y, y2, y3 = [], [], [], []
    for name in sig_dfs:
        m = samplesByName[name].masses[0]
        if 'mmm' in smear and m < 0.25: continue
        x += [m]
        h = hs[smear][name]
        y += [ h.GetRMS() / h.GetMean() if h.GetMean() else 0]
        y3 += [ rmsX(h)]
        y2 += [ y3[-1] / h.GetMean() if h.GetMean() else 0]
        h.Write()
    g = ROOT.TGraph(len(x), array('d',x), array('d',y))
    g.SetName(smear)
    g.Write()
    g2 = ROOT.TGraph(len(x), array('d',x), array('d',y2))
    g2.SetName(smear+'eff')
    g2.Write()
    g3 = ROOT.TGraph(len(x), array('d',x), array('d',y3))
    g3.SetName(smear+'abs')
    g3.Write()
    gs[smear] = g2

#.append( (m, h1.GetRMS() / h1.GetMean()) )   
#h1.Write()

cms_mu_x = [0.546, 1.02, 5.36]
cms_mu_fwhm = [0.015, 0.0055, 0.11] # FWHM
cms_mu_y = [cms_mu_fwhm[i]/2.355/cms_mu_x[i] for i in range(len(cms_mu_fwhm))]
cms_mu = ROOT.TGraph(3, array('d',cms_mu_x), array('d',cms_mu_y))
print(cms_mu_x)
print(cms_mu_y) # for muons, propose to simply use 1-3% resolution

cms_fit_x = [0.03, 0.1, 0.3, 1]
cms_fit_y = [.35, .15, .1, .07]
cms_fit = ROOT.TGraph(4, array('d',cms_fit_x), array('d',cms_fit_y))

c = ROOT.TCanvas()
c.SetLogx()

mg = ROOT.TMultiGraph()

for smear, g in gs.items():
    mg.Add(g.Clone())

mg.Add(cms_mu)
mg.Add(cms_fit)

mg.Draw("AC*")
mg.GetHistogram().GetYaxis().SetRangeUser(0,0.5)
mg.GetHistogram().GetXaxis().SetRangeUser(0,8)

# cms_mu.Draw("* same")

c.SaveAs('plots/mass.pdf')

def makeUnc(u,d):
    if u.GetN() != d.GetN():
        return
    N = u.GetN()
    g = ROOT.TGraphErrors(N)
    for i in range(N):
        x1 = u.GetX()[i]
        y1 = u.GetY()[i]
        x2 = d.GetX()[i]
        y2 = d.GetY()[i]
        if abs(x1-x2)>1e-6:
            print('mismatch!',x1,x2)
            return
        g.SetPoint(i, x1, (y1+y2)/2.)
        g.SetPointError(i, x1*0.1, abs((y1-y2))/2.)
        print(i,x1,x2,y1,y2)
        #print('Setting {} and {} +/- {} from {} and {}'.format(x1, (y1+y2)/2., abs((y1-y2))/2., y1, y2))
    return g

gUnc = makeUnc(gs['mee1'],gs['mee2'])
gUnc.SetTitle(';m_{ee} [GeV];fractional resolution')
gUnc.SetLineWidth(2)
gUnc.SetLineColor(ROOT.kBlack)
gUnc.SetFillColor(ROOT.kBlue)
gUnc.SetFillStyle(3001)

# gUnc.Draw("AC4")

c.SetTopMargin(0.05)
c.SetRightMargin(0.05)
c.SetLeftMargin(0.11)
c.SetBottomMargin(0.12)

mg = ROOT.TMultiGraph()
gUnc.Draw("AC")
gUp = gs['mee1'].Clone()
gDn = gs['mee2'].Clone()
gUp.SetLineWidth(2)
gUp.SetLineColor(ROOT.kBlue)
gUp.SetLineStyle(2)
gDn.SetLineWidth(2)
gDn.SetLineColor(ROOT.kBlue)
gDn.SetLineStyle(2)
mg.Add(gUnc)
mg.Add(gUp)
mg.Add(gDn)
mg.Draw('ACX')
mg.GetHistogram().GetYaxis().SetRangeUser(0,0.5)
mg.GetHistogram().GetYaxis().SetTitle('Fractional resolution')
mg.GetHistogram().GetXaxis().SetTitle('m_{ee} [GeV]')

mg.GetHistogram().GetXaxis().SetLabelSize(0.04)
mg.GetHistogram().GetYaxis().SetLabelSize(0.04)
mg.GetHistogram().GetXaxis().SetTitleSize(0.05)
mg.GetHistogram().GetYaxis().SetTitleSize(0.05)
mg.GetHistogram().GetXaxis().SetTitleOffset(0.8)
mg.GetHistogram().GetYaxis().SetTitleOffset(1.0)

leg = ROOT.TLegend(0.7,0.75,0.9,0.9)
leg.SetTextFont(42)
leg.SetNColumns(1)
leg.AddEntry(gUnc, 'Nominal', 'l')
leg.AddEntry(gUp,  '1 sigma', 'l')
leg.SetFillStyle(0) 
leg.SetFillColor(0)
leg.SetBorderSize(0)
leg.Draw()

c.SaveAs('plots/massPaper.pdf')

gUnc.SetName('gUnc')
gUp.SetName('gUp')
gDn.SetName('gDn')
gUnc.Write()
gUp.Write()
gDn.Write()

fo.Write()
fo.Close()

#exit(0)
