from channels import *
from semantics.STAr.expression import *

"""
ARCHITECTURE OF ROUTER

        ....> M2 --> OUT1
        .     |
IN --> M0 >-< M1
        .     |
        ....> M3 --> OUT2


"""


Router = Connector("Router")

IN = Router.createPort(PORT_IO_IN)
OUT1, OUT2 = Router.createPorts(2, PORT_IO_OUT)
M0, M1, M2, M3 = Router.createNodes(4)

Sync.connect(IN, M0)
SyncDrain.connect(M0, M1)

LossySync.connect(M0, M2)
LossySync.connect(M0, M3)
Sync.connect(M2, M1)
Sync.connect(M3, M1)

Sync.connect(M2, OUT1)
Sync.connect(M3, OUT2)


"""
ARCHITECTURE OF A FIFO2

IN --[]--> --[]--> OUT
"""


FIFO2 = Connector("FIFO2")
IN = FIFO2.createPort(PORT_IO_IN)
OUT = FIFO2.createPort(PORT_IO_OUT)

M = FIFO2.createNode()

FIFO1.connect(IN, M)
FIFO1.connect(M, OUT)

"""
ARCHITECTURE OF A PROBABILISTIC LOSSY

              / - StochasticChoice -> M1 - Filter -> M2
             /                                       v
IN - Sync -> M0                                      |
             \                                       ^
              \ -------- LossySync ----------------> M3 - Sync -> Out
"""

PLossy = Connector("Probabilistic Lossy")
IN = PLossy.createPort(PORT_IO_IN)
OUT = PLossy.createPort(PORT_IO_OUT)

M0, M1, M2, M3 = PLossy.createNodes(4)

Sync.connect(IN, M0)
StochasticChoice.connect(M0, M1, params={'dist': BinaryDistribution(0.2)})
v = Variable(name='x')
Filter.connect(M1, M2, params={'f': (v,  EqExpr(v, 1))})
LossySync.connect(M0, M3)
SyncDrain.connect(M2, M3)
Sync.connect(M3, OUT)


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

IN = PRouter.createPort(PORT_IO_IN)
OUT1, OUT2 = PRouter.createPorts(2, PORT_IO_OUT)
M0, M1, M2, M3, M4, M5 = PRouter.createNodes(6)

v = Variable(name='x')

Sync.connect(IN, M0)
SyncDrain.connect(M0, M1)

LossySync.connect(M0, M2)
LossySync.connect(M0, M3)
Sync.connect(M2, M1)
Sync.connect(M3, M1)

Sync.connect(M2, OUT1)
Sync.connect(M3, OUT2)

StochasticChoice.connect(M0, M4, params={'dist': BinaryDistribution(0.2)})
Filter.connect(M4, M5, params={'f': (v,  EqExpr(v, 1))})
SyncDrain.connect(M5, M2)


"""
ARCHITECTURE OF A RESET TIMER

         R
         |
        Map
         |
         v
A ---- pTimer ---> B

"""
RstTimer = Connector("Reset Timer")

IN, RESET = RstTimer.createPorts(2, PORT_IO_IN)
OUT = RstTimer.createPort(PORT_IO_OUT)

v = Variable(name='x')

M = RstTimer.createNode()
PTimer.connect(IN, M, OUT, params={"t0": ValueExpr(4)})
Map.connect(RESET, M, params={"f": (v, ValueExpr(4))})

"""
ARCHITECTURE OF A T-TIMER

    [NOT CONNECTED]
         |
         v
A ---- pTimer ---> B

"""

TTimer = Connector("t-Timer")

IN = TTimer.createPort(PORT_IO_IN)
OUT = TTimer.createPort(PORT_IO_OUT)

M = TTimer.createNode()
PTimer.connect(IN, M, OUT, params={"t0": ValueExpr(4)})


"""
ARCHITECTURE OF A FIFO4

A --- FIFO2 --> --- FIFO2 --> B

This connector is used to test the connection between two connectors instead of two channels

"""

FIFO4 = Connector("FIFO4")
IN = FIFO4.createPort(PORT_IO_IN)
OUT = FIFO4.createPort(PORT_IO_OUT)

M = FIFO4.createNode()
FIFO2.connect(IN, M)
FIFO2.connect(M, OUT)