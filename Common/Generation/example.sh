outDir="eventOuputs"

# outDir=$outDir"SigXS2"
# outDir=$outDir"ScanNDTest"
outDir=$outDir"221212"

# generate background
nEvents=1000000
nEvents=1000
# ./generate_events.sh b $outDir/outBtest4 $nEvents

# generate signal
# for mzd in 0.03 0.1 0.3 1 3
for mzd in 0.1 0.3 1 3
do
    # for mnd in 0.1
    for mnd in 10 #0.1 0.3 1 3 10
    do
        nEvents=10000
        # nEvents=1000
        echo Generating $nEvents events for mZD = ${mzd} and mND = ${mnd}
        dName=`echo "outS_mZD${mzd}_mND${mnd}" | tr . p`
        # ./generate_events.sh s $outDir/$dName $nEvents $mzd $mnd
        # move events to the data directory
        mkdir -p ../../DarkNeutrino/data/lhe/$outDir
        mv $outDir/$dName/Generation/Events/run_01/unweighted_events.lhe.gz ../../DarkNeutrino/data/lhe/$outDir/$dName.lhe.gz
    done
done
