import ROOT
import os
from math import hypot
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(ROOT.kFruitPunch)
COLZ=[ROOT.kBlack, ROOT.kRed, ROOT.kBlue, 8,6,7,9]+list(range(40,180))
marks=list(range(20,35))


def save(canv, name, pdir='plots/', exts=['.pdf']):
    os.system('mkdir -p '+pdir)
    for i, ext in enumerate(exts):
        os.system('mkdir -p '+pdir+'/'+ext[1:])
        canv.SaveAs(pdir+'/'+ext[1:]+'/'+name+ext)
        if 'eps' in ext:
            os.system('mkdir -p '+pdir+'/epspdf')
            n1 = pdir+'/eps/'+name+'.eps'
            n2 = pdir+'/epspdf/'+name+'.pdf'
            os.system('epstopdf {} {}'.format(n1,n2))
        
        # save(canv, name, pdir+'/'+ext[1:], [ext])
        # if i: # save other formats in a subdir
        #     save(canv, name, pdir+'/'+ext[1:], [ext])
        # else:
        #     canv.SaveAs(pdir+'/'+name+ext)

def plot(name, _hists, pdir='plots/', toStack=[], labs=[], legtitle='',
         xtitle='', ytitle='', rescale=None, legstyle='',toptext='',
         spam=[], spamalign=13,
         legcoors=(0.7,0.6,0.88,0.9), redrawBkg=False, normStack=False,
         xlims=None, legcols=1, gridx=False,gridy=False, exts=['.pdf'],
         logx=False, logy=False, ymin=0, ymax=None, colz=None, fcolz=None, dopt='',
         bsub=False, ratio = False, ratlims=(0.9,1.1), spamxy=(0.13,0.85)):
    if not colz: colz = COLZ
    c = ROOT.TCanvas()
    pad = c
    hists = [h.Clone() for h in _hists]
    if normStack:
        bTot=0
        for ih,h in enumerate(hists):
            if ih in toStack:
                bTot += h.Integral(0,h.GetNbinsX()+1)
        for ih,h in enumerate(hists):
            if ih in toStack:
                h.Scale( 1./ bTot )
            else:
                h.Scale( 1./ h.Integral(0,h.GetNbinsX()+1) )
        
    twoPanel = (bsub or ratio)
    if twoPanel:
        p1 = ROOT.TPad("pad1","pad1",0,0.30,1,1)
        p1.SetBottomMargin(0.002) #0.025)
        p1.Draw()
        p2 = ROOT.TPad("pad2","pad2",0,0,1,0.30)
        p2.SetTopMargin(0.06)
        p2.SetBottomMargin(0.25)
        p2.SetFillStyle(0)
        p2.Draw()
        p1.cd()
        pad = p1

    if ymin==0 and logy: ymin = 5e-4
    pad.SetLogx(logx)
    pad.SetLogy(logy)
    pad.SetGridx(gridx)
    pad.SetGridy(gridy)

    leg = ROOT.TLegend(*legcoors)
    leg.SetTextFont(42)
    leg.SetNColumns(legcols)
    if len(legtitle): leg.SetHeader(legtitle)
    
    # first build the stack if needed
    hStack=ROOT.THStack()
    hSum=hists[0].Clone('sum')
    hSum.Reset()
    
    # loop to format histograms before drawing
    hmax=0
    maxBin=0
    for i,h in enumerate(hists):
        if rescale=='norm': h.Scale(1./h.Integral() if h.Integral() else 1)
        elif type(rescale)==list: h.Scale(rescale[i])
        elif rescale: h.Scale(rescale)
        if h.GetMaximum() > hmax:
            hmax = h.GetMaximum()
            maxBin = h.GetMaximumBin()
        h.SetLineWidth(2)
        if colz[i]:
            h.SetLineColor(colz[i])
            h.SetMarkerColor(colz[i])
        if fcolz and i<len(fcolz) and fcolz[i]:
            h.SetFillColor(fcolz[i])
            h.SetFillStyle(1001)
        else:
            h.SetFillColor(0)
        if i in toStack:
            h.SetLineColor(ROOT.kBlack)
            hSum.Add(h)
            hStack.Add(h) # don't draw until the end
        # legend 
        lab = labs[i] if len(labs)>i else h.GetName()
        legsty = 'mlp'
        if legstyle:
            if type(legstyle)==str:
                legsty = legstyle
            elif type(legstyle)==list:
                legsty = legstyle[i]
        # legsty = legstyle if legstyle else 'mlp'
        leg.AddEntry(h,lab,legsty)

    if hSum.GetMaximum() > hmax:
        hmax = hSum.GetMaximum()
        maxBin = hSum.GetMaximumBin()
    leftLeg = maxBin > hists[0].GetNbinsX() / 2 # implement this some day...
    
    # drawing
    if len(toStack):
        hStack.Draw('hist')
        hSum.SetLineColor(ROOT.kBlack)
        hSum.SetLineWidth(2)
        hSum.Draw("hist same")
    else: hists[0].Draw(dopt)
    
    for i,h in enumerate(hists):
        if i in toStack: continue
        # elif i==0: h.Draw(" "+dopt)
        else: h.Draw("same "+dopt)

    # hStack.Draw('same' if len(toStack)<len(hists) else '')
    
    h0=hists[0]
    if redrawBkg: h0.Draw("same "+dopt)
    if len(toStack):
        hStack.GetXaxis().SetTitle(h0.GetXaxis().GetTitle())
        hStack.GetYaxis().SetTitle(h0.GetYaxis().GetTitle())
        h0 = hStack
    h0.GetYaxis().SetRangeUser(ymin,ymax if ymax else (3 if logy else 1.2)*hmax)
    h0.SetMaximum(ymax if ymax else (3 if logy else 1.2)*hmax)
    if xlims: h0.GetXaxis().SetRangeUser(*xlims)
    # h0.GetYaxis().SetRangeUser(ymin,1450e3)
    if len(xtitle): h0.GetXaxis().SetTitle(xtitle)
    if len(ytitle): h0.GetYaxis().SetTitle(ytitle)
    
    leg.SetFillStyle(0) 
    leg.SetFillColor(0)
    leg.SetBorderSize(0)
    if labs!='none':
        leg.Draw()
    
    h0.Draw('axis same')

    # make the ratio plot if desired
    if twoPanel:
        p2.cd()
        rats = [h.Clone(h.GetName()+"_rat") for h in hists]
        r0 = rats[0].Clone()
        for i, rat in enumerate(rats):
            # careful here... come back to this logic after testing
            if bsub and i: rat.Add(r0)
            rat.Divide(r0)
            if i==0:
                print(i, rat.GetBinContent(40))
                rat.Draw("e2 ")
                rat.GetYaxis().SetRangeUser(*ratlims)
            else:
                print(i, rat.GetBinContent(40))
                rat.Draw("hist same")
                

    
    if toptext:
        tl = ROOT.TLatex(0.1,0.92, toptext)
        tl.SetNDC()
        tl.SetTextFont(12)
        tl.SetTextSize(0.03)
        tl.Draw()
        # tl.Draw()
        
    if len(spam):
        x, y = spamxy
        tl = ROOT.TLatex()
        tl.SetTextAlign(spamalign)
        tl.SetNDC()
        tl.SetTextFont(42)
        tl.SetTextSize(0.04)
        for l in spam:
            tl.DrawLatex(x,y,l)
            y -= 0.05
    
    save(c, name, pdir=pdir, exts=exts)


