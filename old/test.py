from dataclasses import dataclass

@dataclass
class Grunnvarme:
    #-- PROFet
    areal: int
    bygningsstandard: str
    bygningstype: str
    behovsprofil: str
    

    #-- Energiberegning
    cop : float
    #--
    #-- Priser
    investeringskostnad : int
    driftskostnad : int
    #--