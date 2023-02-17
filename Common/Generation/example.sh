outDir="eventOuputs"
outDir="eventOuputsZDchan"
outDir="eventOuputsNoUm4"
outDir="eventOuputsPythia"

# outDir=$outDir"SigXS2"
# outDir=$outDir"ScanNDTest"
#outDir=$outDir"221212"
outDir=$outDir"230215"

# generate background
nEvents=1000000
nEvents=100000
# ./generate_events.sh b $outDir/outBtest4 $nEvents
for i in {1..25}
do
    echo running job $i
    # ./generate_events.sh b $outDir/bkgd40k_part$i $nEvents
    mv $outDir/bkgd40k_part$i/Generation/Events/run_01/tag_1_pythia8_events.hepmc.gz ../../DarkNeutrino/data/hepmc/eventOuputsBkgPythiaSplit25/bSplit$i.hepmc.gz
done

# generate signal
# for mzd in 0.002 0.003 0.01 0.03 0.1 0.3 1 3
for mzd in 0.03
do
    # for mnd in 0.1
    for mnd in 0.07 #0.1 0.3 1 3 #10
    do
        nEvents=10000
        # nEvents=1000
        echo Generating $nEvents events for mZD = ${mzd} and mND = ${mnd}
        dName=`echo "outS_mZD${mzd}_mND${mnd}" | tr . p`
        # ./generate_events.sh s $outDir/$dName $nEvents $mzd $mnd
        # ./generate_events.sh sZ $outDir/$dName $nEvents $mzd $mnd
        # move events to the data directory
        mkdir -p ../../DarkNeutrino/data/lhe/$outDir
        mv $outDir/$dName/Generation/Events/run_01/unweighted_events.lhe.gz ../../DarkNeutrino/data/lhe/$outDir/$dName.lhe.gz
        mkdir -p ../../DarkNeutrino/data/hepmc/$outDir
        mv $outDir/$dName/Generation/Events/run_01/tag_1_pythia8_events.hepmc.gz ../../DarkNeutrino/data/hepmc/$outDir/$dName.hepmc.gz
    done
done
