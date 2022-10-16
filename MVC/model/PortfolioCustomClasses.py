from dataclasses import dataclass, field

from matplotlib.dviread import DviFont
#import pandas as pd

@dataclass(frozen=True)
class DataFrameObject:
    oddness: str
    value: int
    name: str
    fish: str = field(default="tuna")

@dataclass(frozen=True)
class Portfolio:
    basis_info: DataFrameObject