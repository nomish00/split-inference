# Setup notes

## Minimalny test

### Serwer
```bash
bash scripts/bootstrap-server-cpu.sh
bash scripts/generate_proto.sh
bash scripts/run-server.sh
```

### Raspberry Pi
```bash
bash scripts/bootstrap-client.sh
bash scripts/generate_proto.sh
bash scripts/run-client.sh
```

## Jeśli pojawi się błąd importu pb2

Uruchom ponownie:

```bash
bash scripts/generate_proto.sh
```

## Jeśli klient nie łączy się z serwerem

Sprawdź:
- poprawność `SERVER_ADDR`,
- czy port `50051` jest otwarty,
- czy serwer nasłuchuje na LAN.
