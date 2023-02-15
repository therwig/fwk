### Howto

The initial step is to generate some events. Currently we use LHE, produced according to the cfg in `Common/Generation`.

Next, these events are converted to ROOT files for later analysis.
```
python3 produceInputs.py
# by default the signals are re-run but one can control this via
python3 produceInputs.py --doBackground # background and all signals
python3 produceInputs.py --doBackground --signals '' # background and no signals
python3 produceInputs.py --signals 'mZD0p3_mND10' # one signal
python3 produceInputs.py --signals 'mZD0p3_mND10,mZD0p1_mND10' # a few signals
```
The file paths are currently hardcoded in this file, which is essential a wrapper that calls a tool in `Common/Analysis`.
The list of samples to read is specified in `config/samples.py`.


