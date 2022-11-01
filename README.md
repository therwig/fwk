# fwk: a general framework for HEP event analysis

Pieces
- Common/Generation: recipes to generate LHE (and HepMC?) events for the analyes contained within
- Common/EventFormat: Production of common-format ROOT/(HF5?) files from LHE/(HepMC?)
- Common/X: Decoration of the base events with extra variables (friend trees) (merge into analysis??)
- Common/Analysis: (Calculate variables?), apply cuts, produce histograms, SR yields
- Common/Limits: Collect sample information, calculate limits
- Common/Reinterpret: this should be analysis-dependent
- ExampleAnalysis: how to use these pieces together

## Example workflow

Add the libraries to your python path and enter the analysis area.
```
source setup.sh
cd DarkNeutrino
```

Convert LHE inputs to root files
```
python3 produceInputs.py
```

