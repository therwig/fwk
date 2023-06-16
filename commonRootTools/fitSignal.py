import ROOT, os
from array import array
from math import sqrt
import numpy as np

rand = ROOT.TRandom3(2023)

def getChi2(sig, bkg, flatBkgSyst=0.0, plotName=''):
    n = sig.GetNbinsX()
    s = np.array([sig.GetBinContent(i) for i in range(1,n+1)])
    b = np.array([bkg.GetBinContent(i) for i in range(1,n+1)])
    bStat = np.array([bkg.GetBinError(i) for i in range(1,n+1)])
    bSyst = flatBkgSyst*b
    bErr = np.hypot(bStat,bSyst)
    # chi2 = ((S+B - B) / Err)^2 = S^2/ERR^2
    pulls = np.divide(s, bErr, out=np.zeros_like(s), where=bErr!=0)
    chi2 = np.sum(pulls*pulls)
    if len(plotName):
        if False: print('s ',s)
        if False: print('b ',b)
        if False: print('bSqrt ',np.sqrt(b))
        if False: print('bStat',bStat)
        if False: print('bSyst',bSyst)
        if False: print('bErr',bErr)
        if False: print('pulls',pulls)
        # plot B, S+B
        c = ROOT.TCanvas()
        c.SetLogx(1)
        hb = bkg.Clone('hb')
        hs = sig.Clone('hs')
        hsb= bkg.Clone('hsb'); hs.Add(hb)
        hb.SetLineColor(ROOT.kBlack)
        hsb.SetLineColor(ROOT.kRed)
        hsb.Draw('hist')
        hb.Draw('e same')
        hb.Draw('hist same')
        c.SaveAs(plotName+'_debug.pdf(')
        # plot B, S+B, now with uniform bins
        c.SetLogx(0)
        hb = ROOT.TH1F('hb_','',n,0,n)
        hs = hb.Clone('hs_')
        hsb= hb.Clone('hsb_')
        for i in range(n):
            hs.SetBinContent(i+1,s[i])
            hb.SetBinContent(i+1,b[i])
            hsb.SetBinContent(i+1,s[i]+b[i])
            hb.SetBinError(i+1,bErr[i])
            hs.SetBinError(i+1,0)
            hsb.SetBinError(i+1,0)
        hb.SetLineColor(ROOT.kBlack)
        hsb.SetLineColor(ROOT.kRed)
        hsb.Draw('hist')
        hb.Draw('e same')
        hb.Draw('hist same')
        c.SaveAs(plotName+'_debug.pdf')
        # plot the pulls
        hp = hsb.Clone('hp')
        for i in range(n):
            hp.SetBinContent(i+1,pulls[i])
            hp.SetBinError(i+1,0)
            hb.SetBinContent(i+1,0)
            hb.SetBinError(i+1,1)
        hp.Draw('hist')
        hb.Draw('e same')
        hb.Draw('hist same')
        tl = ROOT.TLatex(); tl.SetNDC()
        tl.DrawText(0.2,0.9,'Total Chi2 = {:.2f}'.format(chi2))
        c.SaveAs(plotName+'_debug.pdf)')
        
    return chi2


def getMuSigInterval(sig, bkg, flatBkgSyst=0.0, maxChi2=5, plotName='', nToys=1000, forceToys=False):
    useToys = forceToys
    if len(plotName): useToys = True
    nomChi2 = getChi2(sig, bkg, flatBkgSyst, plotName=plotName)
    if useToys:
        pseudoChi2s=[0] if nToys==0 else []
        for nToy in range(nToys):
            bToy = bkg.Clone('btoy')
            for i in range(bToy.GetNbinsX()+2):
                bToy.SetBinContent(i, rand.Gaus(0, bToy.GetBinError(i)) )
            pseudoChi2s.append( getChi2(bToy, bkg, flatBkgSyst) )
        pseudoChi2s.sort()
        pseudoChi2_95 = pseudoChi2s[int(len(pseudoChi2s)*0.95)]
        if len(plotName):
            c = ROOT.TCanvas("c","")
            hchi2 = ROOT.TH1F('pseudochi2',';chi2', 100, 0, 1.1*pseudoChi2s[-1])
            for x in pseudoChi2s: hchi2.Fill(x)
            hchi2.Draw('hist')
            c.SaveAs(plotName+"_chi2.pdf(")
            hchi2c = hchi2.Clone('hchi2c')
            for i in range(sig.GetNbinsX()+2): hchi2c.SetBinContent( i, hchi2c.Integral(0,i) )
            hchi2c.Draw('hist')
            c.SaveAs(plotName+"_chi2.pdf")
            #print('chi2s: ', pseudoChi2_95, ROOT.TMath.ChisquareQuantile(0.95,sig.GetNbinsX()), ROOT.TMath.ChisquareQuantile(0.05,sig.GetNbinsX()))
    else:
        pseudoChi2_95 = ROOT.TMath.ChisquareQuantile(0.95,sig.GetNbinsX())
    
    maxSF = sqrt(maxChi2/nomChi2) if nomChi2 else 1
    # maxSF = sqrt(maxChi2/nomChi2)
    nScan=10
    sfs = [-maxSF+i*maxSF/nScan for i in range(2*nScan+1)]
    chi2s=[]
    for sf in sfs:
        sScaled = sig.Clone("sScaled")
        sScaled.Scale(sf)
        chi2s.append( getChi2(sScaled, bkg) )

    g = ROOT.TGraph(len(sfs),array('d',sfs),array('d',chi2s))
    g.SetTitle(';signal strength;chi2')
    g.SetName('chi2')
    g.Fit('pol2','Q')
    fitFunc = g.GetFunction("pol2")
    fitParam = (fitFunc.GetParameter(2)) # chi2 = fitParam * sf^2
    if len(plotName):
        # c = ROOT.TCanvas("c","")
        g.Draw("A*")
        c.SaveAs(plotName+"_chi2.pdf)")
        # print("The allowed 2sigma signal stength is +/-{:.2f}".format(sqrt(4/fitParam)))
    return sqrt(pseudoChi2_95/fitParam) if fitParam else 9e99
    # return sqrt(4/fitParam) # need nDOF ?

