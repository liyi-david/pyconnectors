from builtin import *
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism


"""
ARCHITECTURE OF A PROBABILISTIC ROUTER

        A' -Filter > B'
        ^            v
 StochasticChoice    |
        |            ^
        |  ........> B --> E
        | .          |
        |.           |
        .            v
A   --> M  >-------< C
        .            ^
         .           |
          .          |
           ........> D --> F


"""

PRouter = Connector("Probabilistic Router")

A = PRouter.createPort(PORT_IO_IN, 'A')
E, F = PRouter.createPorts(PORT_IO_OUT, 'E', 'F')
M, C, B, D, A1, B1 = PRouter.createNodes(6)

v = Variable(name='x')

Sync.connect(A, M)
SyncDrain.connect(M, C)

LossySync.connect(M, B)
LossySync.connect(M, D)
Sync.connect(B, C)
Sync.connect(D, C)

Sync.connect(B, E)
Sync.connect(D, F)

StochasticChoice.connect(M, A1, params={'dist': BinaryDistribution(0.2)})
Filter.connect(A1, B1, params={'f': (v, EqExpr(v, 1))})
SyncDrain.connect(B1, B)

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
print(model, "\n", prop)