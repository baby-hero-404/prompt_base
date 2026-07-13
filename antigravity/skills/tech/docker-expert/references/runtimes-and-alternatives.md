# Modern Container Runtimes & Alternatives

Traditional Docker containers (using `runc`) are no longer the only option for deploying packaged applications in 2026.

## Selection Guideline

| Use Case | Recommended Technology | Why? |
|----------|------------------------|------|
| **Standard web services / General Purpose** | Traditional Docker (`runc` / `containerd`) | Widest ecosystem, standard orchestration (K8s/Compose). |
| **Edge Computing / Extremely fast startup** | WASM (WebAssembly) Containers | Millisecond cold starts, extremely small footprint, runs anywhere. |
| **High Security / Strong Isolation** | microVMs (Firecracker, Kata Containers) | Hardware-level virtualization isolation with container-like speed. Perfect for multi-tenant serverless. |

## WASM (WebAssembly) Containers

- **What they are:** Compiled binaries running in a WASM runtime (like Wasmtime or WasmEdge) instead of a Linux namespace.
- **Integration:** Docker now supports WASM natively via `containerd` shims.
- **Dockerfile example:** You often don't need a Dockerfile. You compile directly to `.wasm` and package it.

## microVMs (Firecracker)

- **What they are:** Lightweight virtual machines designed for serverless computing. They boot in milliseconds.
- **Why use them:** Containers share the host kernel. If the kernel is compromised, all containers are at risk. microVMs provide a hardware boundary.
- **Usage:** Typically managed via platforms like Fly.io, AWS Fargate, or specialized orchestrators (Nomad) rather than vanilla Docker Compose.
