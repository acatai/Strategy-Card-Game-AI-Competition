import Engine / [Config, Draft, Search, State]
import Research / IOHelpers

proc main (): void =
  let config = getConfig()
  var input = getInput()

  for turn in 1 .. 30: echo config.evalDraft(input.readState)
  for turn in 1 .. 99: echo config.play(input.readState)

when isMainModule:
  main()
