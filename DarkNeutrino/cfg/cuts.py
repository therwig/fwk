cuts={
    'incl'  : '1',
    'leps'  : '{meeS}<10 and {e2pt}>1 and abs({e1eta})<2.5 and abs({e2eta})<2.5', # otherwise not enforced in MG 2-step generation for signal
    'lepsHT': '{meeS}<10 and {e2pt}>1 and abs({e1eta})<2.5 and abs({e2eta})<2.5 and {htc}<30',
    'trig'  : '{meeS}<10 and {e2pt}>1 and abs({e1eta})<2.5 and abs({e2eta})<2.5 and {htc}<30 and {mupt} > 25 and abs({mueta})<2.5',
    'lep3'  : '{meeS}<10 and {e2pt}>3 and abs({e1eta})<2.5 and abs({e2eta})<2.5 and {htc}<30 and {mupt} > 25 and abs({mueta})<2.5',
    # 'bdtT'  : '{meeS}<10 and {e2pt}>3  and {mupt} > 25 and {bdt}>0',
    # 'bdtL'  : '{meeS}<10 and {e2pt}>3  and {mupt} > 25 and {bdt}>-5',
    # 'cuts'  : '{meeS}<10 and {e2pt}>3  and {mupt} > 25 and {dPhiLepMu}>1.57 and {dRee}<1', # cuts_mtMuL<70 , mtL<20 ?
    
    # try cuts_mtMuL<70 , mtL<20?
    # 'cuts1'  : '{meeS}<10 and {e1pt}>1 and {e2pt}>1 and  and {dPhiLepMu}>1.57 and {dRee}<1', 
    # 'cuts3'  : '{meeS}<10 and {e1pt}>3 and {e2pt}>3 and  and {dPhiLepMu}>1.57 and {dRee}<1', 
    # 'cuts5'  : '{meeS}<10 and {e1pt}>5 and {e2pt}>5 and  and {dPhiLepMu}>1.57 and {dRee}<1', 

    # 'lep3'  : '{e2pt}>3  and {mupt} > 25 and {dPhiLepMu}>1.57',
    # 'lep5'  : '{e2pt}>5  and {mupt} > 25 and {dPhiLepMu}>1.57',
    # 'lep10' : '{e2pt}>10 and {mupt} > 25 and {dPhiLepMu}>1.57',
    # 'srA' : '{e2pt}>1 and {mupt} > 25 and {dPhiLepMu}>1',
    # 'srB' : '{e2pt}>1 and {mupt} > 25 and {dPhiLepMu}>2',
    # 'srC' : '{e2pt}>1 and {mupt} > 25 and {dPhiLepMu}>2.5',
    }

allcuts = 'abs({e1eta})<2.5 and abs({e2eta})<2.5 and {mupt}>25 and abs({mueta})<2.5 and {htc}<30' # TRIGGER PT AND ALL ETA CUTS
# cuts['cuts1'] = allcuts + ' and {meeS}<10 and {e1pt}>1 and {e2pt}>1 and {dPhiLepMu}>2 and {dRee}<1'
# cuts['cuts3'] = allcuts + ' and {meeS}<10 and {e1pt}>3 and {e2pt}>3 and {dPhiLepMu}>2 and {dRee}<1'
# cuts['cuts5'] = allcuts + ' and {meeS}<10 and {e1pt}>5 and {e2pt}>5 and {dPhiLepMu}>2 and {dRee}<1'

# mTMuL ? mtL<20?
# cuts['cuts3a'] = allcuts + ' and {meeS}<10 and {e1pt}>3 and {e2pt}>3 and {dPhiLepMu}>2.5 and {dRee}<1 and {metL}<25'
# cuts['cuts3b'] = allcuts + ' and {meeS}<10 and {e1pt}>3 and {e2pt}>3 and {dPhiLepMu}>2.5 and {dRee}<1 and {metL}<25 and {mTL}<15 and {dRLepMu}>2'

#tmp
# cuts['cutsL3'] = allcuts + ' and {meeS}<10 and {e1pt}>3 and {e2pt}>1 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5'
cuts['cutsL1'] = allcuts + ' and {meeS}<10 and {e1pt}>1 and {e2pt}>1 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5'
cuts['cutsL3'] = allcuts + ' and {meeS}<10 and {e1pt}>3 and {e2pt}>3 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5'
cuts['cutsL5'] = allcuts + ' and {meeS}<10 and {e1pt}>5 and {e2pt}>5 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5'

cuts['cuts1'] = allcuts + ' and {meeS}<10 and {e1pt}>1 and {e2pt}>1 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5 and {dRee}<1 and {metL}<30 and {mTL}<15'
cuts['cuts3'] = allcuts + ' and {meeS}<10 and {e1pt}>3 and {e2pt}>3 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5 and {dRee}<1 and {metL}<30 and {mTL}<15'
cuts['cuts5'] = allcuts + ' and {meeS}<10 and {e1pt}>5 and {e2pt}>5 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5 and {dRee}<1 and {metL}<30 and {mTL}<15'

# cuts['cuts1BDT1'] = allcuts + ' and {meeS}<10 and {e1pt}>1 and {e2pt}>1 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5 and {htc}<30 and {bdt}>-5'
# cuts['cuts1BDT2'] = allcuts + ' and {meeS}<10 and {e1pt}>1 and {e2pt}>1 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5 and {htc}<30 and {bdt}>0'

# cuts['cuts1T'] = allcuts + ' and {meeS}<10 and {e1pt}>1 and {e2pt}>1 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5 and {dRee}<1 and {metL}<30 and {mTL}<15 and {htc}<30 and {pTee}>10 and {e1pt}>5'
# cuts['cuts1TT'] = allcuts + ' and {meeS}<10 and {e1pt}>1 and {e2pt}>1 and {dPhiLepMu}>2.5 and {dRLepMu}>1.5 and {dRee}<1 and {metL}<30 and {mTL}<15 and {htc}<30 and {pTee}>12 and {e1pt}>7'

