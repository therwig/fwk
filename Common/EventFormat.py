import pylhe, pyhepmc, ROOT
# from particle.pdgid import is_hadron, charge
from particle import pdgid
from array import array
import numpy as np

def convert(i, o, addLeps=True, maxEvents=-1, doSkim=False):
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
    for ie, e in enumerate(events):
        if maxEvents>=0 and ie >= maxEvents: break
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

def convertHepMC(i, o, addLeps=True, maxEvents=-1, doSkim=False):
    o = ROOT.TFile(o,'recreate')
    t = ROOT.TTree('Events','')
    MAXLEN=5000

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
    nParents = array('i', [0]*MAXLEN)
    t.Branch("GenPart_nParents" ,nParents ,"GenPart_nParents[nGenPart]/I" )
    nChildren = array('i', [0]*MAXLEN)
    t.Branch("GenPart_nChildren" ,nChildren ,"GenPart_nChildren[nGenPart]/I" )
    parentPdgId = array('i', [0]*MAXLEN)
    t.Branch("GenPart_parentPdgId" ,parentPdgId ,"GenPart_parentPdgId[nGenPart]/I" )
    childPdgId = array('i', [0]*MAXLEN)
    t.Branch("GenPart_childPdgId" ,childPdgId ,"GenPart_childPdgId[nGenPart]/I" )
    childIdx = array('i', [0]*MAXLEN)
    t.Branch("GenPart_childIdx" ,childIdx ,"GenPart_childIdx[nGenPart]/I" )
    parentIdx = array('i', [0]*MAXLEN)
    t.Branch("GenPart_parentIdx" ,parentIdx ,"GenPart_parentIdx[nGenPart]/I" )

    # gen met
    met = array('f',[0])
    metPhi = array('f',[0])
    ht = array('f',[0])
    htc = array('f',[0]) # charged
    # htPhi = array('f',[0])
    # htcPhi = array('f',[0])
    t.Branch("GenMet", met, "GenMet/F" );
    t.Branch("GenMetPhi", metPhi, "GenMetPhi/F" );
    t.Branch("GenHT", ht, "GenHT/F" );
    t.Branch("GenHTc", htc, "GenHTc/F" );
    # t.Branch("GenHTPhi", htPhi, "GenHTPhi/F" );
    # t.Branch("GenHTcPhi", htcPhi, "GenHTPhi/F" );
    
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
        parentLep = array('i', [0]*MAXLEN)
        t.Branch("Lep_parentPdgId", parentLep ,"Lep_parentPdgId[nLep]/I" )
        gparentLep = array('i', [0]*MAXLEN)
        t.Branch("Lep_gparentPdgId", gparentLep ,"Lep_gparentPdgId[nLep]/I" )
    
    events = pyhepmc.open(i)
    
    for ie, e in enumerate(events):
        if maxEvents>=0 and ie >= maxEvents: break
        passSkim=False
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
        ht[0]=0
        htc[0]=0
        # htx=0
        # hty=0
        # htcx=0
        # htcy=0
        id2idx={}
        # print( len(e.particles) )
        for idx, p in enumerate(e.particles):
            id2idx[p.id]=idx
        for p in e.particles:
            # if abs(p.pid) in [12,14,16] and p.status==1:
            if p.status==1:
                if abs(p.pid) in [12,14,16]:
                    metx += p.momentum[0]
                    mety += p.momentum[1]
                elif pdgid.is_hadron(p.pid) or p.pid==22: #get photons from pi0
                    v3 = ROOT.TVector3(p.momentum[0],p.momentum[1],p.momentum[2])
                    if abs(v3.Eta()) < 2.5:
                        if p.pid==22:
                            if v3.Pt() > 5: # em threshold
                                ht[0] += v3.Pt()
                                # htx += p.momentum[0]
                                # hty += p.momentum[1]                            
                        elif pdgid.charge(p.pid):
                            if v3.Pt() > 2: # chg threshold
                                ht[0] += v3.Pt()
                                htc[0] += v3.Pt()
                                # htx += p.momentum[0]
                                # hty += p.momentum[1]
                                # htcx += p.momentum[0]
                                # htcy += p.momentum[1]
                        else:
                            if v3.Pt() > 10: # neutral hadron threshold
                                ht[0] += v3.Pt()
                                # htx += p.momentum[0]
                                # hty += p.momentum[1]
                #continue
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
            nParents[ n[0] ] = int(len(p.parents))
            nChildren[ n[0] ] = int(len(p.children))
            parentPdgId[ n[0] ] = p.parents[0].pid if len(p.parents) else 0
            childPdgId[ n[0] ] = p.children[0].pid if len(p.children) else 0
            parentIdx[ n[0] ] = id2idx[p.parents[0].id] if len(p.parents) else 0
            childIdx[ n[0] ] = id2idx[p.children[0].id] if len(p.children) else 0
            
            if status[ n[0] ] == 1 and (abs(pdg[ n[0] ]) in [11,13]):
                # check for ancestor
                parents = p.parents
                while len(parents)==1 and parents[0].pid == p.pid:
                    parents = parents[0].parents
                parents_ids = [abs(x.pid) for x in parents]
                #if abs(p.pid)==11: print('   - Found parents', parents_ids)
                good_ancestor=0
                for x in [1,2,3,4,5,21,22,23,24,32,74]: # must include quarks, gluons to pickup the hard process
                    if x in parents_ids:
                        good_ancestor = x
                        break
                #if abs(p.pid)==11: print('   - ancestor', good_ancestor)
                good_ancestor2 = 0
                if len(parents):
                    parent = parents[0]
                    gparents = parent.parents
                    while len(gparents)==1 and gparents[0].pid == p.pid:
                        gparents = gparents[0].parents
                    gparents_ids = [abs(x.pid) for x in gparents]
                    for x in [1,2,3,4,5,22,23,24,32,74]: # must include quarks to pickup the hard process
                        if x in gparents_ids:
                            good_ancestor2 = x
                            break
                if good_ancestor:
                    arrsLep['pt'][ nLep[0] ]   = arrs['pt'][ n[0] ]   
                    arrsLep['eta'][ nLep[0] ]  = arrs['eta'][ n[0] ] 
                    arrsLep['phi'][ nLep[0] ]  = arrs['phi'][ n[0] ] 
                    arrsLep['mass'][ nLep[0] ] = arrs['mass'][ n[0] ] 
                    pdgLep[ nLep[0] ]          = pdg[ n[0] ] 
                    statusLep[ nLep[0] ]       = status[ n[0] ] 
                    parentLep[ nLep[0] ]       = good_ancestor
                    gparentLep[ nLep[0] ]      = good_ancestor2
                    nLep[0] += 1
                # else:
                #     print(parents_ids)
            n[0] += 1
            if n[0] >= MAXLEN:
                print ('warning, truncating particles from event in HepMC EventFormat!')
                break
        metVec = ROOT.TVector3(metx,mety,0)
        met[0] = metVec.Pt()
        metPhi[0] = metVec.Phi()
        # htVec = ROOT.TVector3(htx,hty,0)
        # ht[0] = htVec.Pt()
        # htPhi[0] = htVec.Phi()
        # htcVec = ROOT.TVector3(htcx,htcy,0)
        # htc[0] = htcVec.Pt()
        # htcPhi[0] = htcVec.Phi()
        passSkim = (nLep[0]==3) and (11 in pdgLep[:3]) and (-11 in pdgLep[:3]) and ((13 in pdgLep[:3]) or (-13 in pdgLep[:3]))
        if (not doSkim) or passSkim:
            t.Fill()

    t.Write()
    o.Close()

# temporary test
# convertHepMC('tag_1_pythia8_events.hepmc.gz','tag_1_pythia8_events.root')
