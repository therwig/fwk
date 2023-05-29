from multiprocessing import Pool
from cfg.samples import samples
import os

def runAna(sample):
    if not sample.isSM:
        os.system("python3 runAnalysis.py --signals '"+sample.name+"' --maxEvents -1")
    else:
        os.system("python3 runAnalysis.py --doBackground --signals '' --maxEvents -1")
    return None

# sigs = ['mZD0p03_mND0p07','mZD0p03_mND0p1']
sigs = [s for s in samples if not s.isSM]

# print(sigs)

if __name__ == '__main__':
    with Pool(4) as p:
        print(p.map(runAna, sigs))


# for s in samples:
#     print (s.name)
