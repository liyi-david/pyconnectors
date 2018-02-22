def isdist(func):
    def checkafter(self):
        dist = func(self)
        pall = 0
        for p, _ in dist:
            pall += p

        assert (pall == 1)
        return dist

    return checkafter

class Expr:
    @classmethod
    def replace(cls, expr, var, varexpr):
        if isinstance(expr, Variable) and expr == var:
            return varexpr
        elif isinstance(expr, BinaryExpr):
            return expr.__class__(
                Expr.replace(expr.l, var, varexpr),
                Expr.replace(expr.r, var, varexpr)
            )
        elif isinstance(expr, SingleExpr):
            return expr.__class__(
                Expr.replace(expr.expr, var, varexpr)
            )
        else:
            return expr

    @classmethod
    def land(cls, l, r):
        if isinstance(l, ValueExpr) and l.val == True:
            return r
        elif isinstance(r, ValueExpr) and r.val == True:
            return l
        else:
            return AndExpr(l, r)


    @classmethod
    def lnot(cls, expr):
        return NotExpr(expr)

    @classmethod
    def eq(cls, l, r):
        return EqExpr(l, r)

    @isdist
    def getDistribution(self):
        raise Exception("getDistribution not defined")


class SingleExpr(Expr):
    def __init__(self, expr):
        self.expr = expr
        super().__init__()

    @isdist
    def getDistribution(self):
        dist = self.expr.getDistribution()
        for p in dist:
            dist[p] = self.__class__(dist[p])


    def getOperator(self):
        raise Exception("Unimplemented Method")

    def __str__(self):
        return "%s %s" % (self.getOperator(), str(self.expr))


class NotExpr(SingleExpr):
    def __init__(self, expr):
        super().__init__(expr)

    def getOperator(self):
        return "¬"


class BinaryExpr(Expr):
    def __init__(self, l, r):
        if not isinstance(l, Expr):
            l = ValueExpr(l)
        if not isinstance(r, Expr):
            r = ValueExpr(r)

        self.l = l
        self.r = r
        super().__init__()

    @isdist
    def getDistribution(self):
        distl = self.l.getDistribution()
        distr = self.r.getDistribution()

        dist = []
        for pl, exprl in distl:
            for pr, exprr in distr:
                # todo
                pass

        return dist

    def getOperator(self):
        raise Exception("Unimplemented Method")

    def __str__(self):
        return "%s %s %s" % (str(self.l), self.getOperator(), str(self.r))


class AddExpr(BinaryExpr):
    def getOperator(self):
        return "+"


class AndExpr(BinaryExpr):
    def getOperator(self):
        return "∧"

class EqExpr(BinaryExpr):
    def getOperator(self):
        return "="


class DeriveExpr(BinaryExpr):
    def getOperator(self):
        return "⇒"


class ValueExpr(Expr):
    def __init__(self, val):
        self.val = val
        super()

    @isdist
    def getDistribution(self):
        return [(1, self)]

    def __str__(self):
        return str(self.val)

class Variable(Expr):
    def __init__(self, adjoint=None, name=None):
        self.isClock = False
        if adjoint is not None:
            self.isAdjoint = True
            self.ref = adjoint
        else:
            self.isAdjoint = False
            self.name = name

        self.initialValue = None

    @isdist
    def getDistribution(self):
        return [(1, self)]

    def setInitialValue(self, val):
        self.initialValue = val

    def __str__(self):
        if self.isAdjoint:
            return "✉ %s" % str(self.ref)
        else:
            return self.name


class Distribution(Expr):
    def __init__(self):
        pass


class BinaryDistribution(Distribution):
    def __init__(self, p0):
        """
        a distribution that generates 0 or 1
        :param p0: p0 is the probability where 0 is generated
        """
        self.p0 = p0
        super().__init__()

    def __str__(self):
        return "B(%s, %s)" % (self.p0, 1 - self.p0)

    @isdist
    def getDistribution(self):
        return [
            (self.p0, ValueExpr(0)),
            (1 - self.p0, ValueExpr(1))
        ]