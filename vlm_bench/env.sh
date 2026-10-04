# Source in every new shell on the pod:  source /workspace/ocr_bench/env.sh
export WS=/workspace
export HF_HOME=$WS/hf_cache
export PADDLE_PDX_CACHE_HOME=$WS/paddlex_cache
export UV_CACHE_DIR=$WS/uv_cache
export P=$WS/data/pages                 # rendered pages + manifests
export RESULTS=$WS/results
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
cd $WS/ocr_bench
