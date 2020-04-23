#!/usr/local/homebrew/bin/python3
# Driver script for PMM calculation, given folder with tables 3,7, and 8 from Elections Canada
# single command-line argument should be path to this folder

import os, csv, sys
import str
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import PMM
# ^ Library for Parsimonious Mixed-Member functions.
# Defines various functions and classes
MAJOR_PARTY_THRESH = 0.05

assert (len(sys.argv) == 2 ), "Expected 1 command-line arguments for path"

# ================ import data ===============
# input argument should be just path to data tables
pathstr  = sys.argv[1]
year = "".join([x for x in pathstr if str.isdigit(x)])
assert str.isdigit(year), "Cannot determine year from path provided. Please include the election year in the name of your folder"
year = int(year)
assert ( int(year) < 2050 and int(year) > 1867 ), "Inferred implausible year=%d, please check folder names for appropriate year"%year

# Define output paths:
if not os.path.exists( os.path.join( pathstr, "PMM_out") ):
    os.makedirs(os.path.join( pathstr, "PMM_out"))
f_qlist_out     = os.path.join( pathstr, "PMM_out", "PMM_qlist.tsv")
f_standings_out = os.path.join( pathstr, "PMM_out", "PMM_standings.tsv")

# info on total # votes cast & turnout.
T3_path = os.path.join(pathstr, "table_tableau03.csv")
# info on seats awarded
T7_path = os.path.join(pathstr, "table_tableau07.csv")
# Valid votes by party:
T8_path = os.path.join(pathstr, "table_tableau08.csv")

# character encoding changed in 2019:
if (year < 2019 ):
    df_Nvotes     = pd.read_csv(T3_path, index_col="Province", encoding = "ISO-8859-1")
    Seats_init = pd.read_csv(T7_path, index_col="Province", encoding = "ISO-8859-1")
    VV_bp      = pd.read_csv( T8_path, index_col=0, encoding = "ISO-8859-1")
else:
    df_Nvotes     = pd.read_csv(T3_path, index_col="Province")
    Seats_init = pd.read_csv(T7_path, index_col="Province")
    VV_bp      = pd.read_csv( T8_path, index_col=0) # index is party name:


# ================ Process vote totals ===============
N_total_votes = df_Nvotes.iloc[:, 6].sum()
print("Total votes : %d " %(N_total_votes) )
print( "Percent votes valid  : %.4f " %( 100*df_Nvotes.iloc[:, 2].sum()/N_total_votes) )
print( "Percent votes invalid: %.4f " %( 100*df_Nvotes.iloc[:, 4].sum()/N_total_votes) )

# ------------- Process initial seat distribution -----------------
Const_Seats = PMM.get_party_seat_standings(Seats_init)
Seats_total_init = sum( Const_Seats )

# ------------- Valid votes by party: -------------------------------------


Pop_vote_share = pd.Series( VV_bp.sum(axis=1)/N_total_votes,
                            index= VV_bp.index )
# Filter for parties with >5% pop support
maj_parties = Pop_vote_share.index[ Pop_vote_share > 0.05 ]

# Collect Vote_counts for maj parties, and account for spoiled and independent
Vote_counts = VV_bp.loc[maj_parties,].sum(axis=1)
Vote_counts.index = [ PMM.party_abbrev[key] for key in Vote_counts.index ]
maj_parties       = [ PMM.party_abbrev[key] for key in maj_parties ]

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
Standings.to_csv( os.path.join( pathstr, "party_Standings_init.tsv" ),
                  sep="\t" )

# ------------- Now start building party classes: ----------------------------------
f_qlist_out     = os.path.join( pathstr, "PMM_qlist.tsv")
f_standings_out = os.path.join( pathstr, "PMM_standings_final.tsv")


all_parties = { Standings.index[p]: PMM.party( Standings.index[p],
                                        Standings.iloc[p,0],
                                        Standings.iloc[p,1],
                                        N_total_votes,
                                        Seats_total_init)
                for p in range(Standings.shape[0])}

namelist    = Standings.index
Num_parties = len(all_parties)
# includes "spoiled" and "independent"

# ------- Combine and sort quotient lists from each party -----------
Total_quotient_list=[]
for p in all_parties.keys():
    Total_quotient_list.extend( all_parties[p].party_quotient_list )
Total_quotient_list.sort(reverse=True)

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
while (sval < 2*Seats_total_init):
    sval += 1
    current_party = Total_quotient_list[sval].party_att

    # scroll through and add seats until the value is below threshold.
    if (current_party == "SPL" or current_party == "OTH" ):
        continue
        # Skip OTHER, SPOILED quotients.
    elif ( (all_parties[current_party].vote_share*total_seats_assigned)-all_parties[current_party].seats_assigned) > 1 :
        # if this seat is not independent or "spoiled",
        # and is owed seats >1 then give it an extra seat:
        all_parties[current_party].seats_assigned += 1
        total_seats_assigned += 1
    else:
        pass
# --- Finished assigning extra seats -----------
# ------------------------------------------------------------------

Standings_final = pd.DataFrame({"Party": list( all_parties.keys() ),
                      "Seats_initial"  :[ all_parties[p].Seats_initial  for p in all_parties],
                      "Votes"          :[ all_parties[p].Votes          for p in all_parties ],
                      "Vote_share"     :[ all_parties[p].vote_share     for p in all_parties],
                      "Seats_final"    :[ all_parties[p].seats_assigned for p in all_parties ],
                      "Seat_share"     :[ (all_parties[p].seats_assigned)/total_seats_assigned  for p in all_parties]
                      } )
#and output to file:
Standings_final.round(2).to_csv(f_standings_out, sep="\t")

# ==============================================================
#         CALCULATIONS FINISHED. NOW START PLOTTING
# ==============================================================

print("\nPMM program complete.")
