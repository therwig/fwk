#!/usr/bin/env python3
import ROOT, argparse, os
import numpy as np
from cfg.samples import sig_pairs, sig_tags
from plotUtils import *

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--train", action="store_true", default=False, help="Train the BDT")
parser.add_argument("--test", action="store_true", default=False, help="Test the BDT performance")
parser.add_argument("--friends", action="store_true", default=False, help="write the friends")
parser.add_argument("--tag", default='', help="BDT tag to save or load")
parser.add_argument("--signals", default=None, help="Comma-separated list of signal points to run")
parser.add_argument("--doBackground", action="store_true", default=False, help="Convert the background")
args = parser.parse_args()

good_pairs = sig_pairs
if not (args.signals is None):
    good_pairs = [p for p in sig_pairs if sig_tags[p] in args.signals.split(',')]

variables = ["dPhi_ee","dPhi_ee_mu","dR_ee",
             "el1_eta","el1_pt","el2_eta","el2_pt","m_ee_mu",
             # "met","minPtFrac_ee",
             "mtEE","mtMu",
             "mu_eta","mu_pt","pt3L","pt_ee",]

# just thinking about this more when writing the draft
variables2 = [
    "el1_eta","el1_pt","el2_eta","el2_pt",
    "mu_eta","mu_pt",
    "dPhi_ee","dPhi_ee_mu",
    "pt3L","m_ee_mu"]

def prep(df):
    return df.Filter("el2_pt>1 && mu_pt>25", "trigger") 
# def prep(df):
#     return df.Filter("el2_pt>1 && mu_pt>25", "trigger")
    # return df.Filter("el2_pt>1 && mu_pt>25 && (el2_pt*10000-el2_pt*1000)<5", "trigger")

# def subset(shaped_data, frac=0.5):
#     N = round(len(shaped_data)*frac)
#     idx1 = np.random.choice(shaped_data.shape[0], N, replace=False)
#     full_idx = np.array(range(0,len(shaped_data)))
#     idx2 = np.logical_not(np.in1d(full_idx,idx1))
#     return shaped_data[idx1], shaped_data[idx2]

def getTrainData(frac=0):
    data_sig = ROOT.RDataFrame("Friends", "data/friends/outS_*.root")
    data_bkg = ROOT.RDataFrame("Friends", "data/friends/bSplit.root")

    data_sig = prep(data_sig).AsNumpy()
    data_bkg = prep(data_bkg).AsNumpy()
    
    x_sig = np.vstack([data_sig[var] for var in variables]).T
    x_bkg = np.vstack([data_bkg[var] for var in variables]).T
    x = np.vstack([x_sig, x_bkg])


    num_sig = x_sig.shape[0]
    num_bkg = x_bkg.shape[0]
    y = np.hstack([np.ones(num_sig), np.zeros(num_bkg)])

    num_all = num_sig + num_bkg
    w = np.hstack([np.ones(num_sig) * num_all / num_sig, np.ones(num_bkg) * num_all / num_bkg])
    
    # optionally select a subset of the data here
    xTrain, yTrain, wTrain = x, y, w
    xValid, yValid, wValid = None, None, None
    if frac>0:
        N = round(len(x)*frac)
        idx1 = np.random.choice(x.shape[0], N, replace=False)
        full_idx = np.array(range(0,len(x)))
        idx2 = np.logical_not(np.in1d(full_idx,idx1)) # for later?
        xTrain = x[idx1]
        yTrain = y[idx1]
        wTrain = w[idx1]
        xValid = x[idx2]
        yValid = y[idx2]
        wValid = w[idx2]
        
    return xTrain, yTrain, wTrain, xValid, yValid, wValid

# def getTestData(fname=''):
#     data = ROOT.RDataFrame("Friends", fname)
#     data = prep(data).AsNumpy()        
#     x = np.vstack([data[var] for var in variables]).T
#     return x

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
bdt = XGBClassifier()

if args.train:
    # x, y, w = getTrainData() #0.5)
    x, y, w, xValid, yValid, wValid = getTrainData(0.2)

    import timeit
    startTime = timeit.default_timer()
    # bdt = XGBClassifier(max_depth=3, n_estimators=500) #A (114 (133) sec with 1 (4) jobs). 250 in 
    # bdt = XGBClassifier(max_depth=3, n_estimators=250) #A' (63 sec with 1 job).
    # bdt = XGBClassifier(max_depth=6, n_estimators=250) #A'' (118 sec)
    # bdt = XGBClassifier(max_depth=10, n_estimators=1000) #B 689 sec
    # bdt = XGBClassifier(max_depth=10, n_estimators=1000, learning_rate=0.1) #C 711 sec
    # X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=7)
    
    metrics=["error", "logloss","rmse","mae","auc"] # early stopping uses last in the list
    bdt = XGBClassifier(max_depth=10, n_estimators=1000, eval_metric=metrics, early_stopping_rounds=10, learning_rate=0.1)
    eval_set = [(x,y),(xValid, yValid)]
    bdt.fit(x, y, sample_weight=w, eval_set=eval_set, verbose=True) #, sample_weight=w)
    # bdt.fit(x, y, sample_weight=w)
    stopTime = timeit.default_timer()
    print("Training done on ",x.shape[0], "events in ", stopTime-startTime," seconds")

    
