# Basics
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y build-essential cmake curl gnuplot-nox llvm openjdk-11-jdk python3 python3-pip unzip

# Gradle
curl https://downloads.gradle-dn.com/distributions/gradle-7.1.1-bin.zip -o $HOME/gradle-7.1.1-bin.zip
mkdir /usr/local/gradle
unzip -od /usr/local/gradle $HOME/gradle-7.1.1-bin.zip
export PATH=$PATH:/usr/local/gradle/gradle-7.1.1/bin

# Python libs
pip3 install cython==0.29.23 gym==0.19.0 llvmlite==0.37.0 numba==0.54.0 numpy==1.21.0 onnx==1.9.0 onnxruntime==1.8.0 six==1.13.0 tensorflow==2.9.0 torch==1.12.0