def plotGraphs(name, graphs, pdir='plots/', labs=[], legtitle='',
               xtitle='', ytitle='', legstyle='',
               legcoors=(0.7,0.6,0.88,0.9),
               xlims=None, ymin=0, ymax=None, legcols=1,
               logx=False, logy=False, colz=None, styz=None, dopt='',toRoot=False):
    if not colz: colz = COLZ
    c = ROOT.TCanvas()
    c.SetLogy(logy)
    c.SetLogx(logx)

    leg = ROOT.TLegend(*legcoors)
    leg.SetTextFont(42)
    leg.SetNColumns(legcols)
    if len(legtitle): leg.SetHeader(legtitle)
    
    hmin, hmax = 9e99, 0
    mg = ROOT.TMultiGraph()
    for i,g in enumerate(graphs):
        hmax=max([hmax] + [g.GetY()[i] for i in range(g.GetN())])
        hmin=min([hmin] + [g.GetY()[i] for i in range(g.GetN())])
        g.SetLineWidth(2)
        g.SetLineColor(colz[i])
        g.SetMarkerColor(colz[i])
        if styz: g.SetLineStyle(styz[i])
        lab = labs[i] if len(labs)>i else g.GetName()
        legsty = legstyle if legstyle else 'mlp'
        leg.AddEntry(g,lab,legsty)
        mg.Add(g.Clone())

    mg.Draw(dopt if len(dopt) else 'APE')
    h0=mg.GetHistogram()
    # h0.GetYaxis().SetRangeUser(ymin,(3 if logy else 1.2)*hmax)
    mg.SetMinimum(0.8 if (ymin==0 and logy) else ymin)
    # mg.SetMinimum(hmin/3 if logy else 0)
    mg.SetMaximum((3 if logy else 1.2)*hmax)
    if ymax!=None: h0.SetMaximum(ymax)
    # if ymin!=None: h0.SetMinimum(ymin)
    if xlims: h0.GetXaxis().SetRangeUser(*xlims)
    # h0.GetYaxis().SetRangeUser(ymin,1450e3)
    if len(xtitle): h0.GetXaxis().SetTitle(xtitle)
    if len(ytitle): h0.GetYaxis().SetTitle(ytitle)
    # if logx: h0.GetXaxis().SetMoreLogLabels()
    # if logy: h0.GetYaxis().SetMoreLogLabels()
    
    leg.SetFillStyle(0) 
    leg.SetFillColor(0)
    leg.SetBorderSize(0)
    if labs!='none':
        leg.Draw()
    
    # h0.Draw('axis same')
    
    save(c, name, pdir=pdir)
    if toRoot:
        fout = ROOT.TFile(pdir+'/'+name+'_graphs.root','reacreate')
        for g in graphs: g.Write()
        fout.Close()
            
