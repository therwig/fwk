cuts={
    'incl'  : '1', # otherwise not enforced in MG 2-step generation for signal
    'leps'  : '{e2pt}>1', # otherwise not enforced in MG 2-step generation for signal
    'trig'  : '{e2pt}>1  and {mupt} > 25',
    'bdtT'   : '{e2pt}>1  and {mupt} > 25 and {bdt}>0',
    'bdtL'   : '{e2pt}>1  and {mupt} > 25 and {bdt}>-5',
    'dPhi'  : '{e2pt}>1  and {mupt} > 25 and {dPhiLepMu}>1.57',
    'lep3'  : '{e2pt}>3  and {mupt} > 25 and {dPhiLepMu}>1.57',
    'lep5'  : '{e2pt}>5  and {mupt} > 25 and {dPhiLepMu}>1.57',
    'lep10' : '{e2pt}>10 and {mupt} > 25 and {dPhiLepMu}>1.57',
    # 'srA' : '{e2pt}>1 and {mupt} > 25 and {dPhiLepMu}>1',
    # 'srB' : '{e2pt}>1 and {mupt} > 25 and {dPhiLepMu}>2',
    # 'srC' : '{e2pt}>1 and {mupt} > 25 and {dPhiLepMu}>2.5',
    }
