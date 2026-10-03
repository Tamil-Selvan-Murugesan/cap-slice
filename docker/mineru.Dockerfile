# MinerU 4 (MinerU2.5-Pro VLM served by vLLM) on GPU for cap-slice.
#
#   docker build -f docker/mineru.Dockerfile -t cap-slice-mineru .
#   docker run --rm --gpus all --shm-size 8g -v $PWD:/app -v /models:/models cap-slice-mineru \
#       tools/gpu/mineru_run.sh --parser-args "--out parsed --workers 8"
#
# Separate image from Docling on purpose: vLLM pins its own PyTorch, which can
# clash with Docling's. The VLM runs as a server inside this container
# (mineru-kit vlm-server --engine vllm, port 30000) and cap-slice's runner sends
# it concurrent requests through MinerU's own parser.
FROM ubuntu:24.04

ARG TORCH_BACKEND=cu130
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    HF_HOME=/models/hf \
    MINERU_HOME=/models/mineru \
    CAP_SLICE_MINERU_SERVER=http://127.0.0.1:30000

# build-essential + python3.12-dev: Triton (used by vLLM) compiles small C
# helpers at runtime and fails without a compiler and Python headers.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.12 python3.12-venv python3.12-dev build-essential \
        ca-certificates git curl rsync libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /usr/local/bin/uv

RUN uv venv /opt/venv -p python3.12
COPY docker/requirements-mineru-${TORCH_BACKEND}.txt /tmp/requirements.txt
RUN uv pip install --no-cache --torch-backend ${TORCH_BACKEND} -r /tmp/requirements.txt

# cap-slice without its own dependencies: the runner only needs pymupdf (pinned
# above) and the standard library; installing its full deps would pull Docling
# and a second PyTorch into this environment.
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv pip install --no-cache --no-deps -e .

CMD ["cap-slice-parse", "--help"]
