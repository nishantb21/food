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

    tastedata = taster.taste(data)
    for key in tastedata.keys():
      setattr(self, key, tastedata[key])

    self.most_significant_flavour = ("default", 0)

    # for key, value in data["flavours"].items():
    for key, value in tastedata.items():
      if self.most_significant_flavour[1] < value:
        self.most_significant_flavour = (key, value)

  def __init__(self, data):
    self._init(data)

  def __getitem__(self, key):
    return getattr(self, key)
