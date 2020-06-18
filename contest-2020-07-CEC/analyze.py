from contextlib import ExitStack
from functools import lru_cache
from glob import glob
from itertools import chain, zip_longest
from re import compile

normals = compile(r"^.*[ /](.*)\/.*$")
summary = compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d '(?P<player1>.*?)' '(?P<player2>.*?)' (?P<json>{.*}) (?P<score1>-?\d) (?P<score2>-?\d)(?: draftChoicesSeed=\d+| shufflePlayer0Seed=(?P<seed0>\d+)| seed=(?P<seed1>\d+)| shufflePlayer1Seed=(?P<seed2>\d+))*\s*$")
timings = compile(r'"\$(\d) (\d+)ns at turn (\d+)\\n"')
scoring = {'-1': 'errs', '0': 'lost', '1': 'wins'}

def analyze(chunks, stats, times):
  for chunk in filter(None, chunks):
    for line in filter(None, chunk):
      match = summary.match(line)
      if match is not None:
        analyze_line(match.groupdict(), stats, times)
    yield

def analyze_line(match, stats, times):
  if match['seed0'] != match['seed1'] or match['seed0'] != match['seed2']:
    return

  player1 = normalize(match['player1'])
  player2 = normalize(match['player2'])

  pairA = (player1, player2)
  pairB = (player2, player1)

  if pairA not in stats: stats[pairA] = stats_new()
  if pairB not in stats: stats[pairB] = stats_new()

  score1 = match['score1']
  score2 = match['score2']
  if score1 != '-1' and score2 != '-1':
    for match in timings.finditer(match['json']):
      player, time, turn = match.groups()
      time = int(time) / 1_000_000

      # Time limit is 200, but CG servers are quite fast.
      # 10% budget should be enough.
      if time > (1000 if turn in '01' else 200) * 1.1:
        if player == '0': score1 = '-1'
        if player == '1': score2 = '-1'
        break

      if turn not in '01':
        if player1 not in times: times[player1] = times_new()
        if player2 not in times: times[player2] = times_new()
        if player == '0': times_add(times[player1], time)
        if player == '1': times_add(times[player2], time)

  if score1 == '-1' and score2 == '0': score2 = '1'
  if score2 == '-1' and score1 == '0': score1 = '1'

  stats[pairA][scoring[score1]] += 1
  stats[pairB][scoring[score2]] += 1

def graph(paths, chunk, limit=None):
  header = True
  stats = {}
  times = {}

  interleave = lambda xs: chain.from_iterable(zip_longest(*xs))
  chunkify = lambda xs, n: zip_longest(*([iter(xs)] * n))

  with ExitStack() as stack:
    files = [stack.enter_context(open(path, buffering=1)) for path in paths]
    chunks = interleave(chunkify(file, chunk) for file in files)
    for _ in analyze(chunks, stats, times):
      players = {}
      for (player1, player2), results in stats.items():
        if player1 != player2:
          players[player1] = stats_combine(players.get(player1), results)
      if header:
        header = False
        print(';'.join(sorted(players.keys())))
      graph_print(players)
      if limit is not None:
        limit -= 1
        if limit <= 0:
          break

  return stats, times

def graph_print(players):
  def single(pair):
    _, stats = pair
    alls = stats['errs'] + stats['lost'] + stats['wins']
    wins = stats['wins'] / alls * 100
    return f'{wins:6.2f}'
  print(';'.join(map(single, sorted(players.items()))))

@lru_cache(16)
def normalize(player):
  player = normals.match(player).group(1)
  if player == 'CoacProphet':
    return 'ProphetCoac'
  if player == 'release':
    return 'Chad'
  return player

def score(stats, times):
  players = {}

  for (player1, player2), results in sorted(stats.items()):
    if player1 != player2:
      players[player1] = stats_combine(players.get(player1), results)
      score_print(f'{player1:>20} {player2:>20}', results)

  order = lambda pair: score_count(pair[1])[2]
  for player1, results in sorted(players.items(), key=order, reverse=True):
    avg = times_avg(times[player1])
    dev = times_dev(times[player1])
    score_print(f'{player1:>20}', results, f' avg={avg:6.2f}±{dev:6.2f}ms')

def score_count(stats):
  alls = stats['errs'] + stats['lost'] + stats['wins']
  errs = stats['errs'] / alls * 100
  wins = stats['wins'] / alls * 100
  return alls, errs, wins

def score_print(title, stats, extra = ''):
  alls, errs, wins = score_count(stats)
  print(f'{title} wins={wins:6.2f}% errs={errs:6.2f}% alls={alls // 2}{extra}')

def stats_combine(statsA, statsB):
  if statsA is None:
    statsA = {'errs': 0, 'lost': 0, 'wins': 0}

  if statsB is not None:
    statsA['errs'] += statsB['errs']
    statsA['lost'] += statsB['lost']
    statsA['wins'] += statsB['wins']

  return statsA

def stats_new():
  return stats_combine(None, None)

def times_add(times, value):
  times[0] += 1
  delta1 = value - times[1]
  times[1] += delta1 / times[0]
  delta2 = value - times[1]
  times[2] += delta1 * delta2

def times_avg(times):
  return times[1]

def times_dev(times):
  return (times[2] / times[0]) ** 0.5

def times_new():
  return [0, 0.0, 0.0]

if __name__ == '__main__':
  files = sorted(glob('out-*.txt'))
  score(*graph(files, 13 * 13, 2500))
