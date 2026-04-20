import os
import time
import uuid
import grpc
import inference_pb2 as pb2
import inference_pb2_grpc as pb2_grpc

SERVER_ADDR = os.getenv("SERVER_ADDR", "10.74.1.50:50051")
IMAGE_PATH = os.getenv("IMAGE_PATH", "sample.jpg")
TIMEOUT_SEC = float(os.getenv("TIMEOUT_SEC", "30"))


def main():
    if not os.path.exists(IMAGE_PATH):
        raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

    request_id = str(uuid.uuid4())

    t0 = time.perf_counter()
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
    read_ms = (time.perf_counter() - t0) * 1000

    channel = grpc.insecure_channel(SERVER_ADDR)
    stub = pb2_grpc.SplitInferenceStub(channel)

    t1 = time.perf_counter()
    response = stub.Infer(
        pb2.TensorRequest(
            data=image_bytes,
            shape=[],
            dtype="image/jpeg",
            request_id=request_id,
        ),
        timeout=TIMEOUT_SEC,
    )
    remote_ms = (time.perf_counter() - t1) * 1000
    total_ms = (time.perf_counter() - t0) * 1000

    print({
        "mode": "client_send_to_remote",
        "request_id": request_id,
        "read_ms": round(read_ms, 2),
        "remote_ms_including_network": round(remote_ms, 2),
        "total_ms": round(total_ms, 2),
        "image_path": IMAGE_PATH,
        "image_bytes": len(image_bytes),
        "predicted_class": response.predicted_class,
    })


if __name__ == "__main__":
    main()
