# Baseline1
# Baseline2
# Chad
(cd Chad/agent && cargo +nightly-2020-05-14 build --release)
# Coac
(cd Coac && cmake . && make)
# OneLaneIsEnough
(cd OneLaneIsEnough && g++ -std=c++17 -O3 main.cpp -o main)
# ReinforcedGreediness
