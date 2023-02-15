import pylhe, pyhepmc, ROOT
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

def convertHepMC(i, o, addLeps=True):
    o = ROOT.TFile(o,'recreate')
    t = ROOT.TTree('Events','')
    MAXLEN=100

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

    # gen met
    met = array('f',[0])
    metPhi = array('f',[0])
    t.Branch("GenMet" ,met ,"GenMet/F" );
    t.Branch("GenMetPhi" ,metPhi ,"GenMetPhi/F" );
    
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
    
    events = pyhepmc.open(i)
    
    for e in events:
        # print( [p for p in e.particles if abs(p.pid) in [11,13] and p.status==1] )
        # exit(0)
        # n[0] = len(e.particles)
        # for i in range(len(pt)): pt.pop()
        # pt.fromlist( [0] * n[0] )
        # for i in range(n[0]): pt.fromarray( [0] * n[0] )
        
        n[0] = 0
        nLep[0] = 0
        # for i, p in enumerate(e.particles):
        metx=0
        mety=0
        for p in e.particles:
            if abs(p.pid) in [12,14,16] and p.status==1:
                metx += p.momentum[0]
                mety += p.momentum[1]
                continue
            if not abs(p.pid) in [11,13,14,23,24,32,74]: continue # leptons, bosons, Zd, Nd
            if p.pid in [q.pid for q in p.children]: continue # last copy
            if (abs(p.pid) in [11,13,14]) and p.status!=1: continue
            
            v3 = ROOT.TVector3(p.momentum[0],p.momentum[1],p.momentum[2])
            # print ( n[0] , arrs['pt'])
            arrs['pt'][ n[0] ] =  v3.Pt()
            arrs['eta'][ n[0] ] = v3.Eta()
            arrs['phi'][ n[0] ] = v3.Phi()
            arrs['mass'][ n[0] ] = p.generated_mass
            pdg[ n[0] ] = int(p.pid)
            status[ n[0] ] = int(p.status)
            
            if status[ n[0] ] == 1 and (abs(pdg[ n[0] ]) in [11,13]):
                # check for ancestor
                parents = p.parents
                while len(parents)==1 and parents[0].pid == p.pid:
                    parents = parents[0].parents
                parents_ids = [abs(x.pid) for x in parents]
                good_ancestor=False
                for x in [23,24,32,74]:
                    if x in parents_ids:
                        good_ancestor = True
                        break
                if not good_ancestor: continue
                    
                arrsLep['pt'][ nLep[0] ]   = arrs['pt'][ n[0] ]   
                arrsLep['eta'][ nLep[0] ]  = arrs['eta'][ n[0] ] 
                arrsLep['phi'][ nLep[0] ]  = arrs['phi'][ n[0] ] 
                arrsLep['mass'][ nLep[0] ] = arrs['mass'][ n[0] ] 
                pdgLep[ nLep[0] ]          = pdg[ n[0] ] 
                statusLep[ nLep[0] ]       = status[ n[0] ] 
                nLep[0] += 1
            n[0] += 1
            if n[0] >= MAXLEN:
                print ('warning, truncating particles from event in HepMC EventFormat!')
                break
        metVec = ROOT.TVector3(metx,mety,0)
        met[0] = metVec.Pt()
        metPhi[0] = metVec.Phi()
        t.Fill()

    t.Write()
    o.Close()

# temporary test
# convertHepMC('tag_1_pythia8_events.hepmc.gz','tag_1_pythia8_events.root')
