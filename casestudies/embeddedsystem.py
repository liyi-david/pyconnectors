from builtin import *
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism

import casestudies.probabilistic_delay as pdelay

PDelay = pdelay.PDelay


EmbeddedSystem = Connector("Embedded Control System")

IN1, IN2 = EmbeddedSystem.createPorts(2, PORT_IO_IN)
OUT = EmbeddedSystem.createPort(PORT_IO_OUT)
TIMEOUT = EmbeddedSystem.createPort(PORT_IO_OUT)

CPUIN, CPUOUT = EmbeddedSystem.createNodes(2)
A, B, C, D, E = EmbeddedSystem.createNodes(5)

PLossy.connect(IN1, A)
PLossy.connect(IN2, B)
LossySync.connect(A, C)
LossySync.connect(B, C)

Sync.connect(C, CPUIN)
Sync.connect(CPUOUT, D)
Sync.connect(D, E)
Sync.connect(D, OUT)

PTimer.connect(C, E, TIMEOUT, params={"t0": 2})

# case can be 1 or 2
play_case = 2
if play_case == 1:
    Sync.connect(CPUOUT, CPUIN)
    EmbeddedSystem.addProperty(
        "prop 1",
        Property.G(Expr.lnot(PortTriggered(TIMEOUT)))
    )
elif play_case == 2:
    Sync.connect(CPUOUT, CPUIN)
    PDelay.connect(CPUOUT, CPUIN)
    EmbeddedSystem.addProperty(
        "prop 2",
        Property.Pmax(
            Property.G(
                Expr.derive(
                    Expr.land(PortTriggered(IN1), PortTriggered(IN2)),
                    Property.F(
                        Expr.lor(PortTriggered(TIMEOUT), PortTriggered(OUT))
                    )
                )
            )
        )
    )

model, prop = sta2prism(getSemantics(EmbeddedSystem))
print(model, prop)