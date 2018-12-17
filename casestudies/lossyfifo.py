from builtin import *
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism

lossyFIFO1 = Connector("lossyFIFO1")
A = lossyFIFO1.createPort(PORT_IO_IN, 'A')
B = lossyFIFO1.createPort(PORT_IO_OUT, 'B')

M = lossyFIFO1.createNode()
LossySync.connect(A, M)
FIFO1.connect(M, B)

model, prop = sta2prism(getSemantics(lossyFIFO1))
print(model)