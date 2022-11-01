Can run the generation with madgraph using scripts like this:

```
outDir="eventOuputs"

# generate background
nEvents=1000000
./generate_events.sh b $outDir/outB1M $nEvents

# generate signal
for mzd in 0.030 0.1 0.3 1 3
do
    for mnd in 10
    do
        nEvents=10000
        echo Generating $nEvents events for mZD = ${mzd} and mND = ${mnd}
        ./generate_events.sh s $outDir/outS_mZD${mzd}_mND${mnd} $nEvents $mzd $mnd
    done
done
```
