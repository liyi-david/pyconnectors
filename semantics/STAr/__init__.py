from connector import *
from .channel import getChannelSemantics
from .composition import getMixedNode
from .STA import *


def exprReform(expr, actvarmap, localvarmap):
    if isinstance(expr, Variable):
        if expr.isAdjoint:
            return actvarmap[expr.ref]
        else:
            return localvarmap[expr]
    elif isinstance(expr, BinaryExpr):
        return expr.__class__(
            exprReform(expr.l, actvarmap, localvarmap),
            exprReform(expr.r, actvarmap, localvarmap)
        )
    elif isinstance(expr, SingleExpr):
        return expr.__class__(
            exprReform(expr.expr, actvarmap, localvarmap)
        )

    return expr


def getSemantics(connector, params=None):
    assert isinstance(connector, Connector)

    if connector.isChannel:
        return getChannelSemantics(connector, params)
    else:
        s = STA()
        s.ref = connector
        actlink = {}

        def link(act1, act2):
            nonlocal actlink
            assert act1 not in actlink and act2 not in actlink
            actlink[act1] = act2
            actlink[act2] = act1


        # create actions
        for p in connector.ports:
            s.createAction("P%d %s" % (
                connector.ports.index(p),
                "IN" if p.io == PORT_IO_IN else "OUT"
            ))

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
        adjvars = {}
        nodevars = []
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

        allSTAs = list(subconns.values()) + list(nodes.values())

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

        # generate locations and transitions
        locs = [[]]
        synctrans = [[]]
        initialloc = []

        for sta in allSTAs:
            initialloc.append(sta.initialLocation)
            locsn = []
            for ln in sta.locations:
                locsn += list(map(lambda l: l + [ln], locs))

            locs = locsn

            synctransn = []
            for tn in sta.transitions + [None]:
                synctransn += list(map(lambda ts: ts + [tn], synctrans))

            synctrans = synctransn

        for i in range(len(locs)):
            s.createLocation("L%d" % i)

        s.setInitialLocation(s.locations[locs.index(initialloc)])


        # synchronize transitions
        for trans in synctrans:
            flag = True
            for t in trans:
                if t is None:
                    continue
                for a in t.actions:
                    if actlink[a].parent != s:
                        if len(list(filter(lambda t: t is not None and actlink[a] in t.actions, trans))) == 0:
                            # a action cannot be synchronized
                            flag = False
                            break
                if not flag:
                    break

            if flag and len(list(filter(lambda t: t is not None, trans))) > 0:
                # add the transition to s

                guard = ValueExpr(True)
                acts = []
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
                        .setActions(acts)

                    t.assignments = assignments


        s.variables = list(filter(lambda v: v not in nodevars, s.variables))
        return s
