# py-aiger-js
A Python library for compiling AIGs to Javascript.

[![PyPI version](https://badge.fury.io/py/py-aiger-js.svg)](https://badge.fury.io/py/py-aiger-js)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Installation

If you just need to use `aiger_js`, you can just run:

`$ pip install py-aiger-js`

For developers, note that this project uses the
[poetry](https://poetry.eustace.io/) python package/dependency
management tool. Please familarize yourself with it and then
run:

`$ poetry install`

# Usage

This example assume the `py-aiger-ptltl` library for past-tense
temporal logical is also installed.

```python
import aiger_ptl as LTL
from aiger_js import to_js  # <---- Key method

x, y = LTL.atom('x'), LTL.atom('y')

expr = x.historically() \
        .implies(y.once()) \
        .with_output('sat')

js_code = to_js(expr, suffix="1", with_header=True)
print(js_code)
```

This results in the following code being printed to the console.

```javascript
/* ------ HEADER STARTS HERE ------ */

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
/* ------ HEADER ENDS HERE ------ */


function step_1(inputs, latches) {
    var outputs = {};
    var latch_outs = {};

    if (!("bbb05df3-998a-11ea-adb4-afcccd2c8261" in latches)) { latches["bbb05df3-998a-11ea-adb4-afcccd2c8261"] = false}
    if (!("bbb05df1-998a-11ea-adb4-afcccd2c8261" in latches)) { latches["bbb05df1-998a-11ea-adb4-afcccd2c8261"] = true}

    var x1 = !inputs["y"];
    var x2 = !latches["bbb05df3-998a-11ea-adb4-afcccd2c8261"];
    var x3 = x1 && x2;
    var x4 = inputs["x"] && latches["bbb05df1-998a-11ea-adb4-afcccd2c8261"];
    var x5 = x3 && x4;
    var x6 = !x5;
    var x7 = !x3;

    outputs["sat"] = x6;
    latch_outs["bbb05df3-998a-11ea-adb4-afcccd2c8261"] = x7;
    latch_outs["bbb05df1-998a-11ea-adb4-afcccd2c8261"] = x4;

    return {"outputs": outputs, "latches": latch_outs};
}

var spec_1 = eval_factory(step_1);
```

Evaluating:
```javascript
console.log(spec_1([{"x": true, "y": true}, {"x": true, "y": false}]))
```

yields:
```javascript
{ 'sat': true }
```
