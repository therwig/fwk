#!/usr/bin/env python3
import ROOT, argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("input", help="Input ROOT file path")
parser.add_argument("-o", "--output", default='', help="Output file path")
parser.add_argument("--check", action='store_true', default=False, help="Run checks")
args = parser.parse_args()
if len(args.output)==0: args.output = args.input.replace('.root','.friend.root')
print('Analyzing {}'.format(args.input))
df = ROOT.RDataFrame("Events", args.input)
allColumns = list(map(str,df.GetColumnNames()))

ROOT.gInterpreter.Declare("""
using namespace ROOT;
float GetDijetMass(int i, int j, RVecF pt, RVecF eta, RVecF phi, RVecF e){
  ROOT::Math::PtEtaPhiMVector j1(pt[i], eta[i], phi[i], e[i]);
  ROOT::Math::PtEtaPhiMVector j2(pt[j], eta[j], phi[j], e[j]);
  return (j1+j2).M();
}
""")

ROOT.gInterpreter.Declare("""
using namespace ROOT;
float GetMHH(RVecI i, RVecF pt, RVecF eta, RVecF phi, RVecF e){
  ROOT::Math::PtEtaPhiMVector j1(pt[i[0]], eta[i[0]], phi[i[0]], e[i[0]]);
  ROOT::Math::PtEtaPhiMVector j2(pt[i[1]], eta[i[1]], phi[i[1]], e[i[1]]);
  ROOT::Math::PtEtaPhiMVector j3(pt[i[2]], eta[i[2]], phi[i[2]], e[i[2]]);
  ROOT::Math::PtEtaPhiMVector j4(pt[i[3]], eta[i[3]], phi[i[3]], e[i[3]]);
  return (j1+j2+j3+j4).M();
}
""")

ROOT.gInterpreter.Declare("""
using namespace ROOT;
RVecI PickJets(RVecF pt, RVecF eta, RVecF phi, RVecF e){
  // make vectors
  unsigned int n = pt.size();
  if (n<4) return {-1,-1,-1,-1};
  ROOT::Math::PtEtaPhiMVector vecs[n];
  for(int i=0; i<n; i++){
    vecs[i] = ROOT::Math::PtEtaPhiMVector(pt[i], eta[i], phi[i], e[i]);
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
  return {f1, f2, f3, f4};
}
""")


# ROOT.gInterpreter.Declare("""
# using namespace ROOT;
# RVecI PickJets(int nJets){

#   RVecF masses{};
#   unsigned int n = pt.size();
#   ROOT::Math::PtEtaPhiMVector vecs[n];
#   for(int i=0; i<n; i++){
#     vecs[i] = ROOT::Math::PtEtaPhiMVector(pt[i], eta[i], phi[i], e[i]);
#   }
#   for(int i=0; i<n; i++){
#     for(int j=i+1; j<n; j++){
#       masses.push_back( (vecs[i]+vecs[j]).M() );
#     }
#   }
#   return masses;
# }
# """)

ROOT.gInterpreter.Declare("""
using namespace ROOT;
float DoMatch(RVecF jeta, RVecF jphi, RVecF beta, RVecF bphi, RVecI genPartMotherIdxs, RVecI genPartPdgIds){
  for(int i=0; i<jeta.size(); i++){
    for(int j=0; j<beta.size(); j++){
      
    }
  }
  # //for(auto & j in jeta)
  # // return 1;

}
""")


#df = df.Define('GoodJets','GenJet_eta<2.5 && GenJet_eta>-2.5 && GenJet_hadronFlavour==5').Filter('Sum(GoodJets)>=4')
df = df.Define('GoodJets','GenJet_hadronFlavour==5') #.Filter('Sum(GoodJets)>=4')
df = df.Define('JetIdx','PickJets(GenJet_pt[GoodJets], GenJet_eta[GoodJets], GenJet_phi[GoodJets], GenJet_mass[GoodJets])')
df = df.Define('mh1','GetDijetMass(JetIdx[0],JetIdx[1],GenJet_pt[GoodJets], GenJet_eta[GoodJets], GenJet_phi[GoodJets], GenJet_mass[GoodJets])')
df = df.Define('mh2','GetDijetMass(JetIdx[2],JetIdx[3],GenJet_pt[GoodJets], GenJet_eta[GoodJets], GenJet_phi[GoodJets], GenJet_mass[GoodJets])')
df = df.Define('mhh','GetMHH(JetIdx, GenJet_pt[GoodJets], GenJet_eta[GoodJets], GenJet_phi[GoodJets], GenJet_mass[GoodJets])')
df = df.Define('truthBQ','abs(GenPart_pdgId)==5') #.Filter('Sum(GoodJets)>=4')
df = df.Define('matchResult','DoMatch(GenJet_eta[GoodJets], GenJet_phi[GoodJets], GenPart_eta[truthBQ],GenPart_phi[truthBQ], GenPart_genPartIdxMother, GenPart_pdgId)')

newColumns = list(map(str,df.GetColumnNames()))
for c in allColumns: newColumns.remove(c)

if args.check:
    cols = ['JetIdx','GenJet_pt','GoodJets','JetIdx','mh1','mh2']
    arrs = df.AsNumpy(cols)
    cols = ['mh1','mh2']
    for i in range(10):
        for col in cols:
            print( col, arrs[col][i] )
            
df.Snapshot('Friends', args.output, newColumns)
