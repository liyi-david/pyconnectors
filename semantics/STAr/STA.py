from .expression import *


class STA:
    def __init__(self):
        self.variables = []
        self.actions = []
        self.locations = []
        self.initialLocation = None
        self.transitions = []
        self.ref = None
        self.properties = {}

    def createAction(self, _name, _ref=None):
        a = STAAction(_name, self, _ref)
        self.actions.append(a)
        v = Variable(adjoint=a)
        self.variables.append(v)
        return a

    def createVariable(self, _name):
        v = Variable(name=_name)
        self.variables.append(v)
        return v

    def createClock(self, _name):
        v = Variable(name=_name)
        self.variables.append(v)
        v.isClock = True
        return v

    def createLocation(self, _name):
        l = STALocation(_name, self)
        self.locations.append(l)
        return l

    def setInitialLocation(self, loc):
        assert loc in self.locations
        self.initialLocation = loc

    def createTransition(self):
        t = STATransition(self)
        self.transitions.append(t)
        return t

    def getVariableByAction(self, act):
        for v in self.variables:
            if v.isAdjoint and v.ref == act:
                return v
        return None

    def addProperty(self, name, property):
        self.properties[name] = property


class STAAction:
    def __init__(self, _identifier, _parent, _ref):
        self.identifier = _identifier
        self.parent = _parent
        self.ref = _ref

    def __str__(self):
        return "%s(%s)" % (self.identifier, id(self))


class STALocation:
    def __init__(self, _identifier, _parent):
        self.identifier = _identifier
        self.invariant = None
        self.parent = _parent

    def setInvariant(self, invariant):
        self.invariant = invariant

    def __str__(self):
        return self.identifier


class STATransition:
    def __init__(self, _parent):
        assert isinstance(_parent, STA)

        self.source = None
        self.target = None
        self.actions = []
        self.hided_actions = []
        self.guard = None
        self.assignments = {}
        self.parent = _parent

    def startFrom(self, loc):
        assert loc in self.parent.locations
        self.source = loc
        return self

    def endAt(self, loc):
        assert loc in self.parent.locations
        self.target = loc
        return self

    def setActions(self, acts):
        for act in acts:
            assert isinstance(act, STAAction)

        self.actions += acts
        return self

    def setGuard(self, expr):
        assert isinstance(expr, Expr)
        self.guard = expr
        return self

    def addAssignment(self, v, expr):
        assert isinstance(expr, Expr)
        assert v in self.parent.variables
        self.assignments[v] = expr

        return self

    def setHidedActions(self, hided_actions):
        self.hided_actions = hided_actions
        return self

    def __str__(self):
        return "%s -> %s %s%s %s" % (
            str(self.source),
            str(self.target),
            "" if len(self.actions) == 0 else "ON " + ",".join(map(lambda act: str(act), self.actions)) + " ",
            "" if self.guard is None else "WHEN " + str(self.guard) + " ",
            "" if len(self.assignments) == 0 else ": " + ",".join([str(v) + " := " + str(self.assignments[v]) for v in self.assignments])
        )