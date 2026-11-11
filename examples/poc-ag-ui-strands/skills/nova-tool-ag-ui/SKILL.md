---
name: nova-tool-ag-ui
description: Passo a passo para criar ou alterar uma tool do vendedor (agent Strands + ag-ui-strands) e o componente que a desenha no web (CopilotKit v2). Use sempre que a tarefa envolver uma tool nova, renomear uma tool, mudar parâmetros ou criar um card/componente para o resultado de uma tool.
---
# Nova tool no PoC AG-UI + Strands

Uma tool é ligada ao front **pelo nome** (string). Todo passo abaixo usa o mesmo nome.

## 1. Decida o tipo
- **Tool do agente** (roda no Python, front só desenha): ex. `buscar_produtos`, `listar_catalogo`, `finalizar_pedido`.
- **Tool do front** (o run pausa até o cliente agir): ex. `confirmar_pedido`. NÃO é declarada no agent.

## 2. Tool do agente
1. `agent/app/tools.py`: função com `@tool(context=True)`, recebendo `tool_context: ToolContext`.
   - Docstring com `Args:` e `Returns:` — vira a descrição para o modelo.
   - Devolva **string JSON** (`json.dumps(..., ensure_ascii=False)`); o front faz `JSON.parse(result)`.
   - Tenant: `tool_context.invocation_state.get("tenant_id")` (vem do bff via forwardedProps). Logue-o.
2. `agent/app/agent.py`: adicione na lista `tools=[...]` e explique no `SYSTEM_PROMPT` quando chamar.
3. `agent/app/modelo_fake.py`: ensine o roteiro a chamar a tool (senão os testes não a exercitam).
4. `web/components/Loja.tsx`: `useRenderTool({ name, parameters: z.object(...), render })`.
   - `status`: `inProgress | executing | complete`; `result` é string só em `complete`.
   - Mostre um aviso ("Buscando…") antes de `complete`.
   - Opcionais do Python (`float | None`) → `z.number().nullish()`.
5. Componente novo em `web/components/`, tipos em `web/types/`.

## 3. Tool do front (human-in-the-loop)
1. `web/components/Loja.tsx`: `useHumanInTheLoop({ name, description, parameters, render })`.
   - `respond(...)` só existe com `status === "executing"`; depois disso o card fica só leitura.
   - `args.x` pode chegar parcial: use `?? valor_padrao`.
2. `agent/app/main.py`: em `StrandsAgentConfig.tool_behaviors` adicione
   `"<nome>": ToolBehavior(continue_after_frontend_call=False)`.
   **Sem isso o agente recebe "Forwarded to client" e segue sem esperar** (ponto P4 do README).
3. Explique no `SYSTEM_PROMPT` o que fazer com cada resposta (ex. `confirmado: true/false`).
4. A retomada é um **novo run no mesmo thread** com um `ToolMessage` — veja `exemplos/run-agent-input-confirmar.json`.

## 4. Não mexer
- bff: não precisa saber de tools. Trocar tool ou `MODEL_PROVIDER` não muda bff nem web (cenário 9).
- Versões fixadas: `ag-ui-strands==1.0.3`, `strands-agents==1.64.0`, `ag-ui-protocol==1.0.0`, `@ag-ui/client` 1.0.2.

## 5. Feche
- Teste novo em `agent/tests/test_fluxo.py` (padrão `_run(...)` + asserts sobre os eventos AG-UI).
- Rode a skill `testar-poc` (o `auditor` já a carrega).
- Atualize a lista de tools no `README.md`.
