### Howto

The initial step is to generate some events. Currently we use LHE, produced according to the cfg in `Common/Generation`.

Next, these events are converted to ROOT files for later analysis.
```
python3 produceInputs.py
```
The file paths are currently hardcoded in this file, which is essential a wrapper that calls a tool in `Common/Analysis`.
The list of samples to read is specified in `config/samples.py`.


