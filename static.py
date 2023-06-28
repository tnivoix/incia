from enum import Enum

ROOT_FOLDER = "Data_thomas/"


class Root(Enum):
    Rost = 0
    Mid = 1
    Caud = 2


class Side(Enum):
    L = 0
    R = 1


class Color(Enum):
    blue = 0
    orange = 1
    green = 2
    purple = 3