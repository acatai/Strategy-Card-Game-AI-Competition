import std / [osproc, parseopt, strformat, strutils]
import Engine / Input
import Research / IOHelpers

when isMainModule:
  proc main(): void =
    var referee: string
    var player1: string
    var player2: string

    var replays = false
    var threads = countProcessors()
    var plain = false
    var games = 0
    var sofar = 0
    var wins1 = 0
    var wins2 = 0

    for kind, key, value in getOpt():
      if key == "games":   games   = value.parseInt
      if key == "plain":   plain   = value.parseBool
      if key == "player1": player1 = value
      if key == "player2": player2 = value
      if key == "referee": referee = value
      if key == "replays": replays = value.parseBool
      if key == "threads": threads = value.parseInt

    if not plain:
      echo &"{stamp()} Referee: {referee}"
      echo &"{stamp()} Player1: {player1}"
      echo &"{stamp()} Player2: {player2}"
      echo &"{stamp()} Games:   {games}"
      echo &"{stamp()} Replays: {replays}"
      echo &"{stamp()} Threads: {threads}"

    var commands = newSeq[string](games)
    for index in commands.low .. commands.high:
      commands[index] = &"""{referee} -p1 "{player1}" -p2 "{player2}" -d "draftChoicesSeed={index:03} seed={index:03} shufflePlayer0Seed={index:03} shufflePlayer1Seed={index:03}""""

    discard execProcesses(
      cmds = commands,
      n = threads,
      options = {poStdErrToStdOut},
      afterRunEvent = proc (id: int; process: Process) =
        var output = process.outputStream.newInput
        let score1 = output.getInt
        let score2 = output.getInt
        let error = score1 < 0 or score2 < 0

        sofar += 1
        wins1 += score1.max(0)
        wins2 += score2.max(0)

        # In this mode only final results are reported.
        if plain:
          return

        if score1 < 0 or score2 < 0:
          echo &"{stamp()} End of game {sofar:>3}: ERRORED {score1} {score2}"
        else:
          let total = wins1 + wins2
          let index = total - 1
          let proc1 = 100 * wins1 / total
          let proc2 = 100 * wins2 / total
          echo &"{stamp()} End of game {sofar:>3}: {proc1:6.2f}% {proc2:6.2f}%"

        if error or replays:
          echo &"{stamp()} Replay game {sofar:>3}: {commands[sofar - 1]} -s"
    )

    if plain:
      echo &"{wins1} {wins2}"

  main()
