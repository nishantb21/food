'''
User Profiler
'''

import random
import json
import taster
import copy
class Profile:
  def __init__(self, dishlistfile='testset.json', history=20):
    self.flavourlist = ["salt", "sweet", "rich"]

    with open(dishlistfile) as ifile:
      self.items = json.load(ifile)
    #print(json.dumps(self.items))
    self.history = random.sample(self.items, k=history)
    hist = copy.deepcopy(self.history)
    self.taste = self.init_profile(hist)
    #print(json.dumps(self.history))

  def init_profile(self,history):
    _taste = dict()
    for flavour in self.flavourlist:
      _taste[flavour] = 0.0

    for dish in history:
      tastedict = taster.taste(dish)
      #print(tastedict)
      for flavour in self.flavourlist:
        _taste[flavour] += tastedict[flavour]

    for flavour in self.flavourlist:
      _taste[flavour] /= len(history)

    return _taste

  def dish_titles(self):
    return [food["dish_name"] for food in self.history]

  def __str__(self):
    return str(list(zip(self.dish_titles(), [taster.taste(food) for food in self.history])))

if __name__ == "__main__":
  #Profile()
  print(Profile())
