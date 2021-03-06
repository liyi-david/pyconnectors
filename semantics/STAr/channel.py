from channels import *
from .STA import *
from .propertyexpression import *


def getChannelSemantics(channel, params):

    # --------------------------------------------------------------------------------
    if channel == Sync:
        s = STA()
        A = s.createAction("A")
        B = s.createAction("B")
        l0 = s.createLocation("l0")
        s.setInitialLocation(l0)
        s.createTransition()\
            .startFrom(l0)\
            .endAt(l0)\
            .setActions([A, B])\
            .setGuard(Value(True))\
            .addAssignment(s.getVariableByAction(B), s.getVariableByAction(A))

        s.addProperty("p0", Property.G(Expr.derive(ActionTriggered(A), ActionTriggered(B))))
        s.ref = Sync
        return s

    # --------------------------------------------------------------------------------
    if channel == SyncDrain:
        s = STA()
        A = s.createAction("A")
        B = s.createAction("B")
        l0 = s.createLocation("l0")
        s.setInitialLocation(l0)
        s.createTransition()\
            .startFrom(l0)\
            .endAt(l0)\
            .setActions([A, B]) \
            .setGuard(Value(True))

        s.ref = SyncDrain
        return s

    # --------------------------------------------------------------------------------

    if channel == LossySync:
        s = STA()
        A = s.createAction("A")
        B = s.createAction("B")
        l0 = s.createLocation("l0")
        s.setInitialLocation(l0)
        s.createTransition()\
            .startFrom(l0)\
            .endAt(l0)\
            .setActions([A, B])\
            .setGuard(Value(True))\
            .addAssignment(s.getVariableByAction(B), s.getVariableByAction(A))

        s.createTransition()\
            .startFrom(l0)\
            .endAt(l0)\
            .setActions([A]) \
            .setGuard(Value(True))

        s.ref = LossySync
        return s

    # --------------------------------------------------------------------------------

    if channel == FIFO1:
        s = STA()
        A = s.createAction("A")
        B = s.createAction("B")
        buf = s.createVariable("buf")
        empty = s.createLocation("empty")
        full = s.createLocation("full")
        s.setInitialLocation(empty)

        s.createTransition()\
            .startFrom(empty)\
            .endAt(full)\
            .setActions([A]) \
            .setGuard(Value(True))\
            .addAssignment(buf, s.getVariableByAction(A))

        s.createTransition()\
            .startFrom(full)\
            .endAt(empty)\
            .setActions([B])\
            .setGuard(Value(True)) \
            .addAssignment(s.getVariableByAction(B), buf)\
            .addAssignment(buf, Value(0))

        if params is not None and 'default_value' in params:
            # the FIFO is not empty
            default = s.createLocation("default")
            s.setInitialLocation(default)
            s.createTransition() \
                .startFrom(default) \
                .endAt(full) \
                .setActions([]) \
                .setGuard(Value(True)) \
                .addAssignment(buf, params['default_value'])


        s.ref = FIFO1
        return s

    # --------------------------------------------------------------------------------

    if channel == StochasticChoice:
        s = STA()
        A = s.createAction("A")
        B = s.createAction("B")
        sample = s.createVariable("sample")
        idle = s.createLocation("idle")
        prepared = s.createLocation("prepared")
        s.setInitialLocation(idle)

        s.createTransition()\
            .startFrom(idle)\
            .endAt(prepared)\
            .setActions([]) \
            .setGuard(Value(True))\
            .addAssignment(sample, params['dist'])

        s.createTransition()\
            .startFrom(prepared)\
            .endAt(idle)\
            .setActions([A, B])\
            .setGuard(Value(True)) \
            .addAssignment(s.getVariableByAction(B), sample)

        s.ref = StochasticChoice
        return s

    # --------------------------------------------------------------------------------
    if channel == Filter:
        s = STA()
        A = s.createAction("A")
        B = s.createAction("B")
        l0 = s.createLocation("l0")
        v, expr = params['f']
        s.setInitialLocation(l0)
        s.createTransition() \
            .startFrom(l0) \
            .endAt(l0) \
            .setActions([A, B]) \
            .setGuard(Expr.replace(expr, v, s.getVariableByAction(A))) \
            .addAssignment(s.getVariableByAction(B), s.getVariableByAction(A))

        s.createTransition() \
            .startFrom(l0) \
            .endAt(l0) \
            .setActions([A]) \
            .setGuard(Expr.lnot(Expr.replace(expr, v, s.getVariableByAction(A))))

        s.ref = Filter
        return s

    # --------------------------------------------------------------------------------
    if channel == Map:
        s = STA()
        A = s.createAction("A")
        B = s.createAction("B")
        l0 = s.createLocation("l0")
        v, expr = params['f']
        s.setInitialLocation(l0)
        s.createTransition() \
            .startFrom(l0) \
            .endAt(l0) \
            .setActions([A, B]) \
            .setGuard(Value(True)) \
            .addAssignment(s.getVariableByAction(B), Expr.replace(s.getVariableByAction(A), v, expr))

        s.ref = Map
        return s

    # --------------------------------------------------------------------------------
    if channel == PTimer:
        s = STA()
        A = s.createAction("A")
        T = s.createAction("T")
        B = s.createAction("B")
        idle = s.createLocation("idle")
        pending = s.createLocation("pending")

        t = s.createClock("t")
        tmax = s.createVariable("tmax")
        t0 = params['t0']
        tmax.setInitialValue(t0)

        pending.setInvariant(Expr.leq(t, tmax))

        TIMEOUT = Value(-1)

        s.setInitialLocation(idle)

        # transition from idle to pending

        s.createTransition() \
            .startFrom(idle) \
            .endAt(pending) \
            .setActions([A]) \
            .setGuard(Value(True)) \
            .addAssignment(t, Value(0))

        s.createTransition() \
            .startFrom(idle) \
            .endAt(idle) \
            .setActions([T]) \
            .setGuard(Value(True)) \
            .addAssignment(tmax, s.getVariableByAction(T))

        s.createTransition() \
            .startFrom(idle) \
            .endAt(pending) \
            .setActions([A, T]) \
            .setGuard(Value(True)) \
            .addAssignment(t, Value(0)) \
            .addAssignment(tmax, s.getVariableByAction(T))


        # transitions from pending to idle

        s.createTransition() \
            .startFrom(pending) \
            .endAt(idle) \
            .setActions([]) \
            .setGuard(Expr.eq(t, tmax))

        s.createTransition() \
            .startFrom(pending) \
            .endAt(idle) \
            .setActions([T]) \
            .setGuard(Value(True)) \
            .addAssignment(tmax, s.getVariableByAction(T))

        s.createTransition() \
            .startFrom(pending) \
            .endAt(idle) \
            .setActions([B]) \
            .setGuard(Expr.eq(t, tmax)) \
            .addAssignment(s.getVariableByAction(B), TIMEOUT)

        s.createTransition() \
            .startFrom(pending) \
            .endAt(idle) \
            .setActions([B, T]) \
            .setGuard(Expr.eq(t, tmax)) \
            .addAssignment(s.getVariableByAction(B), TIMEOUT) \
            .addAssignment(tmax, s.getVariableByAction(T))


        # self-loop transitions of pTimer
        s.createTransition() \
            .startFrom(pending) \
            .endAt(pending) \
            .setActions([A, B]) \
            .setGuard(Expr.eq(t, tmax)) \
            .addAssignment(t, Value(0)) \
            .addAssignment(s.getVariableByAction(B), TIMEOUT)

        s.createTransition() \
            .startFrom(pending) \
            .endAt(pending) \
            .setActions([A, B, T]) \
            .setGuard(Expr.eq(t, tmax)) \
            .addAssignment(t, Value(0)) \
            .addAssignment(s.getVariableByAction(B), TIMEOUT) \
            .addAssignment(tmax, s.getVariableByAction(T))

        s.properties['afterA'] = PminExpr(GloballyExpr(
            Expr.derive(
                ActionTriggered(A),
                At(pending)
            )
        ))

        s.ref = PTimer
        return s