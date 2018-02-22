from builtin import Router, FIFO2, PLossy, PRouter, RstTimer, TTimer, FIFO4
from channels import Sync, PTimer
from semantics.STAr import getSemantics
from semantics.STAr.composition import getMixedNode
from semantics.STAr.expression import *
from semantics.STAr.prism import sta2prism
from embeddedsystem import EmbeddedSystem

# sem = getSemantics(RstTimer, params={"t0": 2})
# sem = getSemantics(Sync)
sem = getSemantics(EmbeddedSystem)
# sem = getSemantics(FIFO4)
print(sta2prism(sem))
pass