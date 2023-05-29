#outDir="eventOutputs"
#outDir="eventOutputsZDchan"
# outDir="eventOutputsNoUm4"
outDir="eventOutputsPythia"
# outDir="eventOutputsPythiaZZ"
# outDir="eventOutputsPythiaWZhad"
# outDir="eventOutputsPythiaForBDT"
#outDir="xsTestForJosh"

# outDir=$outDir"SigXS2"
# outDir=$outDir"ScanNDTest"
#outDir=$outDir"221212"
# outDir=$outDir"230225"
# outDir=$outDir"230315"
outDir=$outDir"230526"

# generate background
# nEvents=1000000
# nEvents=100000
nEvents=10000
# ./generate_events.sh b $outDir/outBtest4 $nEvents
for i in {1..1} #{1..25}
do
    echo running background job $i
    date
    subdir=""
    sfx=""
    # subdir="/part$i"
    # sfx="$i"
    # ./generate_events.sh b $outDir$subdir/ $nEvents
    # ./generate_events.sh bZ $outDir$subdir/ $nEvents
    # ./generate_events.sh zz $outDir$subdir/ $nEvents
    # ./generate_events.sh ttz $outDir$subdir/ $nEvents
    # ./generate_events.sh wzhad $outDir$subdir/ $nEvents
    # mv $outDir$subdir/Generation/Events/run_01/tag_1_pythia8_events.hepmc.gz ../../DarkNeutrino/data/hepmc/eventOutputsBkgPythiaSplit25/bSplit$i.hepmc.gz
    date
done

# generate signal
# for mzd in 0.003 0.01 0.03 0.1 0.3 1 3
for mzd in 0.03
do
    # for mnd in 0.1
    for mnd in 0.04 0.05 0.06 # 0.07 0.1 0.3 1 3 #10
    do
        # nEvents=1000000
        nEvents=10000
        echo Generating $nEvents events for mZD = ${mzd} and mND = ${mnd}
        dName=`echo "outS_mZD${mzd}_mND${mnd}" | tr . p`
        ./generate_events.sh s $outDir/$dName $nEvents $mzd $mnd
        # ./generate_events.sh sZ $outDir/$dName $nEvents $mzd $mnd
        # move events to the data directory
        # mkdir -p ../../DarkNeutrino/data/lhe/$outDir
        # mv $outDir/$dName/Generation/Events/run_01/unweighted_events.lhe.gz ../../DarkNeutrino/data/lhe/$outDir/$dName.lhe.gz
        mkdir -p ../../DarkNeutrino/data/hepmc/$outDir
        mv $outDir/$dName/Generation/Events/run_01/tag_1_pythia8_events.hepmc.gz ../../DarkNeutrino/data/hepmc/$outDir/$dName.hepmc.gz
    done
done
