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
### import model DarkNeutrino_Dirac
define p = g u c d s u~ c~ d~ s~
define j = g u c d s u~ c~ d~ s~
define l+ = e+ mu+
define l- = e- mu-
define vl = ve vm vt
define vl~ = ve~ vm~ vt~
### generate p p > w- > mu- vm~ e+ e- / zd
generate p p > w- > mu- vm~ e+ e-
output Generation
# output TMPOUTPUT
! cp TOPDIR/cards/param_card.dat Generation/bin/internal/ufomodel/param_card.dat
launch
0
TOPDIR/cards/param_card.dat
TOPDIR/cards/run_card.dat
set nevents TMPNEVENTS
0
