from channels import Sync
from semantics.STAr import getSemantics
from semantics.STAr.prism import sta2prism

model, prop = sta2prism(getSemantics(Sync))
print(model, prop)