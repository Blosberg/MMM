import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class quotient():
    """A class representing a single quotient."""
    def __init__(self, party_att_in = "NULL", assigned_in = False, value_in = 0, jval_in = 0 ):
        """Assume a six-sided die."""
        self.party_att = party_att_in
        self.assigned  = assigned_in
        self.value     = value_in
        self.jval      = jval_in

    def __lt__(self, other):
        # Being assigned to a constituency takes priority in sorting
         # thereafter we compare the values
        if (    self.assigned == False and other.assigned == True ):
             return True
        elif (  self.assigned == True and other.assigned == False ):
             return False
        else:
             return self.value < other.value

    def __gt__(self, other):
        return  other < self

# ====================================================
# --- Define class object "party"
class party():
  """A class representing a party -- each instance will end up with a
  whole list of quotients."""
  def __init__(self, name_in="NULL", Votes_in=0, Seats_const=0, N_total_votes=-1, Seats_total_init=-1):

      self.name           = name_in
      self.Votes          = Votes_in
      self.Seats_initial  = Seats_const

      self.vote_share     = Votes_in/N_total_votes
      # N_total_votes now read in from Elections Canada table
      # so vote_share can be immediately initialized.

      self.seats_assigned = Seats_const;
      # seats currently assigned at a given moment

      # temp = quotient("NULL", False, 0)
      self.party_quotient_list = [ quotient( self.name,
                                             (j < self.Seats_initial),
                                             (self.Votes/(j+1)),
                                             j )
                                   for j in range(2*Seats_total_init) ]


# ====================================================
party_codes_en = {
    #    Define shorthand abbreviations for parties based on key strings
    #    i.e. any party name that contains "Rhinoc" is assumed to be the Rhinocerous party, etc...
    #    this avoids issues with character encoding, etc. 
    'Animal Protection Party':"APP",
    'Bloc Qu':"BLQ",
    "Fourth Front":"C4F",
    'Canadian Nationalist Party':"CNP",
    "Christian Heritage Party":"CHP",
    'Communist Party':"COM",
    'Conservative Party':"CON",
    'Green Party':"GRN",
    'Liberal Party':"LIB",
    'Libertarian Party':"LRT",
    'Marijuana Party':"MJP",
    'Marxist-Leninist Party':"MLP",
    'National Citizens Alliance':"NCA",
    'New Democratic Party':"NDP",
    "pendance du Qu":"PIQ",
    'Rhinoc':"RIN",
    "People's Party":"PPC",
    'Progressive Canadian Party':"PCP",
    'Stop Climate Change':"SCC",
    'The United Party':"UPC",
    'Veterans Coalition Party':"VET",
    'Autres':"OTH",
    "Total":"TOT"
}
party_codes_fr= {
    'Protection des Animaux':"APP",
    'Bloc Québécois':"BLQ",
    "Quatrième front":"C4F",
    'Parti Nationaliste':"CNP",
    "Parti de l'Héritage Chrétien":"CHP",
    'Parti communiste':"COM",
    'Parti conservateur':"CON",
    'Le Parti Vert':"GRN",
    'Parti libéral':"LIB",
    'Parti Libertarien':"LRT",
    'Parti Marijuana':"MJP",
    'Parti Marxiste-Léniniste':"MLP",
    'Alliance Nationale':"NCA",
    'Nouveau Parti démocratique':"NDP",
    "l'Indépendance du Québec":"PIQ",
    'Parti Rhinocéros':"RIN",
    "Parti populaire":"PPC",
    'Parti Progressiste':"PCP",
    'Arrêtons le changement climatique':"SCC",
    'Parti Uni':"UPC",
    'Parti de la coalition des anciens combattants':"VET",
    'Other':"OTH",
    "Total":"TOT"
}
# ====================================================
colours= { 
    "trans":{    
            "BLQ" : "#33FFFF99",
            "CON" : "#0000CC99",
            "GRN" : "#33660099",
            "LIB" : "#CC000099",
            "NDP" : "#FF800099",
            "OTH":"#707070"
    },
    "solid":{        
            "BLQ"  : "#33FFFFFF",
            "CON"  : "#0000CCFF",
            "GRN"  : "#336600FF",
            "LIB"  : "#CC0000FF",
            "NDP"  : "#FF8000FF",
            "OTH":"#707070"
    }
}
# ====================================================
Logos= {    
        "BLQ" : "images_post/logos/BLQ.png",
        "CON" : "images_post/logos/CON.png",
        "GRN" : "images_post/logos/GRN.png",
        "LIB" : "images_post/logos/LIB.png",
        "NDP" : "images_post/logos/NDP.png",
        "OTH" : "images_post/logos/OTH.png"
}
symbols= {
        "BLQ" : "o",
        "CON" : "v",
        "GRN" : "P",
        "LIB" : "s",
        "NDP" : "D",
        "OTH" : "x"
}
# ====================================================
def code_for_single_label(label, party_codes_en, party_codes_fr):
    map_en = [ party_codes_en[s] for s in party_codes_en.keys() if s in label ] 
    map_fr = [ party_codes_fr[s] for s in party_codes_fr.keys() if s in label ] 
    
    assert len(map_en)<=1, "Multiple English matches for label %s"%label
    assert len(map_fr)<=1, "Multiple French  matches for label %s"%label    
    assert (len(map_fr) + len(map_en) ) >=1, "No matches for label %s in either language"%label
    
    if( len(map_fr) == 1 and len(map_en)==1 ):
        assert map_fr[0] == map_en[0], "Different matches for label %s; Eng:%s, Fr:%s"%(label, map_en[0],map_fr[0])

    if( len(map_en) == 1):
        return (map_en[0])
    else:
        return (map_fr[0])   
