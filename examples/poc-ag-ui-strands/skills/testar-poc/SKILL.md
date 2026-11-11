---
name: testar-poc
description: Como validar o PoC ag-ui-strands — testes do agent com o modelo fake, lint/build do web, checagem do bff e os 9 cenários do README. Use antes de dar uma tarefa como concluída ou quando pedirem para rodar os testes.
---
# Validar o PoC

Python no venv: `.venv/Scripts/python` no Windows, `.venv/bin/python` no Linux/macOS (o `dev.sh` detecta).

## 1. Preparar (só se faltar)
```bash
cd agent && uv venv --python 3.13 && uv pip install -r pyproject.toml
cd ../bff && uv venv --python 3.13 && uv pip install -r pyproject.toml
cd ../web && npm install
```

## 2. Testes automáticos (sem chave, sem rede)
```bash
cd agent && .venv/bin/python -m pytest tests -q
```
Os testes forçam `MODEL_PROVIDER=fake` (`agent/app/modelo_fake.py`). Se uma tool nova não aparece
nos eventos, o roteiro do modelo fake provavelmente não foi atualizado.

## 3. Web
```bash
cd web && npm run lint && npm run build
```

## 4. bff (fumaça)
Com o bff no ar (`./dev.sh` ou uvicorn na 8001):
```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8001/agent -H "Content-Type: application/json" -d "{}"
```
Tem que dar **401** (sem `X-Tenant-Id`).

## 5. Cenários manuais (README, seção "Cenários")
Só com o stack no ar e `MODEL_PROVIDER` real ou fake. Liste quais rodou e quais não.
Os críticos: busca mostra só Tênis Runner (1), compra pausa sem número de pedido (3),
Confirmar gera `PED-0001` num novo run do mesmo thread (4), Cancelar não finaliza (5).

## Relatório
Para cada passo: comando, OK/FALHOU, e para falhas o trecho do erro e a causa provável.
