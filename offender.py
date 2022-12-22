class Offender():

  def __init__(self, userID, strike):
    self.userID = userID
    self.strike = strike
  
  #def __repr__(self):
    #return str(self.userID)
  
  def __str__(self):
    return str(self.userID)+", " + str(self.strike)

  def getUser(self) -> int:
    return self.userID
  
  def getStrike(self) -> int:
    return self.strike
