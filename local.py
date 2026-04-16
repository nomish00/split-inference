import time

import torch
from PIL import Image
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights

DEVICE = "cpu"
IMAGE_PATH = "sample.jpg"


def main():
    weights = MobileNet_V2_Weights.DEFAULT
    model = mobilenet_v2(weights=weights).eval().to(DEVICE)
    preprocess = weights.transforms()

    img = Image.open(IMAGE_PATH).convert("RGB")
    x = preprocess(img).unsqueeze(0).to(DEVICE)

    t0 = time.perf_counter()
    with torch.no_grad():
        logits = model(x)
    total_ms = (time.perf_counter() - t0) * 1000

    probs = logits.softmax(dim=1)[0]
    class_id = int(probs.argmax().item())
    score = float(probs[class_id].item())
    label = weights.meta["categories"][class_id]

    print({
        "mode": "server_only",
        "device": DEVICE,
        "total_ms": round(total_ms, 2),
        "predicted_class_id": class_id,
        "predicted_label": label,
        "score": round(score, 4),
    })


if __name__ == "__main__":
    main()
