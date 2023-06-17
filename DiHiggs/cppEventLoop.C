void cppEventLoop(TString fname="data/GluGluToHHTo4B_node_cHHH0.skim.root"){

  // declare the input file and input data
  TFile f(fname);
  TTreeReader reader("Events", &f);
  TTreeReaderValue<unsigned int>  nGenJet(reader, "nGenJet");  
  TTreeReaderArray<float>         genJetEta          (reader, "GenJet_eta");
  TTreeReaderArray<float>         genJetMass         (reader, "GenJet_mass");
  TTreeReaderArray<float>         genJetPhi          (reader, "GenJet_phi");
  TTreeReaderArray<float>         genJetPt           (reader, "GenJet_pt");
  TTreeReaderArray<unsigned char> genJetHadronFlavour(reader, "GenJet_hadronFlavour");
  TTreeReaderArray<int>           genJetPartonFlavour(reader, "GenJet_partonFlavour");  
  TTreeReaderValue<unsigned int>  nGenPart(reader, "nGenPart");
  TTreeReaderArray<float>         genPartEta             (reader, "GenPart_eta");
  TTreeReaderArray<float>         genPartMass            (reader, "GenPart_mass");
  TTreeReaderArray<int>           genPartPdgId           (reader, "GenPart_pdgId");
  TTreeReaderArray<float>         genPartPhi             (reader, "GenPart_phi");
  TTreeReaderArray<float>         genPartPt              (reader, "GenPart_pt");
  TTreeReaderArray<int>           genPartFtatus          (reader, "GenPart_status");
  TTreeReaderArray<int>           genPartFtatusFlags     (reader, "GenPart_statusFlags");
  TTreeReaderArray<int>           genPartGenPartIdxMother(reader, "GenPart_genPartIdxMother");

  // declare output file
  TFile fo(fname.ReplaceAll(".root",".hist.root"),"recreate");
  TH1F hJetPt1("hJetPt1",";jet 1 p_{T} [GeV]",40,0,600);
  TH1F hJetPt2("hJetPt2",";jet 2 p_{T} [GeV]",40,0,400);
  TH1F hJetPt3("hJetPt3",";jet 3 p_{T} [GeV]",40,0,300);
  TH1F hJetPt4("hJetPt4",";jet 4 p_{T} [GeV]",40,0,200);
  TH1F hMH1("hMH1",";higgs 1 mass [GeV]",40,0,400);
  TH1F hMH2("hMH2",";higgs 2 mass [GeV]",40,0,400);
  TH1F hMHH("hMHH",";di-higgs mass [GeV]",40,0,800);

  int iEvt=0;
  while (reader.Next()) {
    //if (iEvt>5) break;
    unsigned int n = *nGenJet;
    if (n<4) continue;
    ROOT::Math::PtEtaPhiMVector vecs[n];
    for(int i=0; i<n; i++){
      vecs[i] = ROOT::Math::PtEtaPhiMVector(genJetPt[i], genJetEta[i], genJetPhi[i], genJetMass[i]);
    }
    // make pair masses
    int iMass=0;
    std::map<std::pair<int,int>, float> massMap;
    for(int i=0; i<n; i++){
      for(int j=i+1; j<n; j++){
        massMap[{i,j}] = (vecs[i]+vecs[j]).M();
      }
    }
    
    // best indices, metric
    int f1=-1;
    int f2=-1;
    int f3=-1;
    int f4=-1;
    float dM = 9e9;
    
    // find minimizing pairs
    for(int i1=0; i1<n; i1++){
      for(int i2=i1+1; i2<n; i2++){
        for(int i3=i2+1; i3<n; i3++){
          for(int i4=i3+1; i4<n; i4++){
            float m1 = massMap[{i1,i2}];
            float m2 = massMap[{i3,i4}];
            //    if (fabs(m1-m2) < dM){
            //      dM = fabs(m1-m2);
            if (fabs(m1-125) + fabs(m2-125) < dM){
              dM = fabs(m1-125) + fabs(m2-125);
              f1 = i1;
              f2 = i2;
              f3 = i3;
              f4 = i4;
            }
          }
        }
      }
    }
    int t1, t2;
    if( (vecs[f1]+vecs[f2]).Pt() < (vecs[f1]+vecs[f2]).Pt() ){
      t1=f1; t2=f2;
      f1=f3; f2=f4;
      f3=t1; f4=t2;
    }
    hMH1.Fill( (vecs[f1]+vecs[f2]).M() );
    hMH2.Fill( (vecs[f3]+vecs[f4]).M() );
    hMHH.Fill( (vecs[f1]+vecs[f2]+vecs[f3]+vecs[f4]).M() );
      
    vector<float> pts{genJetPt[f1],genJetPt[f2],genJetPt[f3],genJetPt[f4]};
    std::sort(pts.begin(), pts.end(), std::greater<float>());
    hJetPt1.Fill(pts[0]);
    hJetPt2.Fill(pts[1]);
    hJetPt3.Fill(pts[2]);
    hJetPt4.Fill(pts[3]);
    
    iEvt++;
  } // close event loop

  fo.Write();
  fo.Close();
  gSystem->Exit(0); // close the interactive session
}
