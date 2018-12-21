import std / tables
import ClosetAI, Icebox, Manual, Random3

const draftEvaluations * = toTable({
  "default":  evaluateDraftManual,
  "ClosetAI": evaluateDraftClosetAI,
  "Icebox":   evaluateDraftIcebox,
  "Manual":   evaluateDraftManual,
  "Random3":  evaluateDraftRandom3,
})
