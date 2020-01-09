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
  def __init__(self, name_in="NULL", Votes_in=0, Seats_const=0):        

      self.name           = name_in
      self.Votes          = Votes_in
      self.Seats_initial  = Seats_const
  
      self.vote_share     = -1;
      # vote_share cannot be calculated without considering the whole list
      # of parties, so initialize it to an obviously nonsensical value.

      self.seats_assigned = Seats_const; 
      # seats currently assigned at a given moment 

      # temp = quotient("NULL", False, 0)
      self.party_quotient_list = []
  


