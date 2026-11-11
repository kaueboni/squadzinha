# Exemplo: skills de projeto (PoC AG-UI + Strands)

Skills escritas para um projeto com três partes: web (Next.js 16 + CopilotKit v2),
bff (FastAPI) e agent (Strands + ag-ui-strands).

| Skill | Para quem | O que ensina |
|---|---|---|
| `nova-tool-ag-ui` | developer | criar/alterar uma tool ponta a ponta (Python + componente) e as armadilhas (`continue_after_frontend_call=False`, modelo fake) |
| `next16-copilotkit` | developer | ler os docs do `node_modules` antes de codar; padrões do runtime v2; versões fixadas |
| `testar-poc` | auditor | pytest com modelo fake, lint/build do web, fumaça do bff, cenários do README |

## Como usar no projeto

1. Copie `skills/*` para `.claude/skills/` do projeto.
2. Em `.claude/minimal-squad.json`, acrescente:

```json
"overrides": {
  "agents": {
    "developer": { "skills_extra": ["nova-tool-ag-ui", "next16-copilotkit"] },
    "auditor":   { "skills_extra": ["testar-poc"] }
  }
}
```

3. Rode `/minimal-squad:init --atualizar` (ou `install.py --steps agents`).

O developer fica com 5 skills (3 da squad + 2 daqui). O instalador aceita e só
avisa que passou do recomendado (4), porque cada skill aumenta o contexto. Se
quiser ficar no limite, troque `next16-copilotkit` por uma regra no `CLAUDE.md`
do projeto.
