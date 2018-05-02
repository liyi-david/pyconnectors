from builtin import *
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism

EmbeddedSystem = Connector("Embedded Control System")

IN1, IN2 = EmbeddedSystem.createPorts(2, PORT_IO_IN)
OUT = EmbeddedSystem.createPort(PORT_IO_OUT)
TIMEOUT = EmbeddedSystem.createPort(PORT_IO_OUT)
CPUIN = EmbeddedSystem.createPort(PORT_IO_OUT)
CPUOUT = EmbeddedSystem.createPort(PORT_IO_IN)

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

model, prop = sta2prism(getSemantics(EmbeddedSystem))
print(model, prop)