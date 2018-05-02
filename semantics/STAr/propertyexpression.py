from .expression import *


class Property(Expr):
    @classmethod
    def A(cls, subFormulae):
        return ForallExpr(subFormulae)

    @classmethod
    def E(cls, subFormulae):
        return ExistsExpr(subFormulae)

    @classmethod
    def G(cls, subFormulae):
        return GloballyExpr(subFormulae)

    @classmethod
    def F(cls, subFormulae):
        return FinallyExpr(subFormulae)

    @classmethod
    def Pmin(cls, subFormulae):
        return PminExpr(subFormulae)

    @classmethod
    def Pmax(cls, subFormulae):
        return PmaxExpr(subFormulae)

    @classmethod
    def U(cls, formulaeL, formulaeR):
        return UntilExpr(formulaeL, formulaeR)


class UnaryPropertyExpr(Property):
    def __init__(self, subFormulae):
        self.subFormulae = subFormulae

    def getOperator(self):
        raise Exception()

    def __str__(self):
        return "%s %s" % (self.getOperator(), str(self.subFormulae))


class ForallExpr(UnaryPropertyExpr):
    def getOperator(self):
        return "∀"


class ExistsExpr(UnaryPropertyExpr):
    def getOperator(self):
        return "∃"


class PminExpr(UnaryPropertyExpr):
    def getOperator(self):
        return "Pmin"


class PmaxExpr(UnaryPropertyExpr):
    def getOperator(self):
        return "Pmax"


class GloballyExpr(UnaryPropertyExpr):
    def getOperator(self):
        return "G"


class FinallyExpr(UnaryPropertyExpr):
    def getOperator(self):
        return "F"


class UntilExpr(Property):
    def __init__(self, l, r):
        self.l = l
        self.r = r

    def __str__(self):
        return str(self.l) + " U " + str(self.r)


class ActionTriggered(Property):
    def __init__(self, *acts):
        if len(acts) == 1 and type(acts[0]) in [list, tuple, set]:
            self.acts = list(acts[0])
        else:
            self.acts = acts

    def __str__(self):
        return ",".join(map(lambda act:act.identifier, self.acts))


class At(Property):
    def __init__(self, loc):
        self.location = loc

    def __str__(self):
        return "@" + self.location.identifier


class ValueOf(Property):
    def __init__(self, p):
        self.port = p


class PortTriggered(Property):
    def __init__(self, *ports):
        self.ports = ports