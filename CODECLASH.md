# [CodeClash] RobotRumble
This is the starter codebase for the RobotRumble arena featured in CodeClash.

The code represented in this codebase comes from the following sources:
- The `cli` folder is from the https://github.com/robot-rumble/cli repository, which wraps the Robot Rumble engine in a command line interface. The `cli` tool is also how the ./rumblebot executable is built.
- The `logic/` folder is from https://github.com/robot-rumble/logic, which captures how Robot Rumble is implemented.
- The `builtin-bots/` folder is from https://github.com/robot-rumble/builtin-bots, which contains the source code for several example robots provided to beginner players.
- The `docs/` folder contains documentation for the Robot Rumble engine, which is also hosted at https://github.com/robot-rumble/docs.

<hr />

### To rebuild `./robotrumble` executable from scratch
From within a dockerfile...
```dockerfile
# Ensure awscli is installed w/ apt-get
RUN apt-get update && apt-get install -y awscli curl

# Install Rust via rustup
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
 && . "$HOME/.cargo/env" \
 && echo 'source $HOME/.cargo/env' >> /etc/bash.bashrc
ENV PATH="/root/.cargo/bin:${PATH}"

# Use a newer toolchain required by deps, and default to it
RUN rustup toolchain install 1.82.0 && rustup default 1.82.0

# Force Cargo to use system linker (gcc) instead of rust-lld
RUN mkdir -p /root/.cargo \
 && printf '[target.x86_64-unknown-linux-gnu]\nlinker = "cc"\n' > /root/.cargo/config.toml

# Clone the repo... (OMITTED)

# Pull public S3 assets
RUN cd /workspace/cli && aws --no-sign-request s3 sync s3://rr-public-assets/lang-runners ../logic/wasm-dist/lang-runners
RUN cd /workspace/cli && aws --no-sign-request s3 sync s3://rr-public-assets/cli-assets dist/

# Build without updating deps; use Cargo.lock as-is
RUN cd /workspace/cli && cargo build --locked --release

# Place the built binary at /workspace/rumblebot
RUN install -Dm755 /workspace/cli/target/release/rumblebot /workspace/rumblebot

# Remove some unnecessary bloat
RUN rm -rf /workspace/cli/target

# Remove rust toolchains & caches
RUN rm -rf /root/.cargo /root/.rustup /root/.cache \
 && sed -i '/source \$HOME\/\.cargo\/env/d' /etc/bash.bashrc || true \
 && true
```
