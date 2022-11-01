import pylhe
import ROOT
from array import array
import numpy as np

def convert(i, o, addLeps=True):
    o = ROOT.TFile(o,'recreate')
    t = ROOT.TTree('Events','')
    MAXLEN=20

    # output all gen particles
    n = array('i',[0])
    t.Branch("nGenPart" ,n ,"nGenPart/I" );
    
    vs=['pt','eta','phi','mass']
    arrs={ v: array('f', [0.]*MAXLEN) for v in vs }
    for v in vs:
        t.Branch("GenPart_"+v ,arrs[v] ,"GenPart_"+v+"[nGenPart]/F" );

    # non-float branches
    pdg = array('i', [0]*MAXLEN)
    t.Branch("GenPart_pdgId" ,pdg ,"GenPart_pdgId[nGenPart]/I" )
    status = array('i', [0]*MAXLEN)
    t.Branch("GenPart_status" ,status ,"GenPart_status[nGenPart]/I" )
    
    # output a collection of prompt leptons
    if addLeps:
        nLep = array('i',[0])
        t.Branch("nLep" ,nLep ,"nLep/I" );
    
        vsLep=['pt','eta','phi','mass']
        arrsLep={ v: array('f', [0.]*MAXLEN) for v in vs }
        for v in vsLep:
            t.Branch('Lep_'+v ,arrsLep[v] ,"Lep_"+v+"[nLep]/F" );

        # non-float branches
        pdgLep = array('i', [0]*MAXLEN)
        t.Branch("Lep_pdgId" ,pdgLep ,"Lep_pdgId[nLep]/I" )
        statusLep = array('i', [0]*MAXLEN)
        t.Branch("Lep_status" ,statusLep ,"Lep_status[nLep]/I" )
    
    events = pylhe.read_lhe(i)
    for e in events:
        n[0] = len(e.particles)
        # for i in range(len(pt)): pt.pop()
        # pt.fromlist( [0] * n[0] )
        # for i in range(n[0]): pt.fromarray( [0] * n[0] )
        
        nLep[0] = 0
        for i, p in enumerate(e.particles):
            v3 = ROOT.TVector3(p.px,p.py,p.pz)
            arrs['pt'][i] =  v3.Pt()
            arrs['eta'][i] = v3.Eta()
            arrs['phi'][i] = v3.Phi()
            arrs['mass'][i] = p.m
            pdg[i] = int(p.id)
            status[i] = int(p.status)
            
            if status[i] == 1 and (abs(pdg[i]) in [11,13]):
                arrsLep['pt'][ nLep[0] ]   = arrs['pt'][i]   
                arrsLep['eta'][ nLep[0] ]  = arrs['eta'][i] 
                arrsLep['phi'][ nLep[0] ]  = arrs['phi'][i] 
                arrsLep['mass'][ nLep[0] ] = arrs['mass'][i] 
                pdgLep[ nLep[0] ]          = pdg[i] 
                statusLep[ nLep[0] ]       = status[i] 
                nLep[0] += 1
            
        t.Fill()

    t.Write()
    o.Close()
