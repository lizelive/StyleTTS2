set -e
IMAGE=$(podman build -q .)
podman run --rm -it --device nvidia.com/gpu=all -p 7860:7860 -v /home/lizelive/.cache/huggingface:/home/user/.cache/huggingface --gpus all "$IMAGE" python app.py
