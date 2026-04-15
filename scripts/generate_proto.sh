#!/usr/bin/env bash
set -e

source .venv/bin/activate
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. inference.proto

echo "Generated inference_pb2.py and inference_pb2_grpc.py"
