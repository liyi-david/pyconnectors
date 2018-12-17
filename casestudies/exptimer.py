from builtin import *
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism

EXPTimer = Connector("EXPTimer")

EXP, TIMEOUT = Value(-1), Value(-2)
t = 2
v = Variable('x')


A = EXPTimer.createPort(PORT_IO_IN, 'A')
H = EXPTimer.createPort(PORT_IO_OUT, 'H')
A0, H0 = EXPTimer.createNodes(2)
D0, D1, D2 = EXPTimer.createNodes(3)
Router.connect(D0, D1, D2)

B, C, E, F, G = EXPTimer.createNodes(5)

Sync.connect(A, A0)
Sync.connect(E, H0)
Sync.connect(H0, H)
Sync.connect(F, G)
Filter.connect(A0, B, params={'f': (v, Expr.neq(v, EXP))})
Filter.connect(A0, C, params={'f': (v, Expr.eq(v, EXP))})
PTimer.connect(B, F, E, params={'t0': t})
FIFO1.connect(B, D0)
SyncDrain.connect(E, D1)
SyncDrain.connect(D2, G)
Map.connect(C, F, params={'f': (v, Value(t))})
Map.connect(G, H0, params={'f': (v, TIMEOUT)})

EXPTimer.addProperty(
    "reset",
    Property.eq(
        Property.Pmax(
            Property.G(
                Expr.derive(
                    Expr.land(PortTriggered(A), Expr.eq(ValueOf(A), EXP)),
                    Expr.land(PortTriggered(H), Expr.eq(ValueOf(H), TIMEOUT))
                )
            )
        ),
        Value(1)
    )
)

model, prop = sta2prism(getSemantics(EXPTimer))
print(model)
print(prop)