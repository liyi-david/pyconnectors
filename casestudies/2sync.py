from builtin import *
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism

doubleSync = Connector("double sync")
A = doubleSync.createPort(PORT_IO_IN, 'A')
B = doubleSync.createPort(PORT_IO_OUT, 'B')

M = doubleSync.createNode()
Sync.connect(A, M)
Sync.connect(M, B)

doubleSync.addProperty(
    "Sync",
    Property.G(Expr.derive(PortTriggered(A), PortTriggered(B)))
)

sem = getSemantics(doubleSync)


model, prop = sta2prism(sem)
print(model)
print(prop)