# split-inference-starter

Starter repo do eksperymentów **split inference** dla układu:
- Raspberry Pi 4 jako edge client,
- lokalny serwer CPU-only jako backend,
- opcjonalnie później AWS / GPU.

## Struktura repo

```text
split-inference-starter/
├── client_pi.py
├── server.py
├── inference.proto
├── inference_pb2.py
├── inference_pb2_grpc.py
├── sample.jpg
├── .gitignore
├── README.md
├── requirements/
│   ├── base.txt
│   ├── client.txt
│   ├── server-cpu.txt
│   └── dev.txt
├── scripts/
│   ├── bootstrap-client.sh
│   ├── bootstrap-server-cpu.sh
│   ├── generate_proto.sh
│   ├── run-client.sh
│   └── run-server.sh
└── docs/
    └── setup-notes.md
```

## Instalacja

### Raspberry Pi

```bash
bash scripts/bootstrap-client.sh
```

### Serwer CPU-only

```bash
bash scripts/bootstrap-server-cpu.sh
```

## Generowanie plików protobuf / gRPC

```bash
bash scripts/generate_proto.sh
```

To wygeneruje:
- `inference_pb2.py`
- `inference_pb2_grpc.py`

## Uruchomienie

### Serwer

```bash
bash scripts/run-server.sh
```

### Klient

Najpierw ustaw w `client_pi.py`:
- `SERVER_ADDR`
- `IMAGE_PATH`

Potem:

```bash
bash scripts/run-client.sh
```

## Typowy pierwszy workflow

1. `bash scripts/bootstrap-server-cpu.sh`
2. `bash scripts/generate_proto.sh`
3. `bash scripts/run-server.sh`
4. na Pi: `bash scripts/bootstrap-client.sh`
5. na Pi: `bash scripts/generate_proto.sh`
6. ustaw `SERVER_ADDR` w `client_pi.py`
7. `bash scripts/run-client.sh`

## Uwaga o plikach pb2

W tym repo możesz:
- commitować `inference_pb2.py` i `inference_pb2_grpc.py`, albo
- generować je lokalnie po każdej zmianie `inference.proto`.

Dla prostego projektu badawczego wygodne jest **commitowanie tych plików do repo**.
