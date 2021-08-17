import std / [parseopt, random, strformat, strutils]
import Engine / Cards
import Research / [IOHelpers, Referee]

type
  Options = tuple[
    games: int,
    verbose: bool
  ]

proc getOptions (): Options =
  for kind, key, value in getOpt():
    if key == "games": result.games = value.parseInt
    if key == "verbose": result.verbose = value.parseBool

proc main (): void =
  let (games, verbose) = getOptions()
  let player1 = getConfig("p1-")
  let player2 = getConfig("p2-")
  let cards = getCards()
  var wins = 0

  randomize()

  for game in 1 .. games:
    # FIXME: Implement draft from options
    let draft = newDraft(cards)

    if play(player1, player2, draft, verbose):
      wins += 1

    let proc1 = 100 * wins / game
    let proc2 = 100 - proc1
    echo &"{stamp()} Stats {game:>3}: {proc1:6.2f}% {proc2:6.2f}%"

when isMainModule:
  main()
