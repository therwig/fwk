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

void skimW() {

   //Get old file, old tree and set top branch address
   TFile *oldfile = new TFile("data/root/bSplit.root");
   TTree *oldtree = (TTree*)oldfile->Get("Events");
   Long64_t nentries = oldtree->GetEntries();

   const int MAX=200;
   
   int nGenPart = 0;
   float genPt[MAX];
   float genEta[MAX];
   float genPhi[MAX];
   int genPdg[MAX];
   oldtree->SetBranchAddress<int>("nGenPart", &nGenPart);
   oldtree->SetBranchAddress("GenPart_pt", &genPt[0]);
   oldtree->SetBranchAddress("GenPart_eta", &genEta[0]);
   oldtree->SetBranchAddress("GenPart_phi", &genPhi[0]);
   oldtree->SetBranchAddress("GenPart_pdgId", &genPdg[0]);

   int nLepPart = 0;
   float lepPt[MAX];
   float lepEta[MAX];
   float lepPhi[MAX];
   int lepPdg[MAX];
   oldtree->SetBranchAddress<int>("nLep", &nLepPart);
   oldtree->SetBranchAddress("Lep_pt", &lepPt[0]);
   oldtree->SetBranchAddress("Lep_eta", &lepEta[0]);
   oldtree->SetBranchAddress("Lep_phi", &lepPhi[0]);
   oldtree->SetBranchAddress("Lep_pdgId", &lepPdg[0]);
   
   //Create a new file + a clone of old tree in new file
   TFile *newfile = new TFile("skim.root","recreate");
   TTree *newtree = oldtree->CloneTree(0);

   TLorentzVector el1, el2, mu, nu;
   const float ME=0.0005;
   const float MMU=0.105;
   for (Long64_t i=0;i<nentries; i++) {
      oldtree->GetEntry(i);
      
      // Neutrino loop
      int iNu=-1; 
      for(int j=0;j<nGenPart;j++){
        if (abs(genPdg[j])!=14) continue;
        if (iNu>=0 && genPt[j] < genPt[iNu]) continue;
        iNu=j;
      }
      if (iNu<0){
        cout << "missed neutrino" << endl;
        break;
      }
        // cout << " " << iNu << " " << genPt[iNu] << " " << genPdg[iNu] << endl;
      
      // Lepton loop
      int iMu=-1; 
      int iEl1=-1; 
      int iEl2=-1; 
      for(int j=0;j<nLepPart;j++){ // these are already reduced to 1 ea.
        if (abs(lepPdg[j])==13) iMu = j;
        if (lepPdg[j]== 11) iEl1 = j;
        if (lepPdg[j]==-11) iEl2 = j;
      }
      if (iMu<0 || iEl1<0 || iEl2<0){
        cout << "missed lepton" << endl;
        break;
      }
      nu.SetPtEtaPhiM(genPt[iNu], genEta[iNu], genPhi[iNu], 0);
      mu.SetPtEtaPhiM(lepPt[iMu], lepEta[iMu], lepPhi[iMu], MMU);
      el1.SetPtEtaPhiM(lepPt[iEl1], lepEta[iEl1], lepPhi[iEl1], ME);
      el2.SetPtEtaPhiM(lepPt[iEl2], lepEta[iEl2], lepPhi[iEl2], ME);
      /* cout << (mu+nu).M() << " and " << (mu+nu+el1+el2).M() << endl; */
      if ( (mu+nu).M() + (mu+nu+el1+el2).M() < 156.6 ) newtree->Fill();
      /* if (i>10) break; */
      /* if (met > 100) newtree->Fill(); */
      //if (i < 10) cout << met << endl;
      if (i%100==0) progress(float(i)/nentries);
   }
   cout << endl;
   //newtree->Print();
   newtree->AutoSave();
   delete oldfile;
   delete newfile;
}
