set size 1.0, 1.0

set term post eps enh rounded color solid lw 2 font 'Verdana-Bold,20'
set output "PR_2015_output.eps"

set title "2015 election vote distribution + MME PR projection"

maj_before=169
maj_after=193
#-----------------------------------------------------------------

set yrange [0:215]
unset xtics
# set xtics nomirror
set ylabel "Seats"


set boxwidth 1.0
set style fill solid


set style data histogram


set xtics rotate by 45 offset -0.8,-1.8 
set bmargin 3
set rmargin 8
leftedge=-1
rightedge=5


unset key
set arrow from leftedge, maj_before  to rightedge, maj_before  nohead 
set arrow from leftedge, maj_after   to rightedge, maj_after   nohead linestyle 9
set label "majority" at 5.15,154
set arrow from rightedge+0.1, maj_before to rightedge+0.1, maj_after

plot for [COL=2:3] 'party_seatsbefore_after-2015.txt' using COL:xtic(1) title columnheader

unset multiplot
