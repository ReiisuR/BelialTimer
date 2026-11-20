# Guia de desenvolvimento local — BelialTimer

## Objetivo

Este guia permite trabalhar no BelialTimer pelo **VS Code + Codex local**, sem baixar um ZIP do GitHub a cada alteração.

## 1. Clonar uma única vez

Instale Git e Python 3.12. No PowerShell:

```powershell
git clone https://github.com/ReiisuR/BelialTimer.git
cd BelialTimer
code .
```

A partir daí, trabalhe nessa pasta. Não é necessário baixar novamente o ZIP.

## 2. Instalar dependências e executar

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 main.py
```

Para testes:

```powershell
py -3.12 -m unittest discover -s tests -v
```

Para build Windows, quando necessário:

```powershell
py -3.12 -m pip install -r requirements-build.txt
.\build_release.ps1
```

## 3. Fluxo recomendado com Codex

1. Abra a raiz do repositório no VS Code.
2. Peça ao Codex para ler `AGENTS.md` e `ROADMAP.md`.
3. Trabalhe em **uma tarefa por vez**, começando pelo P0.
4. Revise o diff antes de aceitar as alterações.
5. Execute testes e valide mudanças visuais no Windows.
6. Só depois faça commit e push.

Prompt sugerido:

> Leia AGENTS.md, ROADMAP.md e o código relacionado. Resolva a primeira pendência P0, sem mudar outras funcionalidades. Acrescente testes, execute a suíte, descreva o que mudou e aguarde minha aprovação antes de commit/push.

## 4. Atualizar seu repositório local

Antes de iniciar trabalho, se não houver alterações locais pendentes:

```powershell
git pull --ff-only origin main
```

Verifique alterações:

```powershell
git status
git diff
```

Se houver mudanças locais, **não rode comandos destrutivos** para forçar um pull. Faça commit, guarde as mudanças com cuidado ou resolva os conflitos conscientemente.

## 5. Enviar mudanças ao GitHub

Depois de revisar e testar:

```powershell
git add .
git commit -m "fix: corrigir troca de arte no compacto"
git push origin main
```

Prefira adicionar arquivos específicos em vez de `git add .` se houver arquivos pessoais ou mudanças não relacionadas. Se o push for rejeitado, investigue o histórico antes de sincronizar; não use `push --force` na `main`.

## 6. Regras de validação

- Testes automatizados: `py -3.12 -m unittest discover -s tests -v`.
- Interface: iniciar `py -3.12 main.py` e testar navegação, preferências e compacto.
- Mudanças de UI devem ser validadas visualmente: o Qt offscreen não garante posicionamento correto.
- Registrar pendências não verificadas no `ROADMAP.md`.

## 7. Arquivos de referência

- [README.md](README.md): visão geral e instruções de uso.
- [ROADMAP.md](ROADMAP.md): prioridades e critérios de conclusão.
- [AGENTS.md](AGENTS.md): contexto e regras para agentes de código.

## 8. Quando usar branch

Para mudanças maiores, prefira criar uma branch e abrir um pull request:

```powershell
git switch -c feat/nova-dg
```

Para pequenos ajustes, é possível trabalhar na `main` conforme a preferência do mantenedor, sempre revisando testes e diff antes de enviar.