# ====================================================
def standardize_party_labels( DF, party_codes_en, party_codes_fr, axis_in=1):
    """Convert the long and complicated labels for various political parties 
    into standard 3-letter codes, based on a dict of unique strings that 
    tend to appear in each name.
    e.g. anythin with 'Bloc Qu' will become 'BLQ', to avoid unicode issues with
    the e' characters.
    """    
    assert axis_in == 0 or axis_in == 1, "Invalid axis_in %d"%axis_in
    if( axis_in == 1):
        names_init = list(DF)
    elif( axis_in == 0 ):
        assert len( list(DF.shape) ) == 1, "Standardizing row labels should only happen for type pd.Series (i.e. single column)"
        names_init = DF.index    
    
    pcodes    = np.array( [ code_for_single_label(name, party_codes_en, party_codes_fr) for name in names_init] )
    label_out = sorted( list(set(pcodes)))

    if( axis_in == 1):
        result = pd.DataFrame( { label: DF.loc[:,pcodes == label].sum(axis=axis_in) for label in label_out } )
    elif( axis_in == 0 ):
        result  = DF.copy()
        result.index=label_out
    
    return result

# ====================================================
def shouldbe_done( current_seatnum, partylist, maj_parties):
    """Obtain a boolean characterizing whether all major parties
    are currently owed less than 1 seat. Useful for debugging. 
    When this returns True, the while loop should terminate. """
    return all( [current_seatnum*(partylist[p].vote_share)-partylist[p].seats_assigned < 1 for p in maj_parties] )

# ====================================================
def plot_projection( Standings, year, fout):
    """Plot projections of a given year's results based on this system. """
    # data to plot
    n_groups = Standings.shape[0]-1

    # create plot
    fig, ax       = plt.subplots()
    x_positions   = np.arange(n_groups)
    bar_width     = 0.35
    opaque        = 0.95
    semitrans     = 0.5

    Seats_total_init  = Standings["Seats_initial"].sum()
    maj_init = 0.5*Seats_total_init
    Seats_total_final = Standings["Seats_final"].sum()
    maj_final = 0.5*Seats_total_final

    rects1 = plt.bar( x_positions, 
                      Standings["Seats_initial"][:-1], 
                      bar_width,
                      alpha=opaque,
                      color=[ colours["solid"][p]  for p in Standings.index[:-1] ],
                      label='Initial')

    rects2 = plt.bar( x_positions + bar_width, 
                      Standings["Seats_final"][:-1], 
                      bar_width,
                      alpha=semitrans,
                      color=[ colours["trans"][p]  for p in Standings.index[:-1] ],
                      label='PMM')

    xmin = -0.5*bar_width
    xmax = bar_width*(2*(n_groups+1))
    maj_thresh_b4    = plt.plot([xmin, xmax],[maj_init,  maj_init],"-k")
    maj_thresh_after = plt.plot([xmin, xmax],[maj_final, maj_final],"--k")

    # No text in this annotation, to ensure that the arrow goes straight vertical
    ax.annotate('', xy=(xmax, 0.5*Seats_total_final),
                 xycoords='data',
                 xytext=(xmax, 0.5*Seats_total_init),
                 textcoords='data',
                 arrowprops=dict(arrowstyle= '->',
                                 color='black',
                                 lw=2.0,
                                 ls='-')
               )

    ax.annotate('Majority', 
                 xy=( xmax-bar_width, 0.5*Seats_total_init-20),
                 xycoords='data',
                 # xytext=(0.8, 0.5), textcoords='axes fraction'
                 # , horizontalalignment='right', verticalalignment='top',
                )


    # plt.xlabel('Party', fontsize=15)
    plt.ylabel('Seats', fontsize=15)
    plt.title(str(year), fontsize=15 )
    # ax.set_xticks([], [])
    plt.xticks(x_positions + bar_width, tuple( list(Standings.index[:-1])), fontsize=25 )

    #######
    # # Far too much time was wasted here trying to import the party logos 
    # # automatically. Unfortunately matplotlib doesn't want to let me add
    # # enough space for them at the bottom of the figure (illustrative example 
    # # of attempts thus far commented out below). The kludge fix is to add 
    # # them in manually for each figure --an ugly and unsatisfying workaround.
    # # If anyone can suggest how to fix this, please post an issue or PR
    #
    # p=0
    # logo = mpimg.imread(Logos[Standings_final.index[p]])
    # logobox = OffsetImage(logo, zoom=0.5)
    # ab = AnnotationBbox( logobox, 
    #                   xy = (x_positions[p]+0.25*bar_width, 1), 
    #                   xybox=(x_positions[p]+0.95*bar_width, 2),
    # #                     xycoords='figure fraction',
    #                   frameon=True, 
    #                   pad=0 )
    # ax.add_artist(ab)
    plt.savefig(fout, bbox_inches="tight")

