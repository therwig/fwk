void progress(float f){
    // https://stackoverflow.com/questions/14539867/how-to-display-a-progress-indicator-in-pure-c-c-cout-printf
    int barWidth = 70;
    std::cout << "[";
    int pos = barWidth * f;
    for (int i = 0; i < barWidth; ++i) {
        if (i < pos) std::cout << "=";
        else if (i == pos) std::cout << ">";
        else std::cout << " ";
    }
    std::cout << "] " << int(f * 100.0) << " %\r";
    std::cout.flush();    
}

void reco4L() {

   //Get old file, old tree and set top branch address
   TFile *oldfile = new TFile("data/root/ttz.root");
   TTree *oldtree = (TTree*)oldfile->Get("Events");
   Long64_t nentries = oldtree->GetEntries();

   /* TFile *newfile = new TFile("data/root/ttZ_reco.root","recreate"); */
   TFile *newfile = new TFile("data/root/ttZ4L.root","recreate");
   TTree *newtree = new TTree("Events","");
   const bool TopToMu = true;

   const int GMAX=200;
   int nGen = 0;
   float gen_Pt[GMAX];
   float gen_Eta[GMAX];
   float gen_Phi[GMAX];
   float gen_Mass[GMAX];
   int gen_pdg[GMAX];
   int gen_status[GMAX];
   int gen_nParents[GMAX];
   int gen_nChildren[GMAX];
   int gen_parentPdgId[GMAX];
   int gen_childPdgId[GMAX];
   int gen_childIdx[GMAX];
   int gen_parentIdx[GMAX];
      
   oldtree->SetBranchAddress<int>("nGenPart",        &nGen               );
   oldtree->SetBranchAddress("GenPart_pt",           &gen_Pt[0]          );
   oldtree->SetBranchAddress("GenPart_eta",          &gen_Eta[0]         );
   oldtree->SetBranchAddress("GenPart_phi",          &gen_Phi[0]         );
   oldtree->SetBranchAddress("GenPart_mass",         &gen_Mass[0]        );
   oldtree->SetBranchAddress("GenPart_pdgId"       , &gen_pdg[0]         );
   oldtree->SetBranchAddress("GenPart_status"      , &gen_status[0]      );
   oldtree->SetBranchAddress("GenPart_nParents"    , &gen_nParents[0]    );
   oldtree->SetBranchAddress("GenPart_nChildren"   , &gen_nChildren[0]   );
   oldtree->SetBranchAddress("GenPart_parentPdgId" , &gen_parentPdgId[0] );
   oldtree->SetBranchAddress("GenPart_childPdgId"  , &gen_childPdgId[0]  );
   oldtree->SetBranchAddress("GenPart_childIdx"    , &gen_childIdx[0]    );
   oldtree->SetBranchAddress("GenPart_parentIdx"   , &gen_parentIdx[0]   );

   newtree->Branch("nGenPart",             &nGen         , "nGenPart/I"                      );
   newtree->Branch("GenPart_pt",           &gen_Pt[0]    , "GenPart_pt[nGenPart]/F"          );
   newtree->Branch("GenPart_eta",          &gen_Eta[0]   , "GenPart_eta[nGenPart]/F"         );
   newtree->Branch("GenPart_phi",          &gen_Phi[0]   , "GenPart_phi[nGenPart]/F"         );
   newtree->Branch("GenPart_mass",         &gen_Mass[0]  , "GenPart_mass[nGenPart]/F"        );//
   newtree->Branch("GenPart_pdgId"       , &gen_pdg[0]         ,"GenPart_pdgId[nGenPart]/I" );
   newtree->Branch("GenPart_status"      , &gen_status[0]      ,"GenPart_status[nGenPart]/I" );
   newtree->Branch("GenPart_nParents"    , &gen_nParents[0]    ,"GenPart_nParents[nGenPart]/I" );
   newtree->Branch("GenPart_nChildren"   , &gen_nChildren[0]   ,"GenPart_nChildren[nGenPart]/I" );
   newtree->Branch("GenPart_parentPdgId" , &gen_parentPdgId[0] ,"GenPart_parentPdgId[nGenPart]/I" );
   newtree->Branch("GenPart_childPdgId"  , &gen_childPdgId[0]  ,"GenPart_childPdgId[nGenPart]/I" );
   newtree->Branch("GenPart_childIdx"    , &gen_childIdx[0]    ,"GenPart_childIdx[nGenPart]/I" );
   newtree->Branch("GenPart_parentIdx"   , &gen_parentIdx[0]   ,"GenPart_parentIdx[nGenPart]/I" );
   
   
   float genMet;
   float genMetPhi;
   float genHT;
   float genHTc;
   oldtree->SetBranchAddress<float>("GenMet", &genMet);
   oldtree->SetBranchAddress<float>("GenMetPhi", &genMetPhi);
   oldtree->SetBranchAddress<float>("GenHT", &genHT);
   oldtree->SetBranchAddress<float>("GenHTc", &genHTc);
   newtree->Branch<float>("GenMet", &genMet);
   newtree->Branch<float>("GenMetPhi", &genMetPhi);
   newtree->Branch<float>("GenHT", &genHT);
   newtree->Branch<float>("GenHTc", &genHTc);

   const int MAX=40;
   int nLep = 0;
   float lepPt[MAX];
   float lepEta[MAX];
   float lepPhi[MAX];
   float lepMass[MAX];
   int lepPdg[MAX];
   int lepPPdg[MAX];
   int lepGPdg[MAX];
   int lepStatus[MAX];
   oldtree->SetBranchAddress<int>("nLep", &nLep);
   oldtree->SetBranchAddress("Lep_pt", &lepPt[0]);
   oldtree->SetBranchAddress("Lep_eta", &lepEta[0]);
   oldtree->SetBranchAddress("Lep_phi", &lepPhi[0]);
   oldtree->SetBranchAddress("Lep_mass", &lepMass[0]);
   oldtree->SetBranchAddress("Lep_status", &lepStatus[0]);
   oldtree->SetBranchAddress("Lep_pdgId", &lepPdg[0]);
   oldtree->SetBranchAddress("Lep_parentPdgId", &lepPPdg[0]);
   oldtree->SetBranchAddress("Lep_gparentPdgId", &lepGPdg[0]);

   int nNew = 0;
   float newPt[MAX];
   float newEta[MAX];
   float newPhi[MAX];
   float newMass[MAX];
   int newPdg[MAX];
   int newPPdg[MAX];
   int newGPdg[MAX];
   int newStatus[MAX];
   newtree->Branch("nLep",             &nNew        , "nLep/I"                  );
   newtree->Branch("Lep_pt",           &newPt[0]    , "Lep_pt[nLep]/F"          );
   newtree->Branch("Lep_eta",          &newEta[0]   , "Lep_eta[nLep]/F"         );
   newtree->Branch("Lep_phi",          &newPhi[0]   , "Lep_phi[nLep]/F"         );
   newtree->Branch("Lep_mass",         &newMass[0]  , "Lep_mass[nLep]/F"        );
   newtree->Branch("Lep_status",       &newStatus[0], "Lep_status[nLep]/I"      );
   newtree->Branch("Lep_pdgId",        &newPdg[0]   , "Lep_pdgId[nLep]/I"       );
   newtree->Branch("Lep_parentPdgId",  &newPPdg[0]  , "Lep_parentPdgId[nLep]/I" );
   newtree->Branch("Lep_gparentPdgId", &newGPdg[0]  , "Lep_gparentPdgId[nLep]/I");

   int nReco=0;
   newtree->Branch("nReco", &nReco, "nReco/I");
   
   /* TLorentzVector el1, el2, mu, nu; */
   /* const float ME=0.0005; */
   /* const float MMU=0.105; */
   for (Long64_t i=0;i<nentries; i++) {
      oldtree->GetEntry(i);
      // count the number of reconstructable leptons
      nReco=0;
      for(int j=0;j<nLep;j++){
        if(TopToMu && abs(lepPPdg[j])==24 && abs(lepPdg[j])==11)
          lepPdg[j] = lepPdg[j]>0 ? 13 : -13;
        if(abs(lepPdg[j])==13 && fabs(lepEta[j])<2.5) nReco++;
      }
      // transform every 4L event into a "3L event"
      // 0L: can drop either muon, since none will pass selection
      // 1L: keep reco muon. (could add missing muon to the MET, but its never used)
      // 2L: keep a random muon (will scale down by track inefficiency)
      
      /* nNew=nLep; */
      nNew=0;
      for(int j=0;j<nLep;j++){
        if(nReco==0 && lepPdg[j]==13) continue; // skip mu- 
        if(nReco==1 && abs(lepPdg[j])==13 && fabs(lepEta[j])>2.5) continue; // skip fwd mu
        if(nReco==2 && abs(lepPdg[j])==13 && (i%2 ? lepPdg[j] : -lepPdg[j])>0 ) continue; // skip mu- for even events, mu+ for odd
        newPt[nNew]     = lepPt[j]    ;
        newEta[nNew]    = lepEta[j]   ;
        newPhi[nNew]    = lepPhi[j]   ;
        newMass[nNew]   = lepMass[j]  ;
        newStatus[nNew] = lepStatus[j];
        newPdg[nNew]    = lepPdg[j]   ;
        newPPdg[nNew]   = lepPPdg[j]  ;
        newGPdg[nNew]   = lepGPdg[j]  ;
        nNew++;
      }
      if (i%100==0) progress(float(i)/nentries);
      if(nReco==2) newtree->Fill();
      // newtree->Fill();
   }
   cout << endl;
   //newtree->Print();
   newtree->AutoSave();
   delete oldfile;
   delete newfile;
}
