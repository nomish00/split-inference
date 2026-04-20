import io
import time
from concurrent import futures

import grpc
import torch
import torch.nn as nn
import torchvision.models as models

import inference_pb2 as pb2
import inference_pb2_grpc as pb2_grpc

PORT = 50051
#DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE = "cpu"
CUTOFF = 6


class LateMobileNetV2(nn.Module):
    def __init__(self, cutoff=6):
        super().__init__()
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        self.features_tail = nn.Sequential(*list(model.features.children())[cutoff:])
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = model.classifier

    def forward(self, x):
        x = self.features_tail(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x


LATE_MODEL = LateMobileNetV2(CUTOFF).eval().to(DEVICE)


class SplitInferenceService(pb2_grpc.SplitInferenceServicer):
    def Infer(self, request, context):
        t0 = time.perf_counter()
        tensor = torch.load(io.BytesIO(request.data), map_location=DEVICE, weights_only=True)
        with torch.no_grad():
            logits = LATE_MODEL(tensor)
            pred_idx = int(torch.argmax(logits, dim=1).item())

        buf = io.BytesIO()
        torch.save(logits.cpu(), buf)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        print(f"request_id={request.request_id} device={DEVICE} server_ms={elapsed_ms:.2f} pred={pred_idx}")

        return pb2.TensorReply(
            data=buf.getvalue(),
            shape=list(logits.shape),
            dtype=str(logits.dtype),
            request_id=request.request_id,
            predicted_class=str(pred_idx),
        )

    def Health(self, request, context):
        return pb2.HealthReply(status=f"ok:{DEVICE}")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb2_grpc.add_SplitInferenceServicer_to_server(SplitInferenceService(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"gRPC server listening on :{PORT}, device={DEVICE}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        server.stop(grace=5)  # 5 seconds for ongoing requests to finish
        print("Server stopped.")


if __name__ == "__main__":
    serve()
