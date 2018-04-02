import taster


class Dish:
  def _init(self, data):
    for key in data.keys():
      setattr(self, key, data[key])
    '''
    for key in data["flavours"].keys():
      setattr(self, key, data["flavours"][key])
    '''
    self.data = data

    self.tastedata = taster.taste(data)
    print("Taste profile for the dish ", data['dish_name'], "is ", self.tastedata)
    for key in self.tastedata.keys():
      setattr(self, key, self.tastedata[key])

    self.most_significant_flavour = ("default", 0)

    # for key, value in data["flavours"].items():
    for key, value in self.tastedata.items():
      if self.most_significant_flavour[1] < value:
        self.most_significant_flavour = (key, value)

  def __init__(self, data):
    self._init(data)

  def __getitem__(self, key):
    return getattr(self, key)
