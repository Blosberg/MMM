#!/usr/local/homebrew/bin/python3
# Driver script for PMM calculation, given folder with tables 3,7, and 8 from Elections Canada
# single command-line argument should be path to this folder

import os
import csv, sys
# ^ necessary for command-line args.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import PMM
# ^ Library for Parsimonious Mixed-Member functions.
# Defines various functions and classes
MAJOR_PARTY_THRESH = 0.05

assert (len(sys.argv) == 2 ), "Expected 1 command-line arguments for path"

# input argument should be just path to data tables
pathstr  = sys.argv[1]


# ------------- info on total # votes cast & turnout. ---------------------
print ("Collecting info on voter turnout: ...")
T3_path       = os.path.join(pathstr, "table_tableau03.csv")
df_Nvotes        = pd.read_csv(T3_path, index_col="Province")
N_total_votes = df_Nvotes.iloc[:, 6].sum()
print("Total votes : %d " %(N_total_votes) )
print( "Percent votes valid  : %.4f " %( 100*df_Nvotes.iloc[:, 2].sum()/N_total_votes) )
print( "Percent votes invalid: %.4f " %( 100*df_Nvotes.iloc[:, 4].sum()/N_total_votes) )

# ------------- Collect info on initial seat distribution -----------------
T7_path = os.path.join(pathstr, "table_tableau07.csv")
Seats_init = pd.read_csv(T7_path, index_col="Province")
Const_Seats = PMM.get_party_seat_standings(Seats_init)
Seats_total_init = sum( Const_Seats )

# ------------- Valid votes by party: -------------------------------------
T8_path = os.path.join(pathstr, "table_tableau08.csv")
VV_bp = pd.read_csv(T8_path, index_col=0) # index is party name:

Pop_vote_share = pd.Series( VV_bp.sum(axis=1)/N_total_votes,
                            index= VV_bp.index )
# Filter for parties with >5% pop support
maj_parties = Pop_vote_share.index[ Pop_vote_share > 0.05 ]

# Collect Vote_counts for maj parties, and account for spoiled and independent
Vote_counts = VV_bp.loc[maj_parties,].sum(axis=1)
Vote_counts.index = [ PMM.party_abbrev[key] for key in Vote_counts.index ]

# All other parties are grouped together as "OTHER"
# i.e. those who are _explicitly_ independent, as well as those whose
# parties are relegated to "independence" by falling below threshold support.
Vote_counts["OTH"] = sum ( VV_bp.loc[Pop_vote_share < MAJOR_PARTY_THRESH, ].sum(axis = 1 ) )

# "SPL" captures all rejected (i.e. 'spoiled') ballots
Vote_counts["SPL"] = df_Nvotes.sum(axis=0)[4]

Standings = pd.DataFrame( {"Votes":Vote_counts, "Seats_init": Const_Seats } )


print("initial Party Standings: ")
print( Standings )
print("\n----------------------------------")

# OUTPUT this part for documentation:
Standings.to_csv( os.path.join( pathstr, "party_Standings.tsv" ),
                  sep="\t" )

# ------------- Now start building party classes: ----------------------------------
all_parties = []
f_qlist_out     = os.path.join( pathstr, "PMM_qlist.tsv")
f_standings_out = os.path.join( pathstr, "PMM_standings.tsv")


all_parties = [PMM.party( Standings.index[p],
                          Standings.iloc[p,0],
                          Standings.iloc[p,1],
                          N_total_votes,
                          Seats_total_init ) for p in range(Standings.shape[0])]
namelist    = Standings.index
Num_parties = len(all_parties)
# includes "spoiled" and "independent"

# ------- Combine and sort quotient lists from each party -----------
Total_quotient_list=[]
for pind in range(Num_parties):
    Total_quotient_list.extend( all_parties[pind].party_quotient_list )

# and sort, for our globally sorted quotient list
Total_quotient_list.sort(reverse=True)
# ^ now we have an ordered list of all quotients from all parties.

# Sanity check, all constituency seats are assigned, and no others are:
assert all([seat.assigned for seat in Total_quotient_list[0:Seats_total_init-1]]) and not any( [seat.assigned for seat in Total_quotient_list[Seats_total_init:]] ), "ERROR: Total_quotient_list not properly sorted, or inconsistent with expected seat number."

# --- Document the quotient list in a tsv file:
shortlist = Total_quotient_list[:2*Seats_total_init]
# (nothing beyond this list has any chance of consideration.
len( shortlist)
Qlist = pd.DataFrame({"j"        :[ q.jval   for q in shortlist],
                      "Value"    :[ q.value  for q in shortlist],
                      "Assigned" :[ int(q.assigned) for q in shortlist],
                      "party"    :[ q.party_att     for q in shortlist],
                      } )
Qlist.round(2).to_csv(f_qlist_out, sep="\t")

# ------------------------------------------------------------------
# --- Now define Threshold, initialize baseline, and begin to "grow"
# --- by adding quotients until proportionality is reached
Threshold = Total_quotient_list[Seats_total_init-1].value
total_seats_assigned = Seats_total_init

# Starting from the first unassigned seat
sval = Seats_total_init


#=======================================================
print("---------- MADE IT TO CHECKPOINT 2 -------------")
sys.exit()
#=======================================================
# N.B. Check this exit criteria: want to exit when underrep <1

while( Total_quotient_list[sval].value > Threshold ):
    # scroll through and add seats until the value is below threshold.
    if( Total_quotient_list[sval].party_att != "SPL" and Total_quotient_list[sval].party_att != "Oth" ):
        # if this seat is not independent or "spoiled", then find the party matching its name
        pind = namelist.index( Total_quotient_list[sval].party_att )
        # and increment the number of its seats:
        all_parties[pind].seats_assigned += 1
        total_seats_assigned += 1
    #
    sval += 1

#=======================================================
print("---------- MADE IT TO CHECKPOINT 3 -------------")
sys.exit()
#=======================================================

# --- output finale results to file
fout = open(File_standings_out, "w")
for pind in range(Num_parties):
    print("%s\t%d\t%d\t%f\t%d\t%f" %( all_parties[pind].name,
                                      all_parties[pind].Seats_initial,
                                      all_parties[pind].Votes,
                                      all_parties[pind].vote_share,
                                      all_parties[pind].seats_assigned,
                                     (all_parties[pind].seats_assigned/ total_seats_assigned)
                                   ),
          file=fout)
fout.close()

