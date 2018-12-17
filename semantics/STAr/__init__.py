from connector import *

from .propertyexpression import *
from .channel import getChannelSemantics
from .composition import getMixedNode
from .STA import *


def exprReform(expr, actvarmap, localvarmap):
    if isinstance(expr, Variable):
        if expr.isAdjoint:
            return actvarmap[expr.ref]
        elif expr in localvarmap:
            return localvarmap[expr]
        else:
            return expr
    elif isinstance(expr, BinaryExpr):
        return expr.__class__(
            exprReform(expr.l, actvarmap, localvarmap),
            exprReform(expr.r, actvarmap, localvarmap)
        )
    elif isinstance(expr, UnaryExpr):
        return expr.__class__(
            exprReform(expr.expr, actvarmap, localvarmap)
        )
    elif isinstance(expr, UnaryPropertyExpr):
        return expr.__class__(
            exprReform(expr.subFormulae, actvarmap, localvarmap)
        )
    elif isinstance(expr, UntilExpr):
        return expr.__class__(
            exprReform(expr.l, actvarmap, localvarmap),
            exprReform(expr.r, actvarmap, localvarmap)
        )
    elif isinstance(expr, PortTriggered):
        return ActionTriggered(list(map(
            lambda p: actvarmap[p],
            expr.ports
        )))
    elif isinstance(expr, ValueOf):
        return expr
    return expr