def dumpToTxt(fname, h, lims=None):
    f = open(fname+'.txt','w')
    for i in range(1,h.GetNbinsX()+1):
        x = h.GetBinCenter(i)
        y = h.GetBinContent(i)
        if lims and (x<lims[0] or x>lims[1]): continue
        f.write('{} {}\n'.format(x,y))
    f.close()
    
def dumpToTxtG(fname, g):
    f = open(fname+'.txt','w')
    for i in range(g.GetN()):
        x = g.GetX()[i]
        y = g.GetY()[i]
        f.write('{} {}\n'.format(x,y))
    f.close()

# could also handle errors if its not a vanilla tgraph
def sortGraph(g):
    vals=[ (g.GetX()[i], g.GetY()[i]) for i in range(g.GetN())]
    vals.sort(key=lambda x:x[0])
    for i in range(g.GetN()):
        g.SetPoint(i, vals[i][0], vals[i][1])

def addBin(h, x1, x2):
    h.SetBinContent(x1, h.GetBinContent(x1) + h.GetBinContent(x2))
    h.SetBinError(x1, hypot(h.GetBinError(x1), h.GetBinError(x2)))
    h.SetBinContent(x2, 0)
    h.SetBinError(x2, 0)
def addBin2d(h,  x1,  y1,  x2,  y2):
    h.SetBinContent(x1,y1, h.GetBinContent(x1,y1) + h.GetBinContent(x2,y2))
    h.SetBinError(x1,y1, hypot(h.GetBinError(x1,y1), h.GetBinError(x2,y2)))
    h.SetBinContent(x2,y2, 0)
    h.SetBinError(x2,y2, 0)
def removeOverflow(h):
    addBin(h, 1, 0)
    addBin(h, h.GetNbinsX(), h.GetNbinsX()+1)
def removeOverflow2d(h):
    for binx in range(h.GetNbinsX()+2):
        addBin2d(h, binx, h.GetNbinsY(), binx, h.GetNbinsY()+1)
        addBin2d(h, binx, 1, binx, 0)
    for biny in range(h.GetNbinsY()+2):
        addBin2d(h, h.GetNbinsX(), biny, h.GetNbinsX()+1, biny)
        addBin2d(h, 1, biny, 0, biny)
        
