
def plotPaper(name, hs, legPos='R', doNorm=False,
              xtitle='', ytitle='', logx=False, logy=False, pdir='./'):
    pname = os.path.basename(pdir+'/paper/'+name)
    dname = os.path.dirname(pdir+'/paper/'+name)
    legcoors=[0.6,0.55,0.88,0.9]
    if legPos=='L':
        legcoors[2] = 0.1 + legcoors[2] - legcoors[0]
        legcoors[0] = 0.1
    plot(pname, hs, pdir=dname, legcoors=(0.55,0.50,0.88,0.9),
         toStack=toStack, labs=papLabs, legstyle=papSty,
         fcolz=fPapColz, colz=lPapColz, 
         logx=logx, logy=logy, dopt='hist', spam=['#sqrt{s} = '+str(sqrts)+' TeV, '+str(lumi)+' fb^{-1}'], #,'Dark Neutrino'],
         xtitle=xtitle, ytitle=ytitle, normStack=doNorm)

import numpy as np
def text2graph(fname, delimiter=' ', dupLast=False, cols=[0,1]):
    constraints = np.genfromtxt(fname,delimiter=delimiter)
    xvals = list(constraints[:,cols[0]]) + ([constraints[0,cols[0]]] if dupLast else [])
    yvals = list(constraints[:,cols[1]]) + ([constraints[0,cols[1]]] if dupLast else [])
    xvals, yvals = array('d',xvals), array('d',yvals) #promblems with np
    return  ROOT.TGraph(len(xvals), array('d',xvals), array('d',yvals))

def plotSensitivity(saveName, gs, labs=[], xIsMND=True, sfx='',toRoot=True, rangex=None, pdir='./'):
    c = ROOT.TCanvas()
    c.SetLogy()
    c.SetLogx()
    mg = ROOT.TMultiGraph()
    if xIsMND:
        gSig1 = text2graph('external_lines/sig1v2.txt', delimiter=',', dupLast=True); gSig1.SetLineColor(ROOT.TColor.GetColor('#FFFF61'))
        gSig2 = text2graph('external_lines/sig2v2.txt', delimiter=',', dupLast=True); gSig2.SetLineColor(ROOT.TColor.GetColor('#75FB4C'))
        gSig3 = text2graph('external_lines/sig3v2.txt', delimiter=',', dupLast=True); gSig3.SetLineColor(ROOT.TColor.GetColor('#4FA8AA'))
        gSig4 = text2graph('external_lines/sig4v2.txt', delimiter=',', dupLast=True); gSig4.SetLineColor(ROOT.TColor.GetColor('#0000F5'))
        gSig5 = text2graph('external_lines/sig5v2.txt', delimiter=',', dupLast=True); gSig5.SetLineColor(ROOT.TColor.GetColor('#7B1E82'))
        for g in [gSig1,gSig2,gSig3,gSig4,gSig5]:
            g.SetLineWidth(2)
            mg.Add(g)
    else:
        pass
            
    leg = ROOT.TLegend(0.6,0.5,0.9,0.75)
    leg.SetTextFont(42)
    leg.SetNColumns(1)

    gConst = text2graph('external_lines/const_mnd.txt') #if xIsMND else text2graph('external_lines/const_mzd.txt')
    gConst.SetLineWidth(2); gConst.SetLineColor(ROOT.kBlack)
    mg.Add(gConst)
    mg.Draw("AC") # dummy draw
    for ig, g in enumerate(gs):
        g.SetLineWidth(2)
        g.SetLineColor(COLZ[ig+1])
        g.SetFillColor(COLZ[ig+1])
        g.SetFillStyle(3001)
        mg.Add(g.Clone()) # don't transfer ownership
        if ig < len(labs):
            leg.AddEntry(g, labs[ig], 'fl' if g.InheritsFrom('TGraphErrors') else 'l')

    if xIsMND: mg.SetTitle(";m(N_{D}) [GeV]; |U_{#mu 4}|^{2}")
    else: mg.SetTitle(";m(Z_{D}) [GeV]; |U_{#mu 4}|^{2}")
    mg.GetHistogram().GetXaxis().SetTitleOffset(1.3) #SetTitle(";m(N_{D}) [GeV]; |U_{#mu 4}|^{2}")
    mg.GetHistogram().GetXaxis().SetLimits(0.01,10)
    mg.SetMaximum(0.1)
    mg.Draw("L3 same")
    if rangex:
        mg.GetHistogram().GetXaxis().SetLimits(*rangex)

    leg.SetFillStyle(0) 
    leg.SetFillColor(0)
    leg.SetBorderSize(0)
    if len(labs):
        leg.Draw()
        
    c.SaveAs(pdir+'/limits/full_' + saveName + sfx + '.pdf')
    if toRoot:
        fout = ROOT.TFile(pdir+'/limits/graphs_full_' + saveName + sfx + '.root','recreate')
        for g in gs:
            g.Write()
        fout.Close()

