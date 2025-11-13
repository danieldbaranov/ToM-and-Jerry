#!/bin/bash
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=32g
#SBATCH -J "ToM and Jerry"
#SBATCH -p short
#SBATCH -t 0:30:00
#SBATCH --gres=gpu:1
#SBATCH -C "A100|V100"
#SBATCH -o logs/slurm-%j.out
#SBATCH -e logs/slurm-%j.err                

echo "[SLURM] Node: $HOSTNAME"

module load python/3.9.22

source .venv/bin/activate

MODEL="meta-llama/Llama-3.1-8B-Instruct"
PORT=8000

echo "[SLURM] Starting vLLM..."
vllm serve $MODEL \
    --host 0.0.0.0 \
    --port $PORT \
    --api-key test &

VLLM_PID=$!

echo "[SLURM] Waiting for vLLM to initialize..."

RETRIES=40
until curl -s "http://localhost:${PORT}/v1/models" >/dev/null 2>&1; do
    ((RETRIES--))
    if [ $RETRIES -le 0 ]; then
        echo "[SLURM] ERROR: vLLM failed to start."
        kill $VLLM_PID
        exit 1
    fi
    sleep 3
done

echo "[SLURM] vLLM is ready."

echo "[SLURM] Running python script..."
cd code/src
python test.py --model meta-llama/Llama-3.1-8B-Instruct

echo "[SLURM] Stopping vLLM server..."
kill $VLLM_PID

echo "[SLURM] Job complete."
