# Basics
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y build-essential cmake curl gnuplot-nox openjdk-11-jdk libmozjs-68-0 libmozjs-68-dev mono-complete python3 python3-pip unzip

# Gradle
curl https://downloads.gradle-dn.com/distributions/gradle-7.1.1-bin.zip -o $HOME/gradle-7.1.1-bin.zip
mkdir /usr/local/gradle
unzip -od /usr/local/gradle $HOME/gradle-7.1.1-bin.zip
export PATH=$PATH:/usr/local/gradle/gradle-7.1.1/bin

# Python libs
pip3 install numpy scipy sortedcontainers

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env
rustup install nightly-2020-05-14
