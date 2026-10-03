# Docling on GPU for cap-slice.
#
#   docker build -f docker/docling.Dockerfile -t cap-slice-docling .
#   docker run --rm --gpus all -v $PWD:/app -v /models:/models cap-slice-docling \
#       cap-slice-parse --parser docling --out parsed
#
# Plain Ubuntu base: the CUDA build of PyTorch ships its own CUDA libraries as
# pip packages, so the host only needs the NVIDIA driver (+ nvidia-container-toolkit).
# TORCH_BACKEND=cu130 needs driver R580+; on an older driver build with
# --build-arg TORCH_BACKEND=cu128 (pins in docker/requirements-*-cu128.txt).
FROM ubuntu:24.04

ARG TORCH_BACKEND=cu130
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    HF_HOME=/models/hf \
    CAP_SLICE_DEVICE=cuda

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.12 python3.12-venv ca-certificates git curl rsync \
        libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /usr/local/bin/uv

# Pinned dependency set (resolved for Linux x86_64 + CUDA; see docker/README.md).
RUN uv venv /opt/venv -p python3.12
COPY docker/requirements-docling-${TORCH_BACKEND}.txt /tmp/requirements.txt
RUN uv pip install --no-cache --torch-backend ${TORCH_BACKEND} -r /tmp/requirements.txt
# OCR on GPU: replace the CPU onnxruntime with onnxruntime-gpu for this CUDA major
# version (1.22.0 = CUDA 12 build; current releases are CUDA 13). See setup_runpod.sh.
RUN uv pip uninstall onnxruntime && \
    if [ "${TORCH_BACKEND#cu12}" != "${TORCH_BACKEND}" ]; then uv pip install --no-cache onnxruntime-gpu==1.22.0; \
    else uv pip install --no-cache onnxruntime-gpu; fi

# The project itself (deps already installed above; editable so a mounted repo
# at /app is what actually runs).
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv pip install --no-cache --no-deps -e .

CMD ["cap-slice-parse", "--help"]
