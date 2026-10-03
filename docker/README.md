# Docker images for the GPU parse

| Image | Dockerfile | What's inside |
|---|---|---|
| `cap-slice-docling` | `docling.Dockerfile` | Docling 2.130.0, PyTorch 2.14.0 (CUDA 13.0 build), cap-slice with all its deps |
| `cap-slice-mineru` | `mineru.Dockerfile` | MinerU 4.0.10 with vLLM 0.28.0 (PyTorch 2.13.0, CUDA 13.0 build) serving MinerU2.5-Pro-2605-1.2B, plus cap-slice's runner (no other deps) |

Two images because vLLM pins its own PyTorch, which can clash with Docling's.

Both start from plain `ubuntu:24.04`: CUDA builds of PyTorch/vLLM ship their CUDA libraries as pip packages, so the host only needs the **NVIDIA driver (R580+ for CUDA 13)** and **nvidia-container-toolkit**. For an older driver, build with `--build-arg TORCH_BACKEND=cu126` (not on RTX 50xx — Blackwell needs CUDA ≥ 12.8, i.e. a newer driver).

## Pinned dependencies
`requirements-*.txt` are fully pinned and resolved for Linux x86_64 (glibc 2.39 = Ubuntu 24.04), Python 3.12, CUDA 13.0, from the `*.in` files. Resolved on the laptop on 2026-10-03, so the cloud build doesn't hit version conflicts. To regenerate:

```bash
cd docker
uv pip compile docling.in -o requirements-docling.txt --python-version 3.12 \
    --python-platform x86_64-manylinux_2_39 --torch-backend cu130 --no-header
uv pip compile mineru.in  -o requirements-mineru.txt  --python-version 3.12 \
    --python-platform x86_64-manylinux_2_39 --torch-backend cu130 --no-header
```

## Not tested
The images were **not built** on the laptop (no Docker there, and not enough disk). What *was* tested on the laptop, on CPU: the batch runner, both adapters (Docling end to end; MinerU end to end against MinerU's llama.cpp CPU server with the same MinerU2.5-Pro model, including the VLM path on a scanned page), the v2 scorer and the benchmark builder. The first step on the GPU host (`tools/gpu/session.sh smoke`) is what verifies the images.

Mounts at run time: the repo at `/app` (so the code that runs is the checked-out code) and a host model folder at `/models` (weights + Hugging Face cache, survives image rebuilds). See `docs/gpu-run.md`.
