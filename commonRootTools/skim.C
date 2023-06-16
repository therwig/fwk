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

void skim() {

   //Get old file, old tree and set top branch address
   TFile *oldfile = new TFile("nanoAOD.root");
   TTree *oldtree = (TTree*)oldfile->Get("Events");
   Long64_t nentries = oldtree->GetEntries();

   float met = 0;
   oldtree->SetBranchAddress("GenMET_pt",&met);

   //Create a new file + a clone of old tree in new file
   TFile *newfile = new TFile("skim.root","recreate");
   TTree *newtree = oldtree->CloneTree(0);

   for (Long64_t i=0;i<nentries; i++) {
      oldtree->GetEntry(i);
      if (met > 100) newtree->Fill();
      //if (i < 10) cout << met << endl;
      if (i%100==0) progress(float(i)/nentries);
   }
   cout << endl;
   //newtree->Print();
   newtree->AutoSave();
   delete oldfile;
   delete newfile;
}
