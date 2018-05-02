from .STA import *
from connector import *
from .propertyexpression import *

"""
PRISM EXPORTER

- Engine used: explicit
- PTA model checking method: digital clocks

"""


def sta2prism(sta):
    model, properties = "", ""
    # type
    model += "pta\n"

    # location variables
    variable_map = dict()

    variables = []
    constants = []

    for v in sta.variables:
        if v.isAdjoint:
            vname = "d_" + v.ref.identifier.replace(" ", "")
            variable_map[v] = vname
            # if sta.ref.ports[sta.actions.index(v.ref)].io == PORT_IO_IN:
            #     constants.append("const int %s = %d;" % (vname, sta.actions.index(v.ref)))
            # else:
            variables.append("%s : int init 0;" % (vname))

            stname = "st_" + v.ref.identifier.replace(" ", "")
            variable_map[v.ref] = stname
            variables.append("%s : bool init false;" % stname)
        else:
            variable_map[v] = v.name
            variables.append("%s : %s;" % (v.name, "clock" if v.isClock else "int"))

    # generate connector clocks
    for v in sta.ref.resetClocks:
        variable_map[v] = v.name
        variables.append("%s : %s;" % (v.name, "clock" if v.isClock else "int"))

    model += "\n"

    model += "\n".join(constants)
    model += "\n\n"

    model += "module main\n\n"
    model += "\n".join(
        map(lambda line: "  " + line, variables)
    )

    model += "\n\n"
    model += "  loc: [0..%d] init %d;" % (len(sta.locations), sta.locations.index(sta.initialLocation))
    model += "\n\n"

    # generate invariants

    model += "  invariant\n"
    for loc in sta.locations:
        if loc.invariant is not None:
            model += "    (loc = %d) & (%s) &\n" % (
                sta.locations.index(loc),
                expr2prism(loc.invariant, variable_map)
            )
    model += "    (true)\n"
    model += "  endinvariant\n\n"

    for t in sta.transitions:
        actidentifier = "_".join(map(lambda act:act.identifier.replace(" ", ""), t.actions))
        guard = "(" + expr2prism(t.guard, variable_map) + ") & (loc = %d)" % sta.locations.index(t.source)

        assignments = [[1, []]]
        assignments[0][1].append("loc' = %d" % (sta.locations.index(t.target)))

        for act in sta.actions:
            assignments[0][1].append(
                "%s = %s" % (
                    variable_map[act] + "'",
                    "true" if act in t.actions else "false"
                )
            )

        for v in sta.ref.resetClocks:
            for act in t.actions:
                if act.ref in sta.ref.resetClocks[v]:
                    assignments[0][1].append(
                        "%s = %s" % (
                            v.name + "'",
                            0
                        )
                    )
                    break

        for v in t.assignments:
            daNew = []
            for p, expr in t.assignments[v].getDistribution():
                daNew += list(map(
                    lambda item: (
                        item[0] * p,
                        item[1] + ["%s = %s" % (expr2prism(v, variable_map, isPrime=True), expr2prism(expr, variable_map))]
                    ),
                    assignments
                ))

            assignments = daNew

        strassignments = " +\n    ".join(
            map(
                lambda passignments: "%f : %s" % (
                    passignments[0],
                    " & ".join(
                        map(
                            lambda exp: "(" + exp + ")",
                            passignments[1]
                        )
                    )
                ),
                assignments
            )
        )
        strassignments = "\n    " + strassignments

        model += "  [%s] %s -> %s;\n\n" % (
            "act_" + actidentifier,
            guard,
            strassignments
        )

    model += "endmodule\n"

    for name in sta.properties:
        properties += "// PROPERTY " + name + "\n"
        properties += expr2prism(sta.properties[name], variable_map) + "\n\n"

    return model, properties

def expr2prism(expr, variable_map, isPrime=False):
    if isinstance(expr, Variable):
        return variable_map[expr] + "'" if isPrime else variable_map[expr]
    elif isinstance(expr, AddExpr):
        return "(%s + %s)" % (expr2prism(expr.l, variable_map), expr2prism(expr.r, variable_map))
    elif isinstance(expr, AndExpr):
        return "(%s & %s)" % (expr2prism(expr.l, variable_map), expr2prism(expr.r, variable_map))
    elif isinstance(expr, NotExpr):
        return "(!%s)" % expr2prism(expr.expr, variable_map)
    elif isinstance(expr, LeqExpr):
        return "(%s <= %s)" % (expr2prism(expr.l, variable_map), expr2prism(expr.r, variable_map))
    elif isinstance(expr, LtExpr):
        return "(%s < %s)" % (expr2prism(expr.l, variable_map), expr2prism(expr.r, variable_map))
    elif isinstance(expr, OrExpr):
        return "(%s | %s)" % (expr2prism(expr.l, variable_map), expr2prism(expr.r, variable_map))
    elif isinstance(expr, GloballyExpr):
        return "G (%s)" % (expr2prism(expr.subFormulae, variable_map))
    elif isinstance(expr, PminExpr):
        return "Pmin=? [ %s ]" % expr2prism(expr.subFormulae, variable_map)
    elif isinstance(expr, PmaxExpr):
        return "Pmax=? [ %s ]" % expr2prism(expr.subFormulae, variable_map)
    elif isinstance(expr, ActionTriggered):
        return "(" + "&".join(
            map(lambda act: variable_map[act], expr.acts)
        ) + ")"
    elif isinstance(expr, At):
        return "(loc = %d)" % (expr.location.parent.locations.index(expr.location))
    elif isinstance(expr, Value):
        if type(expr.val) in [int, float]:
            return str(expr.val)
        elif type(expr.val) == bool:
            return "true" if expr.val else "false"
    elif isinstance(expr, FinallyExpr):
        return "(F %s)" % expr2prism(expr.subFormulae, variable_map)
    else:
        return str(expr)


def dict_add(dic, key, val):
    ndic = dict(dic)
    ndic[key] = val
    return ndic