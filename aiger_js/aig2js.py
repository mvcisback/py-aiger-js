import io

import attr
import funcy as fn
from aiger import to_aig
from aiger.aig import Node, Input, LatchIn


HEADER = """
function eval_factory(step) {
    return function (trace) {
        var latches = {};
        for (inputs of trace) {
            result = step(inputs, latches);
            outputs = result["outputs"];
            latches = result["latches"];
        }
        return outputs;
    };
}
"""

TEMPLATE = """
function step_{0}(inputs, latches) {{
    var outputs = {{}};
    var latch_outs = {{}};

{1}

    return {{"outputs": outputs, "latches": latch_outs}};
}}


var spec_{0} = eval_factory(step_{0});
"""


def to_js(circ, suffix="aig", with_header=True) -> str:
    """
    Outputs string with Javascript for stepping
    through AIG represented by circ.

    - suffix: controls suffix of generated step and spec code.

    - with_header: Includes prelude necessary for running generated
      code. Only needed once.
    """
    circ = to_aig(circ)

    count = 0

    def fresh():
        nonlocal count
        count += 1
        return f'x{count}'

    with io.StringIO() as buff:
        @attr.s(frozen=True, auto_attribs=True)
        class Writer:
            var: str
            gate: Node

            @fn.memoize
            def __and__(self, other):
                writer = lift(self.gate & other.gate)
                left, right = self.var, other.var
                buff.write(f'    var {writer.var} = {left} && {right};\n')
                return writer

            @fn.memoize
            def __invert__(self):
                writer = lift(~self.gate)
                buff.write(f'    var {writer.var} = !{self.var};\n')
                return writer

        @fn.memoize
        def lift(gate) -> Writer:
            if isinstance(gate, Input):
                var = f'inputs["{gate.name}"]'
            elif isinstance(gate, LatchIn):
                var = f'latches["{gate.name}"]'
            elif isinstance(gate, bool):
                var = 'false'
            else:
                var = fresh()

            return Writer(var=var, gate=gate)

        # Add latch init code:
        for name, init in circ.latch2init.items():
            init = "true" if init else "false"
            buff.write(f'    if (!("{name}" in latches)) {{ ')
            buff.write(f'latches["{name}"] = {init}')
            buff.write('}\n')
        buff.write('\n')

        # Inline gates as straight line program.
        inputs = {i: Input(i) for i in circ.inputs}
        latches = {i: LatchIn(i) for i in circ.latches}
        omap, lmap = circ(inputs, latches, lift=lift)

        # Collect outputs.
        for name, writer in omap.items():
            buff.write(f'\n    outputs["{name}"] = {writer.var};')

        # Collect outputs.
        for name, writer in lmap.items():
            buff.write(f'\n    latch_outs["{name}"] = {writer.var};')

        hdr = HEADER if with_header else ""
        return hdr + TEMPLATE.format(suffix, buff.getvalue())


__all__ = ['to_js']
