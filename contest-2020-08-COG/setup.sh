# Basics
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y build-essential cmake curl gnuplot-nox openjdk-11-jdk python3 python3-pip

# Python libs
pip3 install numpy scipy sortedcontainers

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env
rustup install nightly-2020-05-14
