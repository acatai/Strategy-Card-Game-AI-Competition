import std / tables
import Simple

const stateEvaluations* = toTable({
  "default": evaluateStateSimple,
  "Simple": evaluateStateSimple,
})