def getSemantics(connector, params=None):
    assert isinstance(connector, Connector)

    if connector.isChannel:
        return getChannelSemantics(connector, params)
    else:
        s = STA()
        s.ref = connector
        actlink = {}
        adjvars = {}
        nodevars = []

        def link(act1, act2):
            nonlocal actlink
            assert act1 not in actlink and act2 not in actlink
            actlink[act1] = act2
            actlink[act2] = act1


        # create actions
        for p in connector.ports:
            adjvars[p] = s.createAction(
                "%s_%s" % (
                    p.name,
                    "IN" if p.io == PORT_IO_IN else "OUT"
                ),
                p
            )

        subconns = {}
        for conn in connector.connections:
            subconns[conn] = getSemantics(conn.ref, params=conn.params)
            for porn in conn.connected:
                if isinstance(porn, Port):
                    p = porn
                    assert p in connector.ports
                    link(
                        s.actions[connector.ports.index(p)],
                        subconns[conn].actions[conn.connected.index(p)]
                    )

        nodes = {}
        for node in connector.nodes:
            portsIn, portsOut = [], []
            for conn in connector.connections:
                if node in conn.connected:
                    index = conn.connected.index(node)
                    if conn.ref.ports[index].io == PORT_IO_OUT:
                        portsIn.append(subconns[conn].actions[index])
                    else:
                        portsOut.append(subconns[conn].actions[index])

            # generate corresponding
            nodes[node] = getMixedNode(len(portsIn), len(portsOut))
            for i in range(len(portsIn)):
                link(portsIn[i], nodes[node].actions[i])

            for i in range(len(portsOut)):
                link(portsOut[i], nodes[node].actions[i + len(portsIn)])

        # generate adjoint variables
        # only local actions are generated here
        ct = 0

        for act in actlink:
            if act in s.actions:
                adjvars[act] = s.getVariableByAction(act)
                adjvars[actlink[act]] = adjvars[act]
            elif actlink[act] in s.actions:
                adjvars[actlink[act]] = s.getVariableByAction(actlink[act])
                adjvars[act] = adjvars[actlink[act]]
            else:
                adjvars[act] = s.createVariable("V%d" % ct)
                adjvars[actlink[act]] = adjvars[act]
                nodevars.append(adjvars[act])
                ct += 1

        # ORDER is veryyyyyyyyy important !!!!!
        allSTAs = list(nodes.values()) + list(subconns.values())

        # generate local variables
        localvars = {}
        namecounter = {}
        for sta in allSTAs:
            for localvar in filter(lambda v: not v.isAdjoint, sta.variables):
                """
                rename the variables with the same name, i.e.
                v -> v_0
                v -> v_1
                ...
                """
                if localvar.name not in namecounter:
                    namecounter[localvar.name] = 0
                else:
                    namecounter[localvar.name] += 1

                localvars[localvar] = s.createVariable(localvar.name + "_" + str(namecounter[localvar.name]))
                if localvar.isClock:
                    localvars[localvar].isClock = True

        # generate locations and transitions
        locs = [[]]
        synctrans = [[]]
        initialloc = []

        proceeded_actions = []

        for sta in allSTAs:
            # print(allSTAs.index(sta), len(allSTAs), connector.name)
            initialloc.append(sta.initialLocation)
            locsn = []
            proceeded_actions += sta.actions

            for ln in sta.locations:
                locsn += list(map(lambda l: l + [ln], locs))

            locs = locsn

            synctransn = []
            for tn in sta.transitions + [None]:
                synctransn += list(map(lambda ts: ts + [tn], synctrans))

            synctrans = []
            # filter the new set of sync transitions
            for trans in synctransn:
                isvalid = True
                for t in trans:
                    if t is None:
                        continue
                    if len(t.actions) == 0:
                        if len(list(filter(lambda tr: tr is not None and tr != t, trans))) > 0:
                            isvalid = False
                            break
                    for a in t.actions:
                        if actlink[a].parent != s:
                            if len(list(filter(lambda t: t is not None and actlink[a] in t.actions, trans))) == 0 and \
                                actlink[a] in proceeded_actions:
                                    # a action cannot be synchronized
                                    isvalid = False
                                    break
                    if len(trans) == len(allSTAs) and len(list(filter(lambda lt: lt is None, trans))) == 0:
                        isvalid = False

                if isvalid:
                    synctrans.append(trans)


        for i in range(len(locs)):
            s.createLocation("L%d" % i)

        s.setInitialLocation(s.locations[locs.index(initialloc)])

        # synchronize transitions
        for trans in synctrans:
            # add the transition to s
            guard = Value(True)
            acts = []
            hided_acts = []
            source = []
            target = []
            assignments = {}

            for t in trans:
                if t is None:
                    source.append(None)
                    target.append(None)
                    continue
                else:
                    source.append(t.source)
                    target.append(t.target)
                    acts += list(filter(
                        lambda a: a in s.actions,
                        map(lambda a: actlink[a], t.actions)
                    ))
                    hided_acts += list(filter(
                        lambda a: a not in s.actions,
                        map(lambda a: actlink[a], t.actions)
                    ))

                    guard = Expr.land(
                        guard,
                        exprReform(t.guard, adjvars, localvars)
                    )

                    for var in t.assignments:
                        assignments[exprReform(var, adjvars, localvars)] = exprReform(t.assignments[var], adjvars, localvars)

            # remove all node variables
            found = True
            while found:
                found = False
                for v in assignments:
                    # check whether v is a node variable
                    if v in nodevars:
                        guard = Expr.replace(guard, v, assignments[v])
                        for vp in assignments:
                            assignments[vp] = Expr.replace(assignments[vp], v, assignments[v])

                        # remove this variable
                        del assignments[v]
                        found = True
                        break

            # re-generate all possible source-target location pairs
            locpairs = [(source, target)]
            for i in range(len(locpairs[0][0])):
                if locpairs[0][0][i] is None and locpairs[0][1][i] is None:
                    pairsnew = []
                    for l in allSTAs[i].locations:
                        pairsnew += list(
                            map(
                                lambda lpair: (
                                    lpair[0][:i] + [l] + lpair[0][i+1:],
                                    lpair[1][:i] + [l] + lpair[1][i+1:]
                                ),
                                locpairs
                            )
                        )
                    locpairs = pairsnew

            for src, tgt in locpairs:
                t = s.createTransition().startFrom(s.locations[locs.index(src)])\
                    .endAt(s.locations[locs.index(tgt)])\
                    .setGuard(guard)\
                    .setActions(acts)\
                    .setHidedActions(hided_acts)

                t.assignments = assignments

        s.variables = list(filter(lambda v: v not in nodevars, s.variables))
        for name in connector.properties:
            s.addProperty(
                name,
                exprReform(connector.properties[name], adjvars, localvars)
            )

        # simplify the transitions and solve urgency in s
        for i in reversed(range(0,len(s.transitions))):
            for j in range(0, i):
                if s.transitions[i].source == s.transitions[j].source and \
                    set(s.transitions[i].actions) == set(s.transitions[j].actions) and \
                    set(s.transitions[i].hided_actions) < set(s.transitions[j].hided_actions):
                        s.transitions[i].guard = Expr.land(
                            s.transitions[i].guard,
                            Expr.lnot(s.transitions[j].guard)
                        )

        s.transitions = list(filter(
            lambda t: (not isinstance(t.guard, Value)) or (t.guard.val != False),
            s.transitions
        ))

        return s
