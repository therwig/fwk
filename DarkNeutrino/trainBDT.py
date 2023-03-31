import ROOT
import numpy as np
from cfg.samples import sig_pairs, sig_tags

# data_sig = ROOT.RDataFrame("Events", "data/root/outS_mZD3_mND10.root").AsNumpy()

tag='230225'

# from tmva101_Training.py
print('load trees')
# data_sig = ROOT.RDataFrame("Events", "data/root/outS_*.root")
# data_bkg = ROOT.RDataFrame("Events", "data/root/bSplit.root")
data_sig = ROOT.RDataFrame("Friends", "data/friends/outS_*.root")
data_bkg = ROOT.RDataFrame("Friends", "data/friends/bSplit.root")
print('loaded trees')

def prep(df):
    return df.Filter("el2_pt>1 && mu_pt>25", "trigger") 
    # return df.Filter("nLep>2", "three lep")\
    # .Define("Lep_pt_1", "Lep_pt[0]")\
    # .Define("Lep_pt_2", "Lep_pt[1]")\
    # .Define("Lep_pt_3", "Lep_pt[2]")

# for df in [data_sig,data_bkg]:
    # df = df.Filter("nLep>2", "three lep")
    # df = df.Define("Lep_pt_1", "Lep_pt[0]")
    # df = df.Define("Lep_pt_2", "Lep_pt[1]")
    # df = df.Define("Lep_pt_3", "Lep_pt[2]")
    
data_sig = prep(data_sig).AsNumpy()
data_bkg = prep(data_bkg).AsNumpy()

variables = ["dPhi_ee","dPhi_ee_mu","dR_ee",
             "el1_eta","el1_pt","el2_eta","el2_pt","m_ee_mu",
             # "met","minPtFrac_ee",
             "mtEE","mtMu",
             "mu_eta","mu_pt","pt3L","pt_ee",]

# variables = ["GenMet", "GenMetPhi", "Lep_pt_1", "Lep_pt_2","Lep_pt_3"]
x_sig = np.vstack([data_sig[var] for var in variables]).T
x_bkg = np.vstack([data_bkg[var] for var in variables]).T
x = np.vstack([x_sig, x_bkg])

num_sig = x_sig.shape[0]
num_bkg = x_bkg.shape[0]
y = np.hstack([np.ones(num_sig), np.zeros(num_bkg)])

num_all = num_sig + num_bkg
w = np.hstack([np.ones(num_sig) * num_all / num_sig, np.ones(num_bkg) * num_all / num_bkg])

# Fit xgboost model
print('start xgb')
from xgboost import XGBClassifier
bdt = XGBClassifier(max_depth=3, n_estimators=500)
bdt.fit(x, y, sample_weight=w)

print("Training done on ",x.shape[0],"events. Saving model")
bdt.save_model('myBDT_'+tag+'.json')
#ROOT.TMVA.Experimental.SaveXGBoost(bdt, "myBDT", "tmva101.root", num_inputs=x.shape[1])
