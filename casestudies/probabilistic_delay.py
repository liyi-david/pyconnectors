from builtin import *
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism

"""
"""

PDelay = Connector("Probabilistic Delay")

A = PDelay.createPort(PORT_IO_IN)
B = PDelay.createPort(PORT_IO_OUT)

C, D, E, F, G = PDelay.createNodes(5)

Sync.connect(A, C)
Sync.connect(C, E)
FIFO1.connect(C, D)
StochasticChoice.connect(C, G, params={'dist': BinaryDistribution(0.1, Value(2), Value(1))})
PTimer.connect(E, G, F, params={'t0': 2})
SyncDrain.connect(F, D)
LossySync.connect(D, B)

delaytime = PDelay.createResetClockAt("delaytime", A, B)

# PDelay.addProperty(
#     "prop",
#     Property.Pmin(
#         Property.U(
#             Expr.lnot(PortTriggered(B)),
#             Expr.geq(Variable("t_0"), Value(2))
#         )
#     )
# )


model, prop = sta2prism(getSemantics(PDelay))
print(model)
print(prop)