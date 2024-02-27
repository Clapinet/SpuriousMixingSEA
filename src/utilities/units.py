from dataclasses import dataclass


@dataclass
class Unit:

    name: str
    symbol: str
    unit: str
    symphonie_type: str  # type (t, u or v) in SYMPHONIE outputs

    def __str__(self):
        return f"{self.symbol} [{self.unit}]"


tem = Unit("tem", "T", "°C", "t")
sal = Unit("sal", "S", "psu", "t")
dpt = Unit("dpt", "Depth", 'm', 't')
hgt = Unit("hgt", "Height", 'm', 't')




    