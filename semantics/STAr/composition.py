from .STA import *


def getMixedNode(numIn, numOut):
    node = STA()

    # actions, i.e. ports
    inActs = [node.createAction("I%s" % i) for i in range(numIn)]
    outActs = [node.createAction("O%s" % i) for i in range(numOut)]

    l0 = node.createLocation("l0")
    node.setInitialLocation(l0)

    # generate transitions
    for act in inActs:
        t = node.createTransition().startFrom(l0) \
            .endAt(l0) \
            .setActions([act] + outActs) \
            .setGuard(Value(True)) \

        for o in outActs:
            t.addAssignment(
                node.getVariableByAction(o),
                node.getVariableByAction(act)
            )

    return node