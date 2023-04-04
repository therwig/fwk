cuts={
    'incl'  : '1', 
    'leps'  : '{meeS}<10 and {e2pt}>1', # otherwise not enforced in MG 2-step generation for signal
    'trig'  : '{meeS}<10 and {e2pt}>1  and {mupt} > 25',
    'lep3'  : '{meeS}<10 and {e2pt}>3  and {mupt} > 25',
    'bdtT'  : '{meeS}<10 and {e2pt}>3  and {mupt} > 25 and {bdt}>0',
    'bdtL'  : '{meeS}<10 and {e2pt}>3  and {mupt} > 25 and {bdt}>-5',
    'cuts'  : '{meeS}<10 and {e2pt}>3  and {mupt} > 25 and {dPhiLepMu}>1.57 and {dRee}<1', # cuts_mtMuL<70 , mtL<20 ?
    # 'lep3'  : '{e2pt}>3  and {mupt} > 25 and {dPhiLepMu}>1.57',
    # 'lep5'  : '{e2pt}>5  and {mupt} > 25 and {dPhiLepMu}>1.57',
    # 'lep10' : '{e2pt}>10 and {mupt} > 25 and {dPhiLepMu}>1.57',
    # 'srA' : '{e2pt}>1 and {mupt} > 25 and {dPhiLepMu}>1',
    # 'srB' : '{e2pt}>1 and {mupt} > 25 and {dPhiLepMu}>2',
    # 'srC' : '{e2pt}>1 and {mupt} > 25 and {dPhiLepMu}>2.5',
    }
