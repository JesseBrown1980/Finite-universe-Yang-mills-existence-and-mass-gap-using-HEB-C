The V0 room-walk program as it ran on the seat's machine (Rust 1.81, clippy -D warnings exit 0, unsafe forbidden, integers only).
It is stored as text (main.rs.txt, Cargo.toml.txt, Cargo.lock.txt) because it reuses the canonical ternary kernel through an absolute #[path] to
C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs, which exists only on that machine, so it cannot be built by this repository's hosted jobs.
To build it: restore the three file names, and point the #[path] line at a copy of that tribit/mod.rs.
