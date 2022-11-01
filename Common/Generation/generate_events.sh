[[ $1 =~ \-*help ]] && {
    echo "usage: $0 <[b]kg/[s]ig> <outDir> <nEvents> <mZd> <mNd>"
    echo
    exit 0
}

## PARSE
PROC=b
if [[ $1 = s ]]; then
    PROC=s
fi
shift;
DIR=$1; shift;
NEVENTS=$1; shift;

    
if [[ $PROC = s ]]; then
    CARD=proc_card_mg5_sig.tpl;
    MZD=$1; shift;
    MND=$1; shift;
else
    CARD=proc_card_mg5_bkg.tpl; shift;
fi


echo "Will generate the process with card: $CARD"
echo "Will write to output directory $DIR"
echo "Will generate $NEVENTS events"
echo "Will generate a dark photon with mass $MZD"
echo "Will generate a dark neutrino with mass $MND"

HERE=`pwd`
mkdir -p $DIR
cp cards/$CARD $DIR/proc_card_mg5.dat
sed -i '' 's|TMPOUTPUT|'${DIR}'|g' $DIR/proc_card_mg5.dat
sed -i '' 's|TOPDIR|'${HERE}'|g' $DIR/proc_card_mg5.dat
sed -i '' 's|TMPNEVENTS|'${NEVENTS}'|g' $DIR/proc_card_mg5.dat

if [[ $PROC = s ]]; then
    sed -i '' 's|TMPMZD|'${MZD}'|g' $DIR/proc_card_mg5.dat
    sed -i '' 's|TMPMND|'${MND}'|g' $DIR/proc_card_mg5.dat
fi

echo Entering directory $DIR
cd $DIR
mg5_aMC -f proc_card_mg5.dat
echo Done generating events. Returning to directory $HERE
cd $HERE
