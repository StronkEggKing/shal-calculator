###########
#LIBRARIES#
###########

import math
from typing import Optional
from table import key_map as Conversions


#####
#SAL#
#####

def calculate(inp):
    out = ""
    CurrentConv = "Eng"
    for char in str(inp):
        #print(char)
        for Eng, Ar in Conversions.items():
            if char == Eng and CurrentConv == "Eng":
                out = out + Ar
            elif char == Ar:
                CurrentConv = "Ar"
                out = out + Eng

    #print(out)
    return out
