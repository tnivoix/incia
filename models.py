from enum import Enum

class Root(Enum):
  R = "Rostral"
  M = "Middle"
  C = "Caudal"

class DrugLoc(Enum):
  CONTROL = "Ctrl"
  TC = "TC"
  ME = "ME"
  TCME = "TC+ME"

class DrugName(Enum):
  PICRO = "Picro"
  GABA = "Gaba"
  STRY = "Stry"

class Lesion(Enum):
  NONE = "None"
  LESIONTC = "Lesion TC"
  LESIONME = "Lesion ME"
  LESIONTCME = "Lesion TC+ME"

class Folder:
  def __init__(self, date, subject):
    self.date = date
    self.subject = subject

class Experiment:
  def __init__(self, folder, number, drugLoc, drugName, lesion):
    self.folder = folder
    self.number = number
    self.drugLoc = drugLoc
    self.drugName = drugName
    self.lesion = lesion

class File:
  def __init__(self, experiment, side, root):
    self.experiment = experiment
    self.side = side
    self.root = root