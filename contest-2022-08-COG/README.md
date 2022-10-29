Bots used in this competition won't work after commit [7aaec88](https://github.com/acatai/Strategy-Card-Game-AI-Competition/commit/7aaec88d2c19e24f0f10f24bb6d6cf141e69f46e).

![results](graph.svg)

```sh
source setup.sh
source prepare.sh
source run.sh > out-1.txt &
source run.sh > out-2.txt &
source run.sh > out-3.txt &
source run.sh > out-4.txt &
wait
source graph.sh
```