def getChi2Deprecated(sig, bkg, flatBkgSyst=0.0):
    chi2=0
    for i in range(1,sig.GetNbinsX()+1):
        b = bkg.GetBinContent(i)
        bStat = bkg.GetBinError(i)
        bSyst = flatBkgSyst * b
        s = sig.GetBinContent(i)
        # chi2 = ((S+B - B) / Err)^2 = S^2/ERR^2
        chi2 += s*s / (bStat*bStat + bSyst*bSyst) if bStat+bSyst else 0
    return chi2

def getMuSigIntervalDeprecated(sig, bkg, flatBkgSyst=0.0, maxChi2=5, plotName=''):
    nomChi2 = getChi2(sig, bkg, flatBkgSyst)
    maxSF = sqrt(maxChi2/nomChi2)
    nScan=10
    sfs = [-maxSF+i*maxSF/nScan for i in range(2*nScan+1)]
    chi2s=[]
    for sf in sfs:
        sScaled = sig.Clone("sScaled")
        sScaled.Scale(sf)
        chi2s.append( getChi2(sScaled, bkg) )
    chi2s.sort()
    g = ROOT.TGraph(len(sfs),array('d',sfs),array('d',chi2s))
    g.SetTitle(';signal strength;chi2')
    g.SetName('chi2')
    g.Fit('pol2','Q')
    fitFunc = g.GetFunction("pol2")
    fitParam = (fitFunc.GetParameter(2)) # chi2 = fitParam * sf^2
    if len(plotName):
        c = ROOT.TCanvas("c","")
        g.Draw("A*")
        c.SaveAs(plotName+"_chi2.pdf)")
        # print("The allowed 2sigma signal stength is +/-{:.2f}".format(sqrt(4/fitParam)))
    return sqrt(4/fitParam)

# tester
def test():
    f = ROOT.TFile('out_fitSignal.root','recreate')    
    b = ROOT.TH1F('b','',100,0,100)
    s = ROOT.TH1F('s','',100,0,100)
    for i in range(100):
        x = 0.5 + i
        b.Fill(x, ROOT.TMath.Exp(-x/20))
    b.Scale(1000/b.Integral()) # scale to 1000 events
    for i in range(100):
        b.SetBinError(i+1, sqrt(b.GetBinContent(i+1)))
    sfunc = ROOT.TF1("sfunc","TMath::Gaus(x,50,10)",0,100)
    s.FillRandom("sfunc",1000)
    s.Scale(10/1000) # scale to 10 events

    getMuSigInterval(s, b, plotName='tester')

    ## This is absorbed into the above function, but
    ##   can keep this for now so the graph is recorded.
    nomChi2 = getChi2(s, b)
    # want to scan to about +/-5
    maxSF = sqrt(5/nomChi2)
    nScan=10
    sfs = [-maxSF+i*maxSF/nScan for i in range(2*nScan+1)]
    chi2s=[]
    for sf in sfs:
        sScaled = s.Clone("sScaled")
        sScaled.Scale(sf)
        chi2s.append( getChi2(sScaled, b) )

    g = ROOT.TGraph(len(sfs),array('d',sfs),array('d',chi2s))
    g.SetTitle(';signal strength;chi2')
    g.SetName('chi2')
    g.Fit('pol2','Q')
    fitFunc = g.GetFunction("pol2")
    fitParam = (fitFunc.GetParameter(2)) # chi2 = fitParam * sf^2
    print("The allowed 2sigma signal stength is +/-{:.2f}".format(sqrt(4/fitParam)))
    
    
    s.Write()
    b.Write()
    g.Write()
    f.Close()
    
if __name__ == "__main__":
    test()