# ====================================================
def plot_quotients_each_party( maj_party_codes, year, Full_parl_Q, partylist, fout):
    """Plot quotient lists for each party separately."""

    maxQ = max( [partylist[p].party_quotient_list[0].value for p in maj_party_codes] )

    xmin = -5
    xmax = 200
    ymin = 0.5 * Full_parl_Q
    ymax = maxQ

    for p in maj_party_codes:
        plt.scatter( range(len(partylist[p].party_quotient_list)),
                     [ q.value for q in partylist[p].party_quotient_list ],
                     color  = colours["trans"][p],
                     marker = symbols[p],
                     alpha  = 0.5 
                    )
    plt.xlim([xmin, xmax])
    plt.ylim([ymin, ymax])
    plt.yscale('log')   
    plt.legend( maj_party_codes )

    thresh_draw = plt.plot( [xmin, xmax],
                            [ Full_parl_Q, Full_parl_Q],
                            "-k", 
                            alpha=0.5,
                            lw = 5)

    plt.xlabel('$j$',   fontsize=15)
    plt.ylabel('$Q_j$', fontsize=15)

    ax = plt.gca()
    # ax.yaxis.set_label_coords(0.0, 1.05)

    plt.title( "Quotients "+str(year)+", Major Parties", fontsize=15 )
    plt.savefig(fout, bbox_inches="tight")

# ====================================================
def plot_all_quotients( maj_party_codes, year, Qlist_raw, fout ):
    """Plot all quotients together"""

    # Remove one point from each party and plot separately to create a legend.
    First_points = [ min( [q for q in range(len(Qlist_raw)) if Qlist_raw[q].party_att==party] ) for party in maj_party_codes ] 
    Qlist = [ Qlist_raw[q] for q in range(len(Qlist_raw)) if ( (Qlist_raw[q].party_att in maj_party_codes) and ( not q in First_points)) ] 

    # create plot
    fig, ax = plt.subplots()  
    # Now plot just those first points to establish a legend
    for k in First_points:
        plt.scatter( k, 
                     Qlist_raw[k].value,
                     color  = colours["solid"][Qlist_raw[k].party_att],
                     marker = symbols[Qlist_raw[k].party_att],
                    )
    plt.legend( maj_party_codes )
    plt.ylim([10000,10000000])
    plt.yscale('log')

    # Define color-code and marker code lists for the remaining points
    ccode = [ colours["solid"][q.party_att] for q in Qlist ]
    mcode = [ symbols[q.party_att] for q in Qlist ]
    Npoints = len(Qlist)

    x_dat   = range(Npoints)
    y_dat   = [q.value for q in Qlist]

    for k in range(Npoints):
        plt.scatter( x_dat[k], 
                     y_dat[k],
                     color  = ccode[k],
                     marker = mcode[k],
                    )


    # threshold for smallest constituent quotient
    THRESH      = min( [ q.value for q in Qlist if q.assigned ])
    thresh_draw = plt.plot( [min(x_dat), max(x_dat)],
                            [THRESH, THRESH],
                            "-k", 
                            alpha=0.5,
                            lw = 5)

    plt.xlabel('$i$',   fontsize=15)
    plt.ylabel('$Q_i$', fontsize=15)
    plt.title( "Quotients "+str(year)+", Ordered", fontsize=15 )

    plt.savefig(fout, bbox_inches="tight")