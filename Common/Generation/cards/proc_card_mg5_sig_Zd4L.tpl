set group_subprocesses Auto
set ignore_six_quark_processes False
set low_mem_multicore_nlo_generation False
set complex_mass_scheme False
set include_lepton_initiated_processes False
set gauge unitary
set loop_optimized_output True
set loop_color_flows False
set max_npoint_for_channel 0
set default_unset_couplings 99
set max_t_for_channel 99
set zerowidth_tchannel True
set nlo_mixed_expansion True
import model DarkNeutrino_Dirac
define p = g u c d s u~ c~ d~ s~
define j = g u c d s u~ c~ d~ s~
define l+ = e+ mu+
define l- = e- mu-
define vl = ve vm vt
define vl~ = ve~ vm~ vt~
generate p p > zd > zd vm~ zd vm #, zd > e+ e- # decay w pythia instead?
output Generation
# output TMPOUTPUT
! cp TOPDIR/cards/param_card.dat Generation/bin/internal/ufomodel/param_card.dat
launch
shower=Pythia8
0
TOPDIR/cards/param_card.dat
TOPDIR/cards/run_card.dat
TOPDIR/cards/pythia8_card.dat
set nevents TMPNEVENTS
set mzd TMPMZD
set mnm TMPMND
set wzd auto
set wnm auto
0