def CombSig(g1, g2, debug=False):
    xs, ys = [], []
    if g1.GetN() != g2.GetN():
        print('mismatch in number of points!')
        return
    for i in range(g1.GetN()):
        x1 = g1.GetX()[i]
        x2 = g2.GetX()[i]
        if abs(x2-x1) > 1e-5:
            print('mismatch in point x values!')
            return
        s1 = g1.GetY()[i]
        s2 = g2.GetY()[i]
        xs.append(x1)
        if s1==0: ys.append(s2)
        elif s2==0: ys.append(s1)
        else: ys.append( s1*s2/hypot(s1,s2) )
    gNew = ROOT.TGraph(len(xs),array('d',xs), array('d',ys))
    return gNew
    
def ApplyBR(g, isEl=True, debug=False):
    withElx=[]
    withEly=[]
    gxvals = g.GetX()
    br = brEl if isEl else brMu
    if debug:
        print('input points:')
        print(' x:',[g.GetX()[i] for i in range(g.GetN())])
        print(' y:',[g.GetY()[i] for i in range(g.GetN())])
    for i in range(br.GetN()):
        x = br.GetX()[i]
        if debug: print('considering',x,'...',end='')
        if x < gxvals[0]: continue
        if x > gxvals[g.GetN()-1]: continue
        withElx.append(x)
        withEly.append( g.Eval(x) / br.GetY()[i] )
        if debug: print(' added',withElx[-1], withEly[-1],' from limit',g.Eval(x),' and BR =',br.GetY()[i] )
    gNew = ROOT.TGraph(len(withElx),array('d',withElx), array('d',withEly))
    return gNew

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
        g.SetPointError(i, 0, abs((y1-y2))/2.)
        #print('Setting {} and {} +/- {} from {} and {}'.format(x1, (y1+y2)/2., abs((y1-y2))/2., y1, y2))
    return g

def makeUncFromMany(gs):
    lens = [g.GetN() for g in gs]
    if (max(lens) != min(lens)) or len(gs)==0:
        print ('makeUncFromMany mismatch',[(g.GetName(),g.GetN()) for g in gs])
        return
    N = gs[0].GetN()
    g = ROOT.TGraphErrors(N)
    for i in range(N):
        xs = [g.GetX()[i] for g in gs]
        ys = [g.GetY()[i] for g in gs]        
        if max(xs)-min(xs)>1e-6:
            print('makeUncFromMany mismatch!',i,' yields ',xs)
            return
        ymax = max(ys)
        ymin = min(ys)
        g.SetPoint(i, xs[0], (ymax+ymin)/2.)
        g.SetPointError(i, 0, (ymax-ymin)/2.)
        #print('Setting {} and {} +/- {} from {} and {}'.format(x1, (y1+y2)/2., abs((y1-y2))/2., y1, y2))
    return g

def splitErrGraph(gErr):
    N = gErr.GetN()
    xs = [gErr.GetX()[i] for i in range(N)]
    ys = [gErr.GetY()[i] for i in range(N)]
    us = [gErr.GetY()[i] + gErr.GetEY()[i] for i in range(N)]
    ds = [gErr.GetY()[i] - gErr.GetEY()[i] for i in range(N)]
    g   = ROOT.TGraph(N, array('d',xs), array('d',ys) )
    gUp = ROOT.TGraph(N, array('d',xs), array('d',us) )
    gDn = ROOT.TGraph(N, array('d',xs), array('d',ds) )
    return g, gUp, gDn

        
### systematics
class uncert(object):
    def __init__(self, name, isSF=True, forS=True, forB=True, sf=1, upName='', dnName=''):
        self.name = name
        self.isSF = isSF
        self.sf   = sf
        self.forS = forS
        self.forB = forB
        self.upName = upName
        self.dnName = dnName
