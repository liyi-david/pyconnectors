from connector import *

Sync = Connector("Sync")
Sync.createPort(PORT_IO_IN, 'A')
Sync.createPort(PORT_IO_OUT, 'B')
Sync.setTypeChannel()

LossySync = Connector("LossySync")
LossySync.createPort(PORT_IO_IN, 'A')
LossySync.createPort(PORT_IO_OUT, 'B')
LossySync.setTypeChannel()

SyncDrain = Connector("SyncDrain")
SyncDrain.createPort(PORT_IO_IN, 'A')
SyncDrain.createPort(PORT_IO_IN, 'B')
SyncDrain.setTypeChannel()

FIFO1 = Connector("FIFO1")
FIFO1.createPort(PORT_IO_IN, 'A')
FIFO1.createPort(PORT_IO_OUT, 'B')
FIFO1.setTypeChannel()
FIFO1.createParam("default_value")

StochasticChoice = Connector("StochasticChoice")
StochasticChoice.createPort(PORT_IO_IN, 'A')
StochasticChoice.createPort(PORT_IO_OUT, 'B')
StochasticChoice.setTypeChannel()
StochasticChoice.createParam("dist")

Map = Connector("Map")
Map.createPort(PORT_IO_IN, 'A')
Map.createPort(PORT_IO_OUT, 'B')
Map.setTypeChannel()
Map.createParam("f")

Filter = Connector("Filter")
Filter.createPort(PORT_IO_IN, 'A')
Filter.createPort(PORT_IO_OUT, 'B')
Filter.setTypeChannel()
Filter.createParam("f")

PTimer = Connector("pTimer")
PTimer.createPort(PORT_IO_IN, 'A')
PTimer.createPort(PORT_IO_IN, 'T')
PTimer.createPort(PORT_IO_OUT, 'B')
PTimer.setTypeChannel()
PTimer.createParam("t0")