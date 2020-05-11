{.experimental: "parallel".}

import Engine / [Card, Cards, Config, Draft, State]
import Research / [IOHelpers, Referee]
import std / [
  algorithm,
  math,
  random,
  sequtils,
  strformat,
  strutils,
  threadpool
]

const
  # experimental
  activeDrafts {.intdefine.} = 1

  # entrypoint
  mode {.strdefine.} = "default"

  # evolveNormals, evolveToBests, randomExhaustive, randomTournament
  draftsEval {.intdefine.} = 100
  generations {.intdefine.} = 1000
  populationSize {.intdefine.} = 100
  scoreGames {.intdefine.} = 25

  # evolveNormals, evolveToBests
  tournamentSize {.intdefine.} = 4

  # evolveNormals
  elites {.intdefine.} = 0

  # evolveToBests
  bestsSize {.intdefine.} = 5
  mergeAllGenes {.intdefine.} = 0
  mergeEval {.intdefine.} = 10
  mergeGene {.intdefine.} = 0
  mutationProbability {.intdefine.} = 5
  scoreRounds {.intdefine.} = 2
  tournamentGames {.intdefine.} = 10

  # plotBaselines
  baselineDrafts {.intdefine.} = 100
  baselinesGames {.intdefine.} = 25

  # plotChampions
  bestsGames {.intdefine.} = 25
  champions {.intdefine.} = 5
  randoms {.intdefine.} = 5

  # plotEvolution
  progressDrafts {.intdefine.} = 250
  progressEnemies {.intdefine.} = 10
  progressGames {.intdefine.} = 25

type
  Baseline = tuple[drafts: Drafts, evaluator: string, title: string]
  Individual = ref object
    eval: float
    gene: array[160, float]
  Bests = array[generations, array[bestsSize, Individual]]
  Drafts = seq[Draft]
  Parents = array[2, Individual]
  Population = array[populationSize, Individual]

func lerp100 (x: float, y: float, percent: float): float {.inline.} =
  (x * percent + y * (100 - percent)) / 100

func toSummary (id: int, avg: float, bests: openArray[Individual]): string =
  let scores = bests.mapIt(&"{it.eval:5.2f}").join(" ")
  &"Generation {id + 1:4}: avg={avg:5.2f} top{bests.len}=[{scores}]"

func toConfig (individual: Individual): Config =
  let lookup = func (card: Card): float = individual.gene[card.cardNumber - 1]

  result = newConfig(player = "Greedy")
  result.evalDraftFn = func (config: Config, state: State): DraftResult =
    state.evaluateDraftWith(lookup)

proc newIndividual (initialize: bool): Individual =
  result = Individual()
  if initialize:
    result.eval = 50.0
    for index in 0 ..< 160:
      result.gene[index] = rand(1.0)

proc newPopulation (initialize: bool = false): Population =
  for index in result.low .. result.high:
    result[index] = newIndividual(initialize)

func cmp (x, y: Individual): int =
  cmp(x.eval, y.eval)

var plays {.global.} = 0
proc play (x, y: Individual, draft: Draft): bool {.inline.} =
  plays += 1
  play(x.toConfig, y.toConfig, draft)

proc roulette (population: Population, eval: float): Individual =
  var score = rand(eval)
  for individual in population:
    score -= individual.eval
    if score <= 0.0:
      return individual

  population[population.high]

proc selectParents (population: Population, drafts: openArray[Draft]): Parents =
  var tournamentIds: array[populationSize, int]
  for index in 0 ..< populationSize:
    tournamentIds[index] = index
  tournamentIds.shuffle

  var tournament: array[tournamentSize, Individual]
  for index in 0 ..< tournamentSize:
    tournament[index] = population[tournamentIds[index]]

  for index in 0 ..< populationSize:
    tournamentIds[index] = 0

  for draft in drafts:
    parallel:
      for indexA, a in tournament:
        for indexB, b in tournament:
          if indexA == indexB:
            continue

          for _ in 1 .. tournamentGames:
            let winX = spawn play(a, b, draft)
            let winY = spawn play(b, a, draft)
            if winX: tournamentIds[indexA] += 1
            if winY: tournamentIds[indexB] += 1

  var best1: int = if tournamentIds[0] > tournamentIds[1]: 0 else: 1
  var best2: int = 1 - best1
  for index in 2 ..< tournamentSize:
    if tournamentIds[index] > tournamentIds[best1]:
      best2 = best1
      best1 = index
      continue
    if tournamentIds[index] > tournamentIds[best2]:
      best2 = index
      continue

  [tournament[best1], tournament[best2]]

proc selectParentsSorted (population: Population): Parents =
  var best1: int = populationSize - 1
  var best2: int = populationSize - 2
  for _ in 1 .. tournamentSize:
    let index = rand(populationSize)
    if index < best1:
      best2 = best1
      best1 = index
      continue
    if index < best2:
      best2 = index
      continue

  [population[best1], population[best2]]

func sumEvals (population: openArray[Individual]): float =
  for individual in population:
    result += individual.eval

proc evolveNormals (bests: var Bests, drafts: Drafts): void =
  var offspring  = newPopulation()
  var population = newPopulation(true)
  let scoreWin = 100 / (4 * draftsEval * scoreGames * (populationSize - 1))

  proc score(population: var Population): void =
    for individual in population:
      individual.eval = 0

    for draft in drafts:
      parallel:
        for indexA, a in population:
          for indexB, b in population:
            if indexA == indexB:
              continue

            for _ in 1 .. scoreGames:
              let winX = spawn play(a, b, draft)
              let winY = spawn play(b, a, draft)
              if winX: a.eval += scoreWin else: b.eval += scoreWin
              if winY: b.eval += scoreWin else: a.eval += scoreWin

  # Init()
  population.score()
  population.sort(cmp, Descending)

  for generation in 0 ..< generations:
    for index in countup(0, populationSize - 2, 2):
      let parents = selectParentsSorted(population)

      # CrossoverChildren()
      var child1 = offspring[index + 0]
      var child2 = offspring[index + 1]

      for gene in 0 ..< 160:
        let pickA = rand(1)
        let pickB = 1 - pickA
        child1.gene[gene] = parents[pickA].gene[gene]
        child2.gene[gene] = parents[pickB].gene[gene]

      # MutateChildren()
      for gene in 0 ..< 160:
        if mutationProbability > rand(100): child1.gene[gene] = rand(1.0)
        if mutationProbability > rand(100): child2.gene[gene] = rand(1.0)

    # Elitism()
    for index in 0 ..< elites:
      offspring[index].gene = population[index].gene

    # ScoreChildrenPopulation()
    population = offspring
    population.score()
    population.sort(cmp, Descending)

    for index in 0 ..< bestsSize:
      bests[generation][index] = population[index]

    let avg = sumEvals(population) / populationSize.float
    echo &"# {stamp()} {toSummary(generation, avg, bests[generation])}"

proc evolveToBests (bests: var Bests, draftss: array[activeDrafts, Drafts]): void =
  var offspring  = newPopulation()
  var population = newPopulation(true)

  for generation in 0 ..< generations:
    let drafts = draftss.mapIt(it[generation])
    for index in countup(0, populationSize - 2, 2):
      let parents = selectParents(population, drafts)

      # CrossoverChildren()
      var child1 = offspring[index + 0]
      var child2 = offspring[index + 1]

      child1.eval = 0.0
      child2.eval = 0.0

      for gene in 0 ..< 160:
        let pickA = rand(1)
        let pickB = 1 - pickA
        child1.gene[gene] = parents[pickA].gene[gene]
        child2.gene[gene] = parents[pickB].gene[gene]

      # MutateChildren()
      for gene in 0 ..< 160:
        if mutationProbability > rand(100): child1.gene[gene] = rand(1.0)
        if mutationProbability > rand(100): child2.gene[gene] = rand(1.0)

    # ScoreChildrenPopulation()
    let scoreWin = 100.0 / (2.0 * scoreGames * scoreRounds)
    for round in 1 .. scoreRounds:
      offspring.sort(cmp, Descending)

      for index in countup(0, populationSize - 2, 2):
        let a = offspring[index + 0]
        let b = offspring[index + 1]
        for draft in drafts:
          parallel:
            for game in 1 .. scoreGames:
              let winX = spawn play(a, b, draft)
              let winY = spawn play(b, a, draft)
              if winX: a.eval += scoreWin else: b.eval += scoreWin
              if winY: b.eval += scoreWin else: a.eval += scoreWin

    # PopulationSelectMerge()
    var populationEval = sumEvals(population)
    var offspringEval = sumEvals(offspring)

    var nextPopulation = newPopulation()
    for next in nextPopulation:
      let x = roulette(population, populationEval)
      let y = roulette(offspring, offspringEval)

      next.eval = lerp100(y.eval, x.eval, mergeEval)
      next.gene = x.gene

      when mergeAllGenes == 0:
        for draft in drafts:
          for pick in draft:
            for card in pick:
              let id = card.cardNumber - 1
              next.gene[id] = lerp100(next.gene[id], y.gene[id], mergeGene)
      else:
        for id, value in y.gene:
          next.gene[id] = lerp100(next.gene[id], value, mergeGene)

    population = nextPopulation
    population.sort(cmp, Descending)

    for index in 0 ..< bestsSize:
      bests[generation][index] = population[index]

    let avg = sumEvals(population) / populationSize.float
    echo &"# {stamp()} {toSummary(generation, avg, bests[generation])}"

proc plotBaselines (bests: Bests, lines: seq[Baseline]): void =
  echo &"set output 'plot-baselines.svg'"
  echo &"set terminal svg font 'monospace:Bold,16' linewidth 2 size 1000,600"
  echo &"set xlabel 'Generation'"
  echo &"set ylabel '% of wins'"

  echo &"# Running average of size n"
  echo &"n = {min(10, generations)}"
  for k in lines.low .. lines.high:
    echo &"do for[i = 1 : n] {{"
    echo &"  eval(sprintf('pre{k}%d = 0', i))"
    echo &"}}"

    echo &"shift{k} = '('"
    echo &"do for[i = n : 2 : -1] {{"
    echo &"  shift{k} = sprintf('%spre{k}%d = pre{k}%d, ', shift{k}, i, i - 1)"
    echo &"}}"
    echo &"shift{k} = shift{k} . 'pre{k}1 = x)'"

    echo &"sum{k} = '(pre{k}1'"
    echo &"do for[i = 2 : n] {{"
    echo &"  sum{k} = sprintf('%s + pre{k}%d', sum{k}, i)"
    echo &"}}"
    echo &"sum{k} = sum{k} . ')'"

    echo &"samples{k}(x) = $0 > (n - 1) ? n : ($0 + 1)"
    echo &"shift{k}(x) = @shift{k}"
    echo &"avg{k}(x) = (shift{k}(x), @sum{k} / samples{k}($0))"

  var scores = newSeq[float](lines.high)

  for k, line in lines:
    echo &"$baseline{k} <<EOD"

    let baseline = newConfig(draft = line.evaluator, player = "Greedy")

    let score = 100.0 / 2 / baselinesGames / line.drafts.len.float
    for generation, group in bests:
      for index, individual in group:
        let player = individual.toConfig

        individual.eval = 0.0

        parallel:
          for draft in line.drafts:
            for game in 1 .. baselinesGames:
              let winX = spawn play(player, baseline, draft)
              let winY = spawn play(baseline, player, draft)
              if     winX: individual.eval += score
              if not winY: individual.eval += score

      let avg = sumEvals(group) / bestsSize
      scores[k] += avg / generations

      echo &"# {stamp()} {toSummary(generation, avg, group)}"
      echo &"  {generation + 1:4} {avg:5.2f}"
    echo &"EOD"

  echo &"plot \\"
  for k, line in lines:
   let label = &"{line.title} {scores[k]:5.2f}"
   let trail = if k == lines.high: "" else: ", \\"
   echo &"  $baseline{k} using 1:(avg{k}($2)) title '{label}' with lines{trail}"

proc plotChampions (bests: Bests, drafts: Drafts): void =
  echo &"set output 'plot-champions.svg'"
  echo &"set terminal svg font 'monospace:Bold,16' linewidth 2 size 1000,600"
  echo &"set xlabel 'Generation'"
  echo &"set ylabel '% of wins'"

  echo &"# Running average of size n"
  echo &"n = {min(10, generations)}"
  for k in 0 .. champions:
    echo &"do for[i = 1 : n] {{"
    echo &"  eval(sprintf('pre{k}%d = 0', i))"
    echo &"}}"

    echo &"shift{k} = '('"
    echo &"do for[i = n : 2 : -1] {{"
    echo &"  shift{k} = sprintf('%spre{k}%d = pre{k}%d, ', shift{k}, i, i - 1)"
    echo &"}}"
    echo &"shift{k} = shift{k} . 'pre{k}1 = x)'"

    echo &"sum{k} = '(pre{k}1'"
    echo &"do for[i = 2 : n] {{"
    echo &"  sum{k} = sprintf('%s + pre{k}%d', sum{k}, i)"
    echo &"}}"
    echo &"sum{k} = sum{k} . ')'"

    echo &"samples{k}(x) = $0 > (n - 1) ? n : ($0 + 1)"
    echo &"shift{k}(x) = @shift{k}"
    echo &"avg{k}(x) = (shift{k}(x), @sum{k} / samples{k}($0))"

  var labels: array[champions + 1, string]
  var scores: array[champions + 1, float]

  for k in 0 .. champions:
    echo &"$data{k} <<EOD"

    var players: seq[Config]
    if k == 0:
      players = newSeqWith[Config](randoms, newIndividual(true).toConfig)
      labels[k] = &"Randoms {randoms:5}"
    else:
      let generation = k * int(generations / champions) - 1
      players.add(bests[generation][0].toConfig)
      labels[k] = &"Champion {generation + 1:4}"

    let score = 100.0 / 2 / bestsGames / players.len.float
    for generation, group in bests:
      let draftsToCheck =
        if mode == "evolve-specialized": @[drafts[generation]]
        else: drafts

      for index, enemy in group:
        let opponent = enemy.toConfig

        enemy.eval = 0.0

        for draft in draftsToCheck:
          parallel:
            for player in players:
              for game in 1 .. bestsGames:
                let winX = spawn play(player, opponent, draft)
                let winY = spawn play(opponent, player, draft)
                if     winX: enemy.eval += score
                if not winY: enemy.eval += score

      let avg = sumEvals(group) / bestsSize / draftsToCheck.len.float
      scores[k] += avg / generations

      echo &"# {stamp()} {toSummary(generation, avg, group)}"
      echo &"  {generation + 1:4} {avg:5.2f}"
    echo &"EOD"

  echo &"plot \\"
  for k in 0 .. champions:
   let label = &"{labels[k]} {scores[k]:5.2f}"
   let trail = if k == champions: "" else: ", \\"
   echo &"  $data{k} using 1:(avg{k}($2)) title '{label}' with lines{trail}"

proc plotEvolution (bests: Bests, drafts1: Drafts, drafts2: Drafts): void =
  var players: array[generations * bestsSize, Individual]
  for index in players.low .. players.high:
    players[index] = bests[(index / bestsSize).int][index mod bestsSize]

  var enemies: array[progressEnemies, Config]
  for index in enemies.low .. enemies.high:
    enemies[index] = newIndividual(true).toConfig

  echo &"set output 'plot-evolution.svg'"
  echo &"set terminal svg font 'monospace:Bold,16' linewidth 2 size 1000,600"
  echo &"set xlabel 'Known drafts %'"
  echo &"set ylabel 'Fresh drafts %'"
  echo &"$progress <<EOD"
  for index, player in players:
    let config = player.toConfig
    var coords = [0.0, 0.0]

    for coord, drafts in [drafts1, drafts2]:
      player.eval = 0.0

      let score = 100.0 / 2 / progressGames / (enemies.len * drafts.len).float
      for draft in drafts:
        parallel:
          for enemy in enemies:
            for game in 1 .. progressGames:
              let winX = spawn play(config, enemy, draft)
              let winY = spawn play(enemy, config, draft)
              if     winX: player.eval += score
              if not winY: player.eval += score
      coords[coord] = player.eval

    echo &"# {stamp()} Player {index + 1:4}"
    echo &"  {coords[0]:5.2f} {coords[1]:5.2f}"
  echo &"EOD"
  echo &"a = 1"
  echo &"b = 50"
  echo &"fit(x) = a * x + b"
  echo &"fit fit(x) $progress via a, b"
  echo &"plot \\"
  echo &"  $progress notitle pointsize 0.5 pointtype 7, \\"
  echo &"  fit(x) title sprintf('y = %fx + %f', a, b)"

proc plotPerformance (bests: Bests, drafts: Drafts): void =
  echo &"set output 'plot-performance.svg'"
  echo &"set terminal svg font 'monospace:Bold,16' linewidth 2 size 1000,600"
  echo &"set xlabel 'Plays'"
  echo &"set ylabel '% of wins'"

  let games = plays
  let score = 100.0 / 2 / bestsGames / bests[0].len.float / drafts.len.float
  var enemies = [
    newConfig(player = "Greedy", draft = "ClosetAI"),
    newConfig(player = "Greedy", draft = "Icebox"),
    newIndividual(true).toConfig,
    newIndividual(true).toConfig,
    newIndividual(true).toConfig
  ]

  echo &"$data <<EOD"
  for generation, players in bests:
    var results = newSeq[float](enemies.len)
    for index, enemy in enemies:
      var result = 0.0
      for player in players.mapIt(it.toConfig):
        parallel:
          for draft in drafts:
            for game in 1 .. bestsGames:
              let winX = spawn play(player, enemy, draft)
              let winY = spawn play(enemy, player, draft)
              if     winX: result += score
              if not winY: result += score
      results[index] = result

    let cost = (games.float / bests.len.float * (1.0 + generation.float)).int
    let avg = results.sum / results.len.float
    let dev = results.mapIt((it - avg).pow(2.0)).sum / (results.len.float - 1.0)

    echo &"# {stamp()}"
    echo &"  {cost} {avg} {sqrt(dev)}"
  echo &"EOD"

  echo &"plot $data using 1:2:3 title '{mode}' with errorbars"

