# Composition of StochasticChoice and FIFO1

Consider the case where data items pass through the StochasticChoice first and FIFO1 later. The following shows how we perform the product operator.

```
(Idle) --[  ]-> (Ready)       (Empty) --[B1]--> (Full)
  ^                |             ^                |
  |---- [A1,B1]----|             |------[C1]------|

          (a)                            (b)
```

### composition of states


- `(Idle, Empty)` : a.Idle and b.Empty
- `(Idle, Full)` : a.Idle and b.Full
- `(Ready, Empty)` and `(Ready, Full)`

### composition of edges

Asynchonizing edges:

- `a.[ ]` -> `(Idle, Empty) --[]-> (Ready, Empty)` and `(Idle, Full) --[]-> (Ready, Full)`
- `b.[C1]` -> `(Idle, Full) --[C1]-> (Idle, Empty)` and `(Ready, Full) --[C1]-> (Ready, Empty)`

A synchronizing edge:

- `a.[A1, B1]` synchronizing with `b.[B1]` (as `B1` is shared between the two set of actions) -> `(Ready, Empty) --[A1,B1]-> (Idle, Full)`