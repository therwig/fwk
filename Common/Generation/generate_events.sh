[[ $1 =~ \-*help ]] && {
    echo "usage: $0 <[b]kg/[s]ig> <outDir> <nEvents> <mZd> <mNd>"
    echo
    exit 0
}

## PARSE
PROC=b
if [[ $1 = sZ ]]; then
    PROC=sZ
elif [[ $1 = s ]]; then
    PROC=s
elif [[ $1 = bZ ]]; then
    PROC=bZ
elif [[ $1 = zz ]]; then
    PROC=zz
elif [[ $1 = ttz ]]; then
    PROC=ttz
elif [[ $1 = wzhad ]]; then
    PROC=wzhad
fi
shift;
DIR=$1; shift;
NEVENTS=$1; shift;

    
if [[ $PROC = sZ ]]; then
    CARD=proc_card_mg5_sig_Zd4L.tpl;
    MZD=$1; shift;
    MND=$1; shift;
elif [[ $PROC = s ]]; then
    CARD=proc_card_mg5_sig.tpl;
    MZD=$1; shift;
    MND=$1; shift;
elif [[ $PROC = bZ ]]; then
    CARD=proc_card_mg5_bkg_Zd4L.tpl; shift;
elif [[ $PROC = zz ]]; then
    CARD=proc_card_mg5_bkg_ZZ.tpl; shift;
elif [[ $PROC = ttz ]]; then
    CARD=proc_card_mg5_bkg_ttZ.tpl; shift;
elif [[ $PROC = wzhad ]]; then
    CARD=proc_card_mg5_bkg_WZhad.tpl; shift;
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

if [[ $PROC = sZ ]]; then
    sed -i '' 's|TMPMZD|'${MZD}'|g' $DIR/proc_card_mg5.dat
    sed -i '' 's|TMPMND|'${MND}'|g' $DIR/proc_card_mg5.dat
elif [[ $PROC = s ]]; then
    sed -i '' 's|TMPMZD|'${MZD}'|g' $DIR/proc_card_mg5.dat
    sed -i '' 's|TMPMND|'${MND}'|g' $DIR/proc_card_mg5.dat
elif [[ $PROC = b ]]; then
    SEED=`date +%s`
    let "SEED = SEED % 100000" # cant be too big apparently..
    sed -i '' 's|TMPSEED|'${SEED}'|g' $DIR/proc_card_mg5.dat
elif [[ $PROC = bZ ]]; then
    SEED=`date +%s`
    let "SEED = SEED % 100000" # cant be too big apparently..
    sed -i '' 's|TMPSEED|'${SEED}'|g' $DIR/proc_card_mg5.dat
elif [[ $PROC = zz ]]; then
    SEED=`date +%s`
    let "SEED = SEED % 100000" # cant be too big apparently..
    sed -i '' 's|TMPSEED|'${SEED}'|g' $DIR/proc_card_mg5.dat
elif [[ $PROC = ttz ]]; then
    SEED=`date +%s`
    let "SEED = SEED % 100000" # cant be too big apparently..
    sed -i '' 's|TMPSEED|'${SEED}'|g' $DIR/proc_card_mg5.dat
elif [[ $PROC = wzhad ]]; then
    SEED=`date +%s`
    let "SEED = SEED % 100000" # cant be too big apparently..
    sed -i '' 's|TMPSEED|'${SEED}'|g' $DIR/proc_card_mg5.dat
fi

echo Entering directory $DIR
cd $DIR
mg5_aMC -f proc_card_mg5.dat
echo Done generating events. Returning to directory $HERE
cd $HERE
