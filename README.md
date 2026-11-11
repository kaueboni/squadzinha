# squadzinha

Versão do [minimal-squad](https://github.com/kaueboni/minimal-squad) com o
**advisor** do Claude Code: o Sonnet trabalha, o Opus aconselha nos pontos
difíceis, e a squad para menos sem tirar de você as decisões que importam.
Visão geral ilustrada: [`docs/funcionamento.html`](docs/funcionamento.html).
O plugin continua se chamando `minimal-squad` (comando `/minimal-squad:init`);
o marketplace se chama `squadzinha`.

> Se o `minimal-squad` original estiver instalado na mesma máquina, desinstale
> antes (`/plugin uninstall minimal-squad@minimal-squad`): os dois usam o mesmo nome.

## O que o advisor muda

`params.advisor` (padrão `opus`; vazio desliga) vai para `advisorModel` no
`.claude/settings.json`. Os subagentes herdam o advisor.

| Momento | Sem advisor | Com advisor |
|---|---|---|
| 3ª reprovação do auditor | para | consulta o advisor (causa raiz), faz **uma** última rodada; só para se reprovar de novo |
| Spec ambígua no `/build auto` | para | o advisor escolhe a interpretação; a suposição vai no commit e no relatório final |
| Mesmo erro 2x no developer | — | consulta o advisor antes da 3ª tentativa |
| Spec e plano do tech-lead | — | advisor revisa riscos e lacunas antes de entregar |

O advisor **nunca** decide: aprovação da spec e do plano, apagar ou enfraquecer
testes, itens "Ask first" do `SPEC.md` (schema, dependência, credencial,
infraestrutura) e nada que `git revert` não desfaça. Ele não edita arquivos.

Requisitos: Claude Code com o advisor (`/advisor`); modelo principal Sonnet 4.6+,
Opus 4.6+ ou Haiku 4.5. No alvo Copilot o advisor é ignorado.

## Sem contract-tester

A minimal-squad 0.2.0 tinha um sexto agente que escrevia "testes de contrato"
antes do código. Ele saiu: os testes eram escritos a partir da spec, com
mocks, e repetiam o TDD do developer sem checar a integração de verdade (isso
continua sendo dos testes `integration`, que só humanos rodam). Ficou a parte
útil: em tarefa com "Integração: sim", o auditor exige um teste com mock para
cada item de "Impacto em integrações" da spec (idempotência, configuração,
erro do serviço, como desfazer, schema). Num projeto que já tinha a squad,
`/minimal-squad:init --atualizar` remove o `contract-tester.md` se você não o
editou; `tests/contract/` fica onde está.

## Skills do projeto

A squad traz skills genéricas. Skills do seu projeto (stack, armadilhas,
como validar) entram pelos `overrides` do `.claude/minimal-squad.json`:

```json
"overrides": {
  "agents": {
    "developer": { "skills_extra": ["nova-tool-ag-ui", "next16-copilotkit"] },
    "auditor":   { "skills_extra": ["testar-poc"] }
  }
}
```

As skills precisam existir em `.claude/skills/` do projeto. Exemplo completo
(PoC AG-UI + Strands, Next.js 16 + CopilotKit): [`examples/poc-ag-ui-strands/`](examples/poc-ag-ui-strands/).

---

Plugin do Claude Code que **instala no seu projeto** uma squad mínima de
spec-driven development (SDD): cinco subagentes, cinco comandos, skills de
engenharia e guardrails. Depois de instalada, a squad vive no repositório
(`.claude/`), vai para o git e o time inteiro herda. O plugin só é
necessário para instalar, religar integrações e atualizar.

Python primeiro (pytest; ruff ou flake8 se o projeto usar).

## O que é instalado no projeto

| Onde | O quê |
|---|---|
| `.claude/agents/` | `discovery`, `researcher`, `tech-lead`, `developer`, `auditor` |
| `.claude/commands/` | `/spec`, `/build` (e `/build auto`), `/review`, `/test`, `/onboard` |
| `.claude/skills/` | 10 skills de [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT), cópia fixa |
| `.claude/references/` | checklists usados pelas skills |
| `.claude/settings.json` | permissões (merge; nada é removido) |
| `.githooks/` | pre-commit: spec de base fixa, busca de segredos, lint, testes |
| `CLAUDE.md` | um bloco curto delimitado (`minimal-squad:start/end`) |
| `PROGRESS.md` | estado do projeto, histórico, testes e setup (só se não existir) |
| `specs/`, `tasks/`, `tests/fixtures/` | estrutura do fluxo |
| `.claude/minimal-squad.json` | parâmetros confirmados por você |
| `.claude/minimal-squad.lock.json` | hashes do que o plugin gravou (permite atualizar sem pisar em edições suas) |

### A squad

| Agente | Papel | Ferramentas | Modelo padrão |
|---|---|---|---|
| discovery | mapeia o projeto como ele é; só leitura | Read, Grep, Glob | haiku |
| researcher | confere documentação oficial | WebSearch, WebFetch | haiku |
| tech-lead | escreve a spec e o plano | Read, Grep, Glob, Write, Edit | sonnet |
| developer | implementa uma tarefa com TDD | Read, Grep, Glob, Edit, Write, Bash | sonnet |
| auditor | audita; não edita | Read, Grep, Glob, Bash | sonnet |

### O fluxo

```
/spec <feature>        discovery → researcher → tech-lead escreve specs/NNN-SPEC-<feature>.md
                       ⏸ você aprova a spec
/build auto NNN        tech-lead gera tasks/plan.md e tasks/todo.md
                       ⏸ você aprova o plano
                       por tarefa: developer → auditor → commit
/review                auditor revisa a branch inteira
                       você roda os testes de integração, faz push e deploy
```

Convenções: `SPEC.md` é a spec de base e é **fixa** para os agentes;
testes de integração (`@pytest.mark.integration`) **nunca** são rodados por
agentes; fixtures são sempre fictícias.

## Instalação

### Ordem recomendada com os plugins parceiros

1. [agentmeter](https://github.com/kaueboni/agentmeter) (opcional): mede tokens por subagente desde o início.
2. [cortex-lite](https://github.com/kaueboni/cortex-lite) (opcional): memória entre sessões e agentes.
3. **minimal-squad**: o `/minimal-squad:init` detecta os dois e liga a squad a eles.

A ordem não é obrigatória: se instalar um parceiro depois, rode
`/minimal-squad:init --integracoes`.

### Instalar o plugin

```
/plugin marketplace add kaueboni/squadzinha
/plugin install minimal-squad@squadzinha
```

Requisitos: Claude Code com suporte a plugins, git, Python 3.9+ no PATH
(`python3`, `python` ou `py`).

**Windows:** instale o [Git for Windows](https://git-scm.com/download/win) (Git Bash). O Claude Code e o hook de pre-commit rodam nele. Se o projeto usa `.venv`, o `init` grava `test_cmd` e `lint_cmd` com o Python do venv (`.venv/Scripts/python -m pytest -q`), então não precisa ativar o ambiente para commitar.

### Instalar a squad num projeto

Na raiz do projeto (repositório git, sem mudanças pendentes):

```
/minimal-squad:init
```

O comando detecta os parâmetros (comando de testes, lint, specs existentes,
hooks, integrações), mostra tudo e **espera sua confirmação**. Depois cria a
branch `chore/minimal-squad` e aplica em etapas, com um commit por etapa.
Nada é publicado: você revisa e abre o PR.

Se um arquivo do projeto conflitar (por exemplo, um `/spec` seu), o plugin
**não sobrescreve**: grava a versão nova em `.claude/.minimal-squad-pending/`
e lista no relatório para você decidir.

Depois: reinicie o Claude Code.

## GitHub Copilot

A mesma squad também pode ser instalada para o **GitHub Copilot** (VS Code,
Copilot CLI e cloud agent). Não precisa do Claude Code: o instalador roda
direto com Python.

```
git clone https://github.com/kaueboni/squadzinha ~/minimal-squad
cd <seu projeto>                       # repositório git, sem mudanças pendentes
git checkout -b chore/minimal-squad
python ~/minimal-squad/scripts/install.py --project . --init-config --target copilot
# revise .github/minimal-squad.json (test_cmd, lint_cmd, specs_dir, base_spec...)
python ~/minimal-squad/scripts/install.py --project . --steps all
```

O que muda em relação ao Claude Code:

| Claude Code | GitHub Copilot |
|---|---|
| `.claude/agents/<agente>.md` | `.github/agents/<agente>.agent.md` |
| `.claude/commands/<cmd>.md` | `.github/prompts/<cmd>.prompt.md` (mesmos `/spec`, `/build`, `/review`, `/test`, `/onboard`) |
| `.claude/skills/`, `.claude/references/` | `.github/skills/`, `.github/references/` |
| `CLAUDE.md` (bloco) | `.github/copilot-instructions.md` (bloco) |
| `.claude/settings.json` (allow/deny) | `.vscode/settings.json` → `chat.tools.terminal.autoApprove` |
| `.claude/minimal-squad.json`, lock, pendentes | `.github/minimal-squad.json`, lock, pendentes |
| `/minimal-squad:init` escreve a spec de base | prompt `/base-spec` (rode uma vez depois de instalar) |

- **Agentes**: ferramentas convertidas para os aliases do Copilot
  (`read`, `search`, `edit`, `execute`, `web`). As skills de cada agente
  viram uma instrução no início do arquivo ("leia e siga
  `.github/skills/.../SKILL.md`"). `maxTurns` e `effort` não existem no
  Copilot e são omitidos.
- **Modelos**: por padrão o agente usa o modelo escolhido no Copilot. Para
  fixar, preencha `copilot_model_read` (discovery, researcher) e
  `copilot_model_work` (os demais) em `.github/minimal-squad.json`.
- **Orquestração**: os prompts rodam no modo agente com a ferramenta
  `agent`, e chamam cada papel como subagente (cada chamada recebe todo o
  contexto de que precisa). O researcher usa `web`, que não existe no
  cloud agent.
- **Integrações**: cortex-lite, agentmeter, Ponytail e rtk são do Claude
  Code e ficam desligados no alvo copilot.
- **Guardrails**: o pre-commit é o mesmo. A auto-aprovação do terminal no
  VS Code é conveniência, não barreira: `false` só obriga a pedir
  aprovação. Se o `.vscode/settings.json` tiver comentários, o instalador
  não mexe e mostra as regras para você colar.
- **Spec de base**: o pre-commit bloqueia commits que alteram a spec de
  base; o primeiro commit dela (depois do `/base-spec`) é seu, com
  `--no-verify`.

Atualizar depois de um `git pull` no minimal-squad:
`python ~/minimal-squad/scripts/install.py --project . --steps all --check`
para ver o que muda, e sem `--check` para aplicar. Arquivos que você editou
vão para `.github/.minimal-squad-pending/`.

## Integrações (opcionais e desacopladas)

O minimal-squad é o único que conhece os outros plugins. Eles não sabem da
squad.

- **cortex-lite**: cada agente recebe as ferramentas de memória do perfil
  dele (mapeamento em `templates/integrations/cortex-lite.json`):
  discovery → leitor; researcher → pesquisador;
  tech-lead → decisor; developer → executor; auditor → revisor. Ninguém
  recebe `memory_delete`. O `/build auto` exporta a memória para
  `docs/MEMORIA.md` no fim de cada feature.
- **agentmeter**: só observa; o `/build auto` sugere `/agentmeter:tokens --sessao`.
- **Ponytail** e **rtk**: detectados; o rtk ganha regras de permissão com
  prefixo `rtk`, e o Ponytail fica restrito ao diff de cada tarefa.

Sem eles, a squad funciona igual, só sem memória e sem medição.

## Comandos do plugin

| Comando | O que faz |
|---|---|
| `/minimal-squad:init` | instalação completa, com confirmação |
| `/minimal-squad:init --integracoes` | religa cortex-lite, agentmeter, Ponytail e rtk |
| `/minimal-squad:init --atualizar` | aplica uma versão nova do plugin (mostra antes o que muda) |

Os scripts também rodam direto, sem o Claude:

```
python scripts/detect.py --project <projeto>          # só lê
python scripts/inventory.py --project <projeto>       # uso real do Claude Code no projeto
python scripts/install.py --project <projeto> --steps all --check
python scripts/install.py --project <projeto> --init-config --target copilot   # ver "GitHub Copilot"
```

## Segurança

- O instalador é determinístico e não usa rede.
- As permissões instaladas bloqueiam `git push`, `git reset --hard`,
  `git clean`, `rm -rf`, leitura de `.env`, escrita na spec de base, no
  `.claude/settings.json` e em `.githooks/`.
- O pre-commit bloqueia alteração na spec de base, padrões comuns de
  segredos, lint e testes falhando.
- Nada disso substitui revisão humana no PR.

## Licença

MIT. As skills em `templates/skills/` são de Addy Osmani, também MIT; veja
`THIRD_PARTY_NOTICES.md`.
