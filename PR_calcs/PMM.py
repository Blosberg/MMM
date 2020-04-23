import pandas as pd

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

# Define shorthand abbreviations for parties
party_abbrev = {
    'Animal Protection Party of Canada/Le Parti pour la Protection des Animaux du Canada':"APP",
    'Bloc Québécois/Bloc Québécois':"BLQ",
    "Canada's Fourth Front/Quatrième front du Canada":"C4F",
    'Canadian Nationalist Party/Parti Nationaliste Canadien':"CNP",
    "Christian Heritage Party of Canada/Parti de l'Héritage Chrétien du Canada":"CHP",
    'Communist Party of Canada/Parti communiste du Canada':"COM",
    'Conservative Party of Canada/Parti conservateur du Canada':"CON",
    'Green Party of Canada/Le Parti Vert du Canada':"GRN",
    'Liberal Party of Canada/Parti libéral du Canada':"LIB",
    'Libertarian Party of Canada/Parti Libertarien du Canada':"LRT",
    'Marijuana Party/Parti Marijuana':"MJP",
    'Marxist-Leninist Party of Canada/Parti Marxiste-Léniniste du Canada':"MLP",
    'National Citizens Alliance of Canada/Alliance Nationale des Citoyens du Canada':"NCA",
    'New Democratic Party/Nouveau Parti démocratique':"NDP",
    "Parti pour l'Indépendance du Québec/Parti pour l'Indépendance du Québec":"PIQ",
    'Parti Rhinocéros Party/Parti Rhinocéros Party':"RIN",
    "People's Party of Canada/Parti populaire du Canada":"PPC",
    'Progressive Canadian Party/Parti Progressiste Canadien':"PCP",
    'Stop Climate Change/Arrêtons le changement climatique':"SCC",
    'The United Party of Canada/Parti Uni du Canada':"UPC",
    'Veterans Coalition Party of Canada/Parti de la coalition des anciens combattants du Canada':"VET"
}

# --- Extract party seat standings from table
def get_party_seat_standings(Seats_init, maj_parties):
    """Obtain Seat assignments from standard table issued by Elections Canada
    Here, there are multiplie columns for each party, divided by gender,
    condensed here.

    Also, party names have changed over time, so for old elections this
    function will need to be revised.  """
    party_cols = pd.Series( [
        list( filter(lambda x: "Liberal Party of Canada" in x, Seats_init) ),
        list( filter(lambda x: "Conservative Party of Canada" in x, Seats_init) ),
        list( filter(lambda x: "Bloc Québécois" in x, Seats_init) ),
        list( filter(lambda x: "New Democratic Party" in x, Seats_init) ),
        list( filter(lambda x: "Green Party of Canada" in x, Seats_init) ),
        list( filter(lambda x: "Others" in x, Seats_init) ),
        list( filter(lambda x: "Total_" in x, Seats_init) )],
     index = ["LIB","CON","BLQ","NDP","GRN","OTH","TOT"]
    )

    # First gather seat counts for major parties:
    maj_party_cols = party_cols[maj_parties]
    Seats_out      = pd.Series( [ sum( Seats_init[maj_party_cols[p]].sum()) for p in range(len(maj_party_cols)) ],
                                  index = maj_party_cols.index )
    # Now gather the "OTHer" seats

    # Flatten the above list of lists of cols for ALL major parties:
    flat_mpc = [item for sublist in maj_party_cols for item in sublist]

    # Get a list of all col's that are neither a "total" col nor associated with a major party
    OTHer_cols = [ c for c in list(Seats_init) if (not (c in party_cols["TOT"]) and (not c in flat_mpc) ) ]

    Seats_out["OTH"] = sum(Seats_init[OTHer_cols].sum())
    Seats_out["SPL"] = 0
    # Spoiled seat count will always =0

    #--------- Sanity checks:
    # Ensure all columns accounted for:
    assert Seats_init.shape[1] == len(flat_mpc) + len(OTHer_cols) + len(party_cols["TOT"]), "Party names don't match current party names"

    # Ensure all seats add up to the total:
    assert sum( Seats_init[party_cols["TOT"]].sum()) == Seats_out.sum(), "Failed to allocate all seats to a party"

    return Seats_out

# -------------------------------
def shouldbe_done( current_seatnum, partylist, maj_parties):
    """Obtain a boolean characterizing whether all major parties
    are currently owed less than 1 seat."""
    return all( [current_seatnum*(partylist[p].vote_share)-partylist[p].seats_assigned < 1 for p in maj_parties] )


