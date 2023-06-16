import ROOT
from numpy import hypot
from collections import OrderedDict

class HistHelper:
    def __init__(self):
        self.d = OrderedDict()
    # booking
    def book(self, name,title,n,a,b):
        self.d[name]=ROOT.TH1D(name,title,n,a,b)
        self.d[name].Sumw2()
        # self.d[name].SetDirectory(0)
    def bookBins(self, name,title,bins):
        self.d[name]=ROOT.TH1D(name,title,len(bins)-1,bins)
        self.d[name].Sumw2()
        # self.d[name].SetDirectory(0)
    def book2d(self, name,title,n,a,b,nn,aa,bb):
        self.d[name]=ROOT.TH2D(name,title,n,a,b,nn,aa,bb)
        self.d[name].Sumw2()
    def bookProf(self, name,title,n,a,b,lo=0,hi=1):
        self.d[name]=ROOT.TProfile(name,title,n,a,b,lo,hi)
        # self.d[name].SetDirectory(0)
    def load(self, histfile, name):
        self.d[name] = histfile.Get(name)
        self.d[name].SetDirectory(0)
    # filling
    def fill(self, name, *args): self.d[name].Fill(*args)
    # access
    def __getitem__(self, key):
        return self.d[key]
    def __setitem__(self, key, value):
        self.d[key] = value
    # def __getattr__(self, name)
    
    # reformatting
    def addBin(self, h, x1, x2):
        h.SetBinContent(x1, h.GetBinContent(x1) + h.GetBinContent(x2))
        h.SetBinError(x1, hypot(h.GetBinError(x1), h.GetBinError(x2)))
        h.SetBinContent(x2, 0)
        h.SetBinError(x2, 0)
    def addBin2d(self, h,  x1,  y1,  x2,  y2):
        h.SetBinContent(x1,y1, h.GetBinContent(x1,y1) + h.GetBinContent(x2,y2))
        h.SetBinError(x1,y1, hypot(h.GetBinError(x1,y1), h.GetBinError(x2,y2)))
        h.SetBinContent(x2,y2, 0)
        h.SetBinError(x2,y2, 0)
    def removeOverflow(self, h):
        self.add_bin(h, 1, 0)
        self.add_bin(h, h.GetNbinsX(), h.GetNbinsX()+1)
    def removeOverflow2d(self, h):
        for binx in range(h.GetNbinsX()+2):
            self.add_bin(h, binx, h.GetNbinsY(), binx, h.GetNbinsY()+1)
            self.add_bin(h, binx, 1, binx, 0)
        for biny in range(h.GetNbinsY()+2):
            self.add_bin(h, h.GetNbinsX(), biny, h.GetNbinsX()+1, biny)
            self.add_bin(h, 1, biny, 0, biny)
