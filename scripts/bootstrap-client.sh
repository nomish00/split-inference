#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y python3-pip python3-venv protobuf-compiler build-essential libopenblas-dev libjpeg-dev zlib1g-dev

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements/client.txt

echo "Client environment ready"
