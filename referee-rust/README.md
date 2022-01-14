This directory contains a LoCM engine and runner in Rust but also the code used for one of the papers.
We are interested in extracting a standalone engine library as well as a IO-based referee that would replace the current `.jar` one.
At the moment Clippy is configured but not necessarily "happy".

```sh
# LoCM IO agent
cargo run --release --bin agent

# Benhmark
cargo run --release --bin bench

# Evolution process
[RAYON_NUM_THREADS=N] cargo run --release --bin evolve
```
