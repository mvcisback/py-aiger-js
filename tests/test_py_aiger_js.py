import json
import tempfile
from pathlib import Path
from subprocess import check_output

import aiger_ptltl as LTL
from aiger_js.aig2js import to_js


def test_to_js_smoke():
    x, y = LTL.atom('x'), LTL.atom('y')

    expr1 = x.historically() \
             .implies(y.once()) \
             .with_output('sat')

    expr2 = x.once() \
             .implies(y.historically()) \
             .with_output('sat')

    exprs = [x, expr1, expr2, ~expr1, ~expr2, LTL.atom(True), LTL.atom(False)]
    with tempfile.TemporaryDirectory() as base:
        for expr in exprs:
            js_code = to_js(expr)

            js_code += 'var trc = [{"x": true, "y": true}, {"x": true, "y": false}]\n'  # noqa: E501
            js_code += 'console.log(JSON.stringify(spec_aig(trc)))'

            path = Path(base) / "test.js"
            with path.open('w') as f:
                f.write(js_code)

            js_result = check_output(['nodejs', str(path)], encoding='utf-8')

            result = json.loads(js_result)
            inputs = [{'x': True, 'y': True}, {'x': True, 'y': False}]
            assert expr.aig.simulate(inputs)[-1][0] == result