proc randomExhaustive (bests: var Bests, drafts: Drafts): void =
  var population = newPopulation(true)
  let scoreWin = 100 / (4 * draftsEval * scoreGames * (populationSize - 1))

  for generation in 0 ..< generations:
    for individual in population:
      individual.eval = 0

    for draft in drafts:
      parallel:
        for indexA, a in population:
          for indexB, b in population:
            if indexA == indexB:
              continue

            for _ in 1 .. scoreGames:
              let winX = spawn play(a, b, draft)
              let winY = spawn play(b, a, draft)
              if winX: a.eval += scoreWin else: b.eval += scoreWin
              if winY: b.eval += scoreWin else: a.eval += scoreWin

    population.sort(cmp, Descending)

    for index in 0 ..< bestsSize:
      bests[generation][index] = population[index]

    let avg = sumEvals(population) / populationSize.float
    echo &"# {stamp()} {toSummary(generation, avg, bests[generation])}"

proc randomTournament (bests: var Bests, drafts: Drafts): void =
  var population = newPopulation(true)
  let scoreWin = 100 / (2 * draftsEval * scoreGames)

  for generation in 0 ..< generations:
    population.shuffle()
    for individual in population:
      individual.eval = 0

    var tournament1: seq[Individual]
    var tournament2: seq[Individual]
    for individual in population:
      tournament1.add(individual)

    while tournament1.len > 1:
      for index in countup(0, tournament1.len - 2, 2):
        let a = tournament1[index + 0]
        let b = tournament1[index + 1]
        parallel:
          for draft in drafts:
            for _ in 1 .. scoreGames:
              let winX = spawn play(a, b, draft)
              let winY = spawn play(b, a, draft)
              if winX: a.eval += scoreWin else: b.eval += scoreWin
              if winY: b.eval += scoreWin else: a.eval += scoreWin

        let best = if a.eval > b.eval: a else: b
        tournament2.add(best)

      tournament1 = tournament2
      tournament2 = @[]

    population.sort(cmp, Descending)

    for index in 0 ..< bestsSize:
      bests[generation][index] = population[index]

    let avg = sumEvals(population) / populationSize.float
    echo &"# {stamp()} {toSummary(generation, avg, bests[generation])}"

proc main (): void =
  randomize()

  let cards = getCards()
  var bests: Bests

  when mode == "default":
    var draftss: array[activeDrafts, Drafts]
    for index in draftss.low .. draftss.high:
      draftss[index] = newSeqWith(generations, newDraft(cards))
    let drafts: Drafts = newSeqWith(progressDrafts, newDraft(cards))

    evolveToBests(bests, draftss)
    plotPerformance(bests, drafts)

  when mode == "evolve-variant-2":
    let drafts1: Drafts = newSeqWith(generations div 2, newDraft(cards))
    let drafts2: Drafts = newSeqWith(progressDrafts, newDraft(cards))

    evolveToBests(bests, [concat(drafts1, drafts1)])
    plotPerformance(bests, drafts2)

  when mode == "evolve-variant-4":
    let drafts1: Drafts = newSeqWith(generations div 4, newDraft(cards))
    let drafts2: Drafts = newSeqWith(progressDrafts, newDraft(cards))

    evolveToBests(bests, [concat(drafts1, drafts1, drafts1, drafts1)])
    plotPerformance(bests, drafts2)

  when mode == "evolve-specialized":
    let drafts1: Drafts = newSeqWith(generations, newDraft(cards))
    let drafts2: Drafts = newSeqWith(progressDrafts, newDraft(cards))

    evolveToBests(bests, [drafts1])
    plotPerformance(bests, drafts2)

  when mode == "evolve-standard":
    let drafts1: Drafts = newSeqWith(draftsEval, newDraft(cards))
    let drafts2: Drafts = newSeqWith(progressDrafts, newDraft(cards))

    evolveNormals(bests, drafts1)
    plotPerformance(bests, drafts2)

  when mode == "random-exhaustive":
    randomExhaustive(bests, newSeqWith(draftsEval, newDraft(cards)))

  when mode == "random-tournament":
    randomTournament(bests, newSeqWith(draftsEval, newDraft(cards)))

  echo &"# {stamp()} Plays total {plays}"
  for index, best in bests[^1]:
    echo &"# {stamp()} Best {index + 1:2}: {best.gene}"

when isMainModule:
  main()
