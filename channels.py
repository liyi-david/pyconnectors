from connector import *

Sync = Connector("Sync")
Sync.createPort(PORT_IO_IN)
Sync.createPort(PORT_IO_OUT)
Sync.setTypeChannel()

LossySync = Connector("LossySync")
LossySync.createPort(PORT_IO_IN)
LossySync.createPort(PORT_IO_OUT)
LossySync.setTypeChannel()

SyncDrain = Connector("SyncDrain")
SyncDrain.createPort(PORT_IO_IN)
SyncDrain.createPort(PORT_IO_IN)
SyncDrain.setTypeChannel()

FIFO1 = Connector("FIFO1")
FIFO1.createPort(PORT_IO_IN)
FIFO1.createPort(PORT_IO_OUT)
FIFO1.setTypeChannel()

StochasticChoice = Connector("StochasticChoice")
StochasticChoice.createPort(PORT_IO_IN)
StochasticChoice.createPort(PORT_IO_OUT)
StochasticChoice.setTypeChannel()
StochasticChoice.createParam("dist")

Map = Connector("Map")
Map.createPort(PORT_IO_IN)
Map.createPort(PORT_IO_OUT)
Map.setTypeChannel()
Map.createParam("f")

Filter = Connector("Filter")
Filter.createPort(PORT_IO_IN)
Filter.createPort(PORT_IO_OUT)
Filter.setTypeChannel()
Filter.createParam("f")

PTimer = Connector("pTimer")
PTimer.createPort(PORT_IO_IN)
PTimer.createPort(PORT_IO_IN)
PTimer.createPort(PORT_IO_OUT)
PTimer.setTypeChannel()
PTimer.createParam("t0")