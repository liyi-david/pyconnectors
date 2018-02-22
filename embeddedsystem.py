from builtin import *

EmbeddedSystem = Connector("Embedded Control System")

IN1, IN2 = EmbeddedSystem.createPorts(2, PORT_IO_IN)
OUT = EmbeddedSystem.createPort(PORT_IO_OUT)

TIMEOUT = EmbeddedSystem.createPort(PORT_IO_OUT)

CPUIN = EmbeddedSystem.createPort(PORT_IO_OUT)
CPUOUT = EmbeddedSystem.createPort(PORT_IO_IN)

M1, M2, M3, M4 = EmbeddedSystem.createNodes(4)

PLossy.connect(IN1, M1)
PLossy.connect(IN2, M2)
LossySync.connect(M1, M3)
LossySync.connect(M2, M3)

Sync.connect(M3, CPUIN)
Sync.connect(CPUOUT, M4)
Sync.connect(M4, OUT)

PTimer.connect(M3, M4, TIMEOUT, params={"t0": 2})