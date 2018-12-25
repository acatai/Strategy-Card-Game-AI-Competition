import std / [strformat, times]
import .. / .. / Engine / [Action, Config, Search, State]

proc playerAlgorithmDFS * (config: Config, state: State): SearchResult =
  block:
    result = SearchResult(score: NegInf)

    let time = cpuTime()

    var states: array[16, State]
    var statesPointer = 0
    var legals: array[20, seq[Action]]
    var legalsPointers: array[16, int]

    states[0] = state
    legals[0] = state.computeActions

    while cpuTime() - time < config.time:
      when not defined(release):
        echo &""
        echo &"result: {result}"
        echo &"A:      {legalsPointers[statesPointer]}"
        echo &"B:      {legals[statesPointer].len} {legals[statesPointer]}"

      if legalsPointers[statesPointer] >= legals[statesPointer].len:
        statesPointer -= 1
        if statesPointer < 0:
          break
        legalsPointers[statesPointer] += 1
        continue

      var next = states[statesPointer].copy
      next.applyAction(legals[statesPointer][legalsPointers[statesPointer]])

      statesPointer += 1
      states[statesPointer] = next
      legals[statesPointer] = next.computeActions
      legalsPointers[statesPointer] = 0

      if legals[statesPointer].len == 0:
        let score = config.evalState(states[statesPointer])
        if score > result.score:
          result.actions.newSeq(statesPointer)
          for index in 0 ..< statesPointer:
            result.actions[index] = legals[index][legalsPointers[index]]
          result.score = score

          if score > 1000:
            break
