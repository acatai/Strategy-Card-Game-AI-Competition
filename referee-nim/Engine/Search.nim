import std / [strformat, strutils, times]
import Action, State

type
  SearchResult * = ref object
    actions *: seq[Action]
    score   *: float

func `$` * (searchResult: SearchResult): string =
  let actions = searchResult.actions
  result = if actions.len == 0: "PASS" else: actions.join(";")
  result = &"{result} # score: {searchResult.score}"
