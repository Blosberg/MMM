#!/usr/local/homebrew/bin/python3
# Driver script for PMM calculation, given input tsv of constituent seat breakdown.
# single command-line argument should be path to this tsv file, omitting terminal ".in"

import csv, sys
# ^ necessary for command-line args.
import matplotlib.pyplot as plt 
plt.style.use("fivethirtyeight")


from PMM_funcdefs import quotient, party
# ^ self-wrttin lib.

if( len(sys.argv) != 2 ):
    print("ERROR: expected 1 command-line arguments for path; received %d " %( len(sys.argv)-1) )

# arguments should be: file_in, file_out

pathstr  = "./test/2011"
# pathstr  = sys.argv[1]

FILE_in  = pathstr
FILE_in +=".in"

FILE_qlist_out   = pathstr
FILE_qlist_out += "_qlist.out"

File_standings_out = pathstr
File_standings_out += ".out"

all_parties = []
total_votes = 0
Seats_total_init=0

namelist=[]

with open(FILE_in) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\t')
    party_ind  = 0
    for row in csv_reader:
        temp = party()
        temp.name          = row[0]
        temp.Seats_initial = int(row[1])
        temp.Votes         = int(row[2])
        all_parties.append(temp)
        #
        Seats_total_init += temp.Seats_initial
        total_votes      += temp.Votes
        #
        namelist.append(temp.name)

Num_parties=len(all_parties)
# including "spoiled" and "independent"

for pind in range(Num_parties):
    #
    all_parties[pind].vote_share = all_parties[pind].Votes/total_votes
    #
    for j in range(2*Seats_total_init):
        # "jval" represents the ranking of the quotient within each party's list
        temp = quotient(  all_parties[pind].name,
                          (j < all_parties[pind].Seats_initial),
                          all_parties[pind].Votes/(j+1),
                          j 
                        )
        all_parties[pind].party_quotient_list.append(temp)

# the j'th quotient for each party is the party's votes divided by j+1
# (starting from j=0);

Total_quotient_list=[]

for pind in range(Num_parties):
    Total_quotient_list.extend( all_parties[pind].party_quotient_list )

Total_quotient_list.sort(reverse=True)
# ^ now we have an ordered list of all quotients from all parties.

# Sanity check:
if( (not Total_quotient_list[Seats_total_init-1].assigned) or Total_quotient_list[Seats_total_init].assigned):
    print("ERROR: Total_quotient_list not properly sorted.")

# --- Document the quotient list:
allqs=[]
fout = open(FILE_qlist_out, "w")
for sval in range(2*Seats_total_init):
    print("%d\t%d\t%d\t%d\t%s" % ( sval, 
                                   Total_quotient_list[sval].jval, 
                                   Total_quotient_list[sval].value, 
                                   Total_quotient_list[sval].assigned, 
                                   Total_quotient_list[sval].party_att 
                                   ),
         file=fout
    )
    allqs.append(Total_quotient_list[sval].value)
fout.close()

# --- Define threshold and compute standings:

Threshold = Total_quotient_list[Seats_total_init-1].value
total_seats_assigned = Seats_total_init

sval = Seats_total_init

# Starting from the first unassigned seat

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

