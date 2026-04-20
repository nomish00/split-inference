import io
import time
from concurrent import futures

import grpc
import torch
from PIL import Image
from torchvision.models import MobileNet_V2_Weights, mobilenet_v2

import inference_pb2 as pb2
import inference_pb2_grpc as pb2_grpc

PORT = 50051
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

weights = MobileNet_V2_Weights.DEFAULT
preprocess = weights.transforms()
model = mobilenet_v2(weights=weights).eval().to(DEVICE)


class FullInferenceService(pb2_grpc.SplitInferenceServicer):
    def Infer(self, request, context):
        t0 = time.perf_counter()

        image = Image.open(io.BytesIO(request.data)).convert("RGB")
        x = preprocess(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            logits = model(x)
            probs = logits.softmax(dim=1)[0]
            class_id = int(probs.argmax().item())
            score = float(probs[class_id].item())
            label = weights.meta["categories"][class_id]

        elapsed_ms = (time.perf_counter() - t0) * 1000
        print(
            {
                "request_id": request.request_id,
                "device": DEVICE,
                "server_ms": round(elapsed_ms, 2),
                "class_id": class_id,
                "label": label,
                "score": round(score, 4),
                "image_bytes": len(request.data),
            }
        )

        return pb2.TensorReply(
            data=b"",
            shape=[],
            dtype="label",
            request_id=request.request_id,
            predicted_class=f"{class_id}:{label}:{score:.4f}",
        )

    def Health(self, request, context):
        return pb2.HealthReply(status=f"ok:{DEVICE}")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb2_grpc.add_SplitInferenceServicer_to_server(FullInferenceService(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"Full inference gRPC server listening on :{PORT}, device={DEVICE}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
