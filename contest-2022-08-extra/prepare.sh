# AdvancedAvocadoAgent
(cd AdvancedAvocadoAgent/advanced-avocado-agent && gradle build)
# Ag2O

# Baseline1

# Baseline2

# ByteRL

# Chad
(cd Chad/agent && CARGO_NET_GIT_FETCH_WITH_CLI=true cargo +nightly-2020-05-14 build --release)
# Coac
(cd Coac && cmake . && make)
# DrainPower
(cd DrainPower && mcs -out:DrainPower.exe results.cs)
# DrainPowerAggressive
(cd DrainPower && mcs -out:DrainPowerAggressive.exe results.cs)
# LANE_1_0
(cd LANE_1_0 && javac -encoding UTF-8 LANE_1_0.java)
# OneLaneIsEnough
(cd OneLaneIsEnough && g++ -std=c++17 -O3 main.cpp -o main)
# ReinforcedGreediness
