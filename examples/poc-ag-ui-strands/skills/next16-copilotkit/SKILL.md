---
name: next16-copilotkit
description: Regras para escrever código no web/ deste PoC (Next.js 16.4, React 19.3, CopilotKit 1.85 API v2, @ag-ui/client 1.0.2, zod 4). Use antes de editar qualquer arquivo em web/, criar componente, mexer em app/api/copilotkit ou atualizar dependências do front.
---
# web/: Next.js 16 + CopilotKit v2

Estas versões são mais novas que o que você sabe de cor. **Não chute APIs.**

## Antes de escrever
1. Leia `web/AGENTS.md`: manda ler os guias em `web/node_modules/next/dist/docs/` antes de codar.
2. Para CopilotKit, confira os tipos em `web/node_modules/@copilotkit/react-core/` e `@copilotkit/runtime/`
   (procure o `.d.ts` do hook antes de usar). Imports são sempre de `/v2`.
3. Se `node_modules` não existir: `cd web && npm install`.

## Como o projeto já faz (siga o padrão)
- Runtime: `web/app/api/copilotkit/route.ts` — `CopilotRuntime({ agents: { vendedor: new HttpAgent(...) } })`
  + `createCopilotRuntimeHandler({ mode: "single-route", basePath: "/api/copilotkit" })`.
- O header `X-Tenant-Id` e a `BFF_URL` ficam **no servidor** (env). O navegador só fala com `/api/copilotkit`.
- Provider: `<CopilotKit runtimeUrl="/api/copilotkit" useSingleEndpoint agentId="vendedor">`.
- O chat roda só no cliente (`next/dynamic` com `ssr: false`): o provider gera ids aleatórios e o
  Next 16 recusa isso na pré-renderização. Não remova.
- Componentes com hooks do CopilotKit: `"use client"` no topo.
- Parâmetros de tool com zod 4 (`z.object`, `z.number().int()`, `.nullish()`).
- `@ag-ui/client` tem que ficar na **mesma versão** que o `@copilotkit/runtime` usa (hoje 1.0.2).

## Não fazer
- Não tirar o bloco `nextjs-agent-rules` de `AGENTS.md` (o `next dev` recria).
- Não chamar o bff direto do navegador (o bff não tem CORS de propósito).
- Não subir versão de next/copilotkit/@ag-ui sem pedido explícito.

## Validar
`cd web && npm run lint && npm run build`.
