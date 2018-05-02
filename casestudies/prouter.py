from builtin import *
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism


"""
ARCHITECTURE OF A PROBABILISTIC ROUTER

        M4 -Filter > M5
        ^            v
 StochasticChoice    |
        |            ^
        |  ........> M2 --> OUT1
        | .          |
        |.           |
        .            v
IN --> M0 >-------< M1
        .            ^
         .           |
          .          |
           ........> M3 --> OUT2


"""

PRouter = Connector("Probabilistic Router")

A = PRouter.createPort(PORT_IO_IN)
E, F = PRouter.createPorts(2, PORT_IO_OUT)
M0, M1, M2, M3, M4, M5 = PRouter.createNodes(6)

v = Variable(name='x')

Sync.connect(A, M0)
SyncDrain.connect(M0, M1)

LossySync.connect(M0, M2)
LossySync.connect(M0, M3)
Sync.connect(M2, M1)
Sync.connect(M3, M1)

Sync.connect(M2, E)
Sync.connect(M3, F)

StochasticChoice.connect(M0, M4, params={'dist': BinaryDistribution(0.2)})
Filter.connect(M4, M5, params={'f': (v, EqExpr(v, 1))})
SyncDrain.connect(M5, M2)

PRouter.addProperty(
    "message will not get lost",
    Property.geq(
        Property.Pmin(
            Property.G(Expr.derive(PortTriggered(A), Expr.lor(PortTriggered(E), PortTriggered(F))))
        ),
        Value(1)
    )
)

model, prop = sta2prism(getSemantics(PRouter))
print(model, prop)