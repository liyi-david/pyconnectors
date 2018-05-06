# pyconnectors
a python library to compose Reo connectors and render them in PRISM and JANI specification

## declare a channel and its semantics as STAr

Basic channels are declared in `/channels.py`, for example, a `sync` channel is defined as

    Sync = Connector("Sync")
    Sync.createPort(PORT_IO_IN)
    Sync.createPort(PORT_IO_OUT)
    Sync.setTypeChannel()

and its semantics are provided in `/semantics/STAr/channel.py` as

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
        .setGuard(ValueExpr(True))\
        .addAssignment(s.getVariableByAction(B), s.getVariableByAction(A))

    s.addProperty("p0", Globally(DeriveExpr(ActionTriggered(A), ActionTriggered(B))))
    s.ref = Sync
    return s
    
 Users are able to extend this framework with their own channels by modifying the two files.
 
 ## composition
 
 It is very easy to construct complex connectors from channels and other connectors. `/builtin.py` provides a set of examples for this.
 
 For example, a FIFO2 that is composed of two FIFO1 channels can be written as:
 
    """
    ARCHITECTURE OF A FIFO2

    IN --[]--> M --[]--> OUT
    """
    
    FIFO2 = Connector("FIFO2")
    IN = FIFO2.createPort(PORT_IO_IN)
    OUT = FIFO2.createPort(PORT_IO_OUT)

    M = FIFO2.createNode()

    FIFO1.connect(IN, M)
    FIFO1.connect(M, OUT)
    
## property specification and model checking

PTCTL is used as our property specification. Currently supported operators are specified in `/semantics/STAr/propertyexpression.py`.

A connector with properties specified can be exported to JANI and PRISM format.

    pta

    const int d_P0IN = 0;

    module main

      st_P0IN : bool init false;
      d_P1OUT : int init 0;
      st_P1OUT : bool init false;
      d_P2OUT : int init 0;
      st_P2OUT : bool init false;
      sample_0 : int;

      loc: [0..2] init 0;

      invariant
        (true)
      endinvariant

      [act_P1OUT_P0IN] (sample_0 = 1) & (loc = 1) -> 
        1.000000 : (loc' = 0) & (st_P0IN' = true) & (st_P1OUT' = true) & (st_P2OUT' = false) & (d_P1OUT' = d_P0IN);

      [act_P2OUT_P0IN] ((!sample_0 = 1)) & (loc = 1) -> 
        1.000000 : (loc' = 0) & (st_P0IN' = true) & (st_P1OUT' = false) & (st_P2OUT' = true) & (d_P2OUT' = d_P0IN);

      [act_] (true) & (loc = 0) -> 
        0.200000 : (loc' = 1) & (st_P0IN' = false) & (st_P1OUT' = false) & (st_P2OUT' = false) & (sample_0' = 0) +
        0.800000 : (loc' = 1) & (st_P0IN' = false) & (st_P1OUT' = false) & (st_P2OUT' = false) & (sample_0' = 1);

    endmodule

    // PROPERTY reliable
    Pmin=? [ G (((!(st_P0IN)) | ((st_P1OUT) | (st_P2OUT)))) ]
