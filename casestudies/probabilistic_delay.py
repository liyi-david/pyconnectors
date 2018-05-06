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


# # PDelay testbench
# PDelayTestbench = Connector("testbench")
# A = PDelayTestbench.createPort(PORT_IO_OUT)
# M0, M1 = PDelayTestbench.createNodes(2)
# FIFO1.connect(M0, M1, params={'default_value': Value(1)})
# PDelay.connect(M1, A)
#
# PDelayTestbench.addProperty(
#     "prop",
#     Property.Pmin(
#         Property.F(
#             Expr.land(Expr.leq(delaytime, 1), PortTriggered(A))
#         )
#     )
# )

delaytime = PDelay.createResetClockAt("delaytime", A)
PDelay.addProperty(
    "maximum probability",
    Property.derive(
        PortTriggered(A),
        Property.geq(
            Property.Pmax(Property.U(Property.leq(delaytime, Value(1)), PortTriggered(B))),
            Value(0.8)
        )
    )
)

if __name__ == "__main__":
    sem = getSemantics(PDelay)
    model, prop = sta2prism(sem)

    print(model)
    print(prop)