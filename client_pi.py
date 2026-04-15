import io
import time
import uuid

import grpc
import torch
import torch.nn as nn
import torchvision.models as models
from PIL import Image
from torchvision import transforms

import inference_pb2 as pb2
import inference_pb2_grpc as pb2_grpc

SERVER_ADDR = "192.168.1.10:50051"
IMAGE_PATH = "sample.jpg"
CUTOFF = 6
DEVICE = "cpu"


class EarlyMobileNetV2(nn.Module):
    def __init__(self, cutoff=6):
        super().__init__()
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        self.features_head = nn.Sequential(*list(model.features.children())[:cutoff])

    def forward(self, x):
        return self.features_head(x)


def preprocess(image_path):
    tfm = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    img = Image.open(image_path).convert("RGB")
    return tfm(img).unsqueeze(0)


def main():
    early_model = EarlyMobileNetV2(CUTOFF).eval().to(DEVICE)
    x = preprocess(IMAGE_PATH).to(DEVICE)
    request_id = str(uuid.uuid4())

    t0 = time.perf_counter()
    with torch.no_grad():
        t1 = time.perf_counter()
        activations = early_model(x)
        edge_ms = (time.perf_counter() - t1) * 1000

    buf = io.BytesIO()
    torch.save(activations.cpu(), buf)
    payload = buf.getvalue()

    channel = grpc.insecure_channel(SERVER_ADDR)
    stub = pb2_grpc.SplitInferenceStub(channel)

    t2 = time.perf_counter()
    response = stub.Infer(pb2.TensorRequest(
        data=payload,
        shape=list(activations.shape),
        dtype=str(activations.dtype),
        request_id=request_id,
    ))
    remote_ms = (time.perf_counter() - t2) * 1000
    total_ms = (time.perf_counter() - t0) * 1000

    logits = torch.load(io.BytesIO(response.data), map_location="cpu")
    pred_idx = int(torch.argmax(logits, dim=1).item())

    print({
        "request_id": request_id,
        "edge_ms": round(edge_ms, 2),
        "remote_ms_including_network": round(remote_ms, 2),
        "total_ms": round(total_ms, 2),
        "predicted_class": pred_idx,
        "activation_bytes": len(payload),
        "activation_shape": list(activations.shape),
    })


if __name__ == "__main__":
    main()
