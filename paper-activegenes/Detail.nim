{.experimental: "parallel".}

import Engine / [Card, Cards, Config, Draft, State]
import Research / [IOHelpers, Referee]
import std / [
  ospaths,
  parseopt,
  random,
  re,
  sequtils,
  strformat,
  strutils,
  tables,
  threadpool
]

func toConfig (individual: array[160, float]): Config =
  let lookup = func (card: Card): float = individual[card.cardNumber - 1]

  result = newConfig(player = "Greedy")
  result.evalDraftFn = func (config: Config, state: State): DraftResult =
    state.evaluateDraftWith(lookup)

proc readBests (path: string, n: int = 5): seq[Config] =
  let text = toSeq(path.lines())
  let data = text[^n .. text.high]
  for line in data:
    var index = 0
    var params: array[160, float]
    for param in line.replacef(re"^.*\[(.*)\]$", "$1").split(", "):
      params[index] = parseFloat(param)
      index += 1

    result.add(params.toConfig)

proc main (): void =
  randomize()

  let cards = getCards()
  var games = 1
  var drafts = newSeqWith(1, newDraft(cards))
  var players = toOrderedTable({
    "ClosetAI": @[newConfig(draft = "ClosetAI", player = "Greedy")],
    "Icebox": @[newConfig(draft = "Icebox", player = "Greedy")]
  })

  for kind, key, value in getOpt():
    if kind == cmdArgument:
      let groupName = key.extractFilename().split(".", 1)[0]
      if not (groupName in players):
        players[groupName] = @[]
      for individual in readBests(key):
        players[groupName].add(individual)
    elif key == "drafts":
      drafts = newSeqWith(value.parseInt, newDraft(cards))
    elif key == "games":
      games = value.parseInt

  var plays = 0
  var table = initTable[tuple[x: string, y: string], float]()
  for x, xs in players.pairs:
    for y, ys in players.pairs:
      if x != y:
        echo &"# {stamp()} {x} vs {y}"
        let scoreWin = 100 / (2 * games * drafts.len * xs.len * ys.len).float
        for playerX in xs:
          for playerY in ys:
            for game in 1 .. games:
              parallel:
                for draft in drafts:
                  let win = spawn play(playerX, playerY, draft)
                  let who = if win: (x, y) else: (y, x)
                  table[who] = table.getOrDefault(who, 0) + scoreWin
                  plays += 1

  echo &"# {stamp()} Plays total {plays}"

  var spans = initOrderedTable[string, int]()
  spans[""] = max(toSeq(players.keys).mapIt(it.len))
  for x, xs in players.pairs:
    spans[x] = max(6, x.len)
  spans["Average"] = 7

  stdout.write("".align(spans[""]))
  for x, xs in players.pairs:
    stdout.write(&" | {x.align(spans[x])}")
  stdout.writeLine(" | Average")

  for x, xs in players.pairs:
    stdout.write(x.alignLeft(spans[""]))
    var average = 0.0
    for y, ys in players.pairs:
      if x != y: average += table[(x, y)] / (players.len - 1).float
      let score = if x == y: "-" else: &"{table[(x, y)]:.2f}%"
      stdout.write(&" | {score.align(spans[y])}")
    let averageOut = &"{average:.2f}%"
    stdout.writeLine(&" | {averageOut.align(spans[\"Average\"])}")

when isMainModule:
  main()
