from .expression import *

class PropertyExpression(Expr):
    pass


class SinglePropertyOperator(PropertyExpression):
    def __init__(self, subFormulae):
        self.subFormulae = subFormulae

    def getOperator(self):
        raise Exception()

    def __str__(self):
        return "%s %s" % (self.getOperator(), str(self.subFormulae))


class Forall(SinglePropertyOperator):
    def getOperator(self):
        return "∀"


class Exists(SinglePropertyOperator):
    def getOperator(self):
        return "∃"


class Pmin(SinglePropertyOperator):
    def getOperator(self):
        return "Pmin"


class Pmax(SinglePropertyOperator):
    def getOperator(self):
        return "Pmax"

class Globally(SinglePropertyOperator):
    def getOperator(self):
        return "G"


class Finally(SinglePropertyOperator):
    def getOperator(self):
        return "F"


class Until(PropertyExpression):
    def __init__(self, l, r):
        self.l = l
        self.r = r

    def __str__(self):
        return str(self.l) + " U " + str(self.r)


class ActionTriggered(PropertyExpression):
    def __init__(self, *acts):
        if len(acts) == 1 and type(acts[0]) in [list, tuple, set]:
            self.acts = list(acts[0])
        else:
            self.acts = acts

    def __str__(self):
        return ",".join(map(lambda act:act.identifier, self.acts))


class At(PropertyExpression):
    def __init__(self, loc):
        self.location = loc

    def __str__(self):
        return "@" + self.location.identifier


class ValueOf(PropertyExpression):
    def __init__(self, p):
        self.port = p


class PortTriggered(PropertyExpression):
    def __init__(self, *ports):
        self.ports = ports