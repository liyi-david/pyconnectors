from builtin import *
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism

doubleSync = Connector("double sync")
A = doubleSync.createPort(PORT_IO_IN)
B = doubleSync.createPort(PORT_IO_OUT)

M = doubleSync.createNode()
Sync.connect(A, M)
Sync.connect(M, B)

model, prop = sta2prism(getSemantics(doubleSync))
print(model)