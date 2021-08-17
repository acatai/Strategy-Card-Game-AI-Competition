import std / [streams, strutils]

type
  Input* = ref InputObj
  InputObj = object of StreamObj
    line*: string
    stream*: Stream

func newInput*(stream: Stream): Input {.inline.} =
  Input(stream: stream)

proc getLine*(input: Input): string {.inline.} =
  input.stream.readLine

proc getStr*(input: Input): string =
  while true:
    if input.line == "":
      input.line = input.stream.readLine

    for part in input.line.splitWhitespace:
      input.line.delete(0, part.len)
      return part

proc getInt*(input: Input): int {.inline.} =
  input.getStr.parseInt
