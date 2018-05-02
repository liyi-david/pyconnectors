from .STA import *
from .propertyexpression import *
from channels import *

import json

def sta2jani(sta):
    automaton = {
        "name" : "main", "locations": [], "edges": [], "actions": []
    }

    model = {"jani-version": 1, "name": sta.ref.name, "features": [ "derived-operators" ], "type": "dtmc", "system": {
        "elements": [
            {
                "automaton": "main"
            }
        ]
    }, "variables": [],"constants": [], "automata": [automaton], "properties": []}

    variable_map = {}

    # append variables
    for var in sta.variables:
        if var.isAdjoint:
            if sta.ref.ports[sta.actions.index(var.ref)].io == PORT_IO_IN:
                name = "d_" + var.ref.identifier.replace(" ", "")
                model["constants"].append({
                    "name": name,
                    "type": "int",
                    "value": sta.actions.index(var.ref),
                    "comment": ""
                })
            else:
                name = "d_" + var.ref.identifier.replace(" ", "")
                model["variables"].append(
                    {
                        "name": name,
                        "type": "int",
                        "initial-value": -1,
                        "comment": ""
                    }
                )

            model["variables"].append({
                "name": "st_" + var.ref.identifier.replace(" ", ""),
                "type": "bool",
                "initial-value": False,
                "comment": ""
            })
            variable_map[var.ref] = "st_" + var.ref.identifier.replace(" ", "")
        else:
            name = var.name
            model["variables"].append(
                {
                    "name": name,
                    "type": "clock" if var.isClock else "int",
                    "initial-value": 0 if var.initialValue is None else var.initialValue,
                    "comment": ""
                }
            )

        variable_map[var] = name


    # locations
    for loc in sta.locations:
        automaton["locations"].append(
            {
                "name": loc.identifier
            }
        )

    # actions
    used_actions = []

    # transitions
    for t in sta.transitions:
        jt = {
            "location": t.source.identifier,
            "destinations": [],
            "action": "_".join(map(lambda act: act.identifier.replace(" ", ""), t.actions))
        }

        if jt["action"] == "":
            del jt["action"]
        else:
            if jt["action"] not in used_actions:
                used_actions.append(jt["action"])

        distributedAssignments = [(1, {})]

        for v in t.assignments:
            daNew = []
            for p, expr in t.assignments[v].getDistribution():
                daNew += list(map(
                    lambda item: (item[0] * p, dict_add(item[1], v, expr)),
                    distributedAssignments
                ))

            distributedAssignments = daNew

        for p, assign in distributedAssignments:
            jassign = []

            for v in assign:
                jassign.append({
                    "ref": variable_map[v],
                    "value": expr2jani(assign[v], variable_map)
                })

            for act in sta.actions:
                jassign.append({
                    "ref": variable_map[v],
                    "value": True if act in t.actions else False
                })


            jt["destinations"].append({
                "location": t.target.identifier,
                "probability": {
                    "exp": p
                },
                "assignments": jassign
            })

        jt["guard"] = {
            "exp": expr2jani(t.guard, variable_map)
        }
        automaton["edges"].append(jt)

    model["actions"] = list(map(lambda actid: {"name": actid}, used_actions))
    for name in sta.properties:
        model["properties"].append({
            "name": name,
            "expression": expr2jani(sta.properties[name], variable_map),
            "comment":""
        })
    return json.dumps(model, indent="  ")


def expr2jani(expr, variable_map):
    if isinstance(expr, Variable):
        return variable_map[expr]
    elif isinstance(expr, Value):
        return expr.val
    elif isinstance(expr, BinaryExpr):
        return {
            "op": expr.getOperator(),
            "left": expr2jani(expr.l, variable_map),
            "right": expr2jani(expr.r, variable_map)
        }
    elif isinstance(expr, UnaryExpr):
        return {
            "op": expr.getOperator(),
            "exp": expr2jani(expr.expr, variable_map)
        }
    elif isinstance(expr, UnaryPropertyExpr):
        return {
            "op": expr.getOperator(),
            "exp": expr2jani(expr.subFormulae, variable_map)
        }
    elif isinstance(expr, ActionTriggered):
        newexpr = None
        for act in expr.acts:
            newexpr = variable_map[act] if newexpr is None else {
                "op": "∧",
                "left": variable_map[act],
                "right": newexpr
            }

        return newexpr


def dict_add(dic, key, val):
    ndic = dict(dic)
    ndic[key] = val
    return ndic