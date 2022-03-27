import std / tables
import ClosetAI, Icebox, Manual, Random3

const draftEvaluations* = toTable({
  # FIXME: Order is important for typing.
  "Random3": evaluateDraftRandom3,
  "default": evaluateDraftManual,
  "ClosetAI": evaluateDraftClosetAI,
  "Icebox": evaluateDraftIcebox,
  "Manual": evaluateDraftManual,
})