# plotGraphs('yields_zd', [gsets['mND10'][x] for x in gsets['mND10']],
#            xtitle='m(Z_{d}) [MeV]', ytitle='Events',
#            legcoors=(0.7,0.6,0.88,0.9),
#            xlims=None, legcols=1,
#            logy=True, logx=True, colz=None, styz=None, dopt='AL*', pdir=pdir)
#     mg = TMultiGraph()
#     mg.Add(gTrain)
#     mg.Add(gValid)
#     c = ROOT.TCanvas()
#     mg.Draw()
    # x_axis = range(0, epochs)
    # from matplotlib import pyplot
    # fig, ax = pyplot.subplots()
    # ax.plot(x_axis, results['validation_0']['logloss'], label='Train')
    # ax.plot(x_axis, results['validation_1']['logloss'], label='Test')
    # ax.legend()
    # pyplot.ylabel('Log Loss')
    # pyplot.title('XGBoost Log Loss')
    # pyplot.savefig('XGBoost Log Loss')

    saveName = 'myBDT_'+args.tag+'.json'
    saveIt = not os.path.exists(saveName)
    if not saveIt:
        ans = input("Are you sure you'd like to overwrite existing model with the same tag? y/[n]")
        if len(ans) and ans.lower()[0]=='y': saveIt = True
    
    if saveIt:
        bdt.save_model('models/myBDT_'+args.tag+'.json')
        # some diagnostics
        from array import array
        results = bdt.evals_result()
        n = len(results['validation_0']['error']) # n epochs
        for x in results: print(x)
        # print (results['validation_0']['logloss'])
        # print (np.array(results['validation_0']['logloss']))
        pdir='models/diagnostics/'
        for im, met in enumerate(metrics):
            gTrain = ROOT.TGraph(n,array('d',range(n)),array('d',results['validation_0'][met]))
            gValid = ROOT.TGraph(n,array('d',range(n)),array('d',results['validation_1'][met]))
            plotGraphs('myBDT_'+args.tag+'_'+met, [gTrain, gValid], labs=['train','test'], pdir=pdir,
                       xtitle='epochs', ytitle=met,dopt='AL*')
        # gTrain = ROOT.TGraph(n,array('d',range(n)),array('d',results['validation_0']['error']))
        # gValid = ROOT.TGraph(n,array('d',range(n)),array('d',results['validation_1']['error']))
        # plotGraphs('myBDT_'+args.tag+'_error', [gTrain, gValid], labs=['train','test'], pdir=pdir,
        #            xtitle='epochs', ytitle='classification error',dopt='AL*')

def makeFriends(ifname):
    df = ROOT.RDataFrame("Friends", ifname).AsNumpy() # NO PREP!!
    x = np.vstack([df[var] for var in variables]).T
    bdt.load_model('models/myBDT_'+args.tag+'.json')
    y_pred = bdt.predict(x, output_margin=True)
    print(df['dPhi_ee'].shape, y_pred.shape)
    
    os.system('mkdir -p data/bdt/'+args.tag)
    ofname = ifname.replace('/friends/','/bdt/'+args.tag+'/') #.replace('.root','_'+args.tag+'.root')
    # ofile = ROOT.TFile.Open(ofname,'recreate')
    # odf = ROOT.RDF.FromNumpy({"bdt": y_pred,})
    odf = ROOT.RDF.MakeNumpyDataFrame({"bdt": y_pred,})
    odf.Snapshot('Friends',ofname)
    
if args.friends:
    sig_files = ["data/friends/outS_{}.root".format(sig_tags[p]) for p in good_pairs]
    all_files = sig_files + (['data/friends/bSplit.root'] if args.doBackground else [])
    for fn in all_files: makeFriends(fn)

if args.test:
    procTags_mZD0p03 = [sig_tags[p] for p in sig_pairs if p[0]=='0p03'];
    procTags_mND10 = [sig_tags[p] for p in sig_pairs if p[1]=='10'];

    for scanName, tagSet in [('scanN',procTags_mZD0p03),('scanZ',procTags_mND10)]:
        
        fo = ROOT.TFile("test_"+scanName+".root", "recreate")
        hs = {tag : ROOT.TH1F("h_"+tag,";BDT score",60,-40,20) for tag in tagSet}
            
        for tag in tagSet:
            # print (fname)
            f = ROOT.TFile("data/bdt/{}/outS_{}.root".format(args.tag,tag))
            t = f.Get('Friends')
            # h = ROOT.TH1F("h_"+tag,";BDT score",60,-40,20)
            t.Draw("bdt>>h_"+tag)
            # h.SetDirectory(f)
            # fo.cd()
            # f.cd()
            # hs[tag].Write()
            # hs += [ROOT.gDirectory.Get('h1').Clone(tag)]
            # print(ROOT.gDirectory.Get('h1').Integral())
            # print(t.GetEntries(), hbdt.Integral())
            # print(h.Integral())
            # h.SetDirectory(0)
            # hs += [h]
            # hs += [hbdt.Clone(tag)]
            # hs[-1].SetDirectory(0)
            f.Close()
        # plot("test_"+scanName+".pdf",hs,pdir='data/bdt/'+args.tag, rescale=None,labs=[tag for tag in tagSet])
        fo.cd()
        fo.Write()
        fo.Close()

if False:
    bdt.load_model('myBDT_'+args.tag+'.json')
    y_pred = bdt.predict(x)
    
    from sklearn.metrics import roc_curve, auc
    fpr, tpr, _ = roc_curve(y, y_pred, sample_weight=w)
    score = auc(fpr, tpr)
    
    # Plot ROC
    c = ROOT.TCanvas("roc", "", 600, 600)
    g = ROOT.TGraph(len(fpr), fpr, tpr)
    g.SetTitle("AUC = {:.2f}".format(score))
    g.SetLineWidth(3)
    g.SetLineColor(ROOT.kRed)
    g.Draw("AC")
    g.GetXaxis().SetRangeUser(0, 1)
    g.GetYaxis().SetRangeUser(0, 1)
    g.GetXaxis().SetTitle("False-positive rate")
    g.GetYaxis().SetTitle("True-positive rate")
    c.Draw()
    c.SaveAs('bdtTestResults.pdf')
    
