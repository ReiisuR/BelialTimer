# Instruções para agentes de código — BelialTimer

Este arquivo é destinado a Codex e outros agentes que trabalhem **localmente** neste repositório. Leia também [ROADMAP.md](ROADMAP.md) e [CONTRIBUTING.md](CONTRIBUTING.md) antes de alterações maiores.

## Objetivo

Aplicativo Python 3.12 / PySide6 para Digimon Masters Online. O projeto evolui do timer Belial para uma Central de DGs, mantendo o timer compacto do **Pesadelo (Belial)** como primeiro módulo funcional.

## Decisões de produto — não contrariar sem autorização
1. **Belial = Pesadelo**, uma única DG, identificador `pesadelo` no catálogo.
2. O painel principal é um menu e tem visual fixo por enquanto.
3. Jogadores ajustam as preferências **antes** de iniciar a DG.
4. Preferências globais de fundo, letras e alertas devem se aplicar aos módulos/timers de DG, incluindo compacto, e não alterar o estilo da Central.
5. Mecânicas e sequência de teste/real do Belial são específicas dessa DG.
6. A arte do compacto deve ser selecionável entre `cotovelo`, `sentada` e `deitada`; a configuração da arte normal é separada.
7. X/CENTRAL do compacto devem retornar à Central. Não encerrar o aplicativo ao voltar.
8. Não inventar mecânicas, dificuldades ou dados de DGs.
9. Preservar compatibilidade com configurações já salvas e testes existentes.

## Mapa do código
- `main.py`: inicia QApplication, Central e integração de navegação/retorno ao timer.
- `app/dungeon_dashboard.py`: painel, busca, filtros, cartões e sinais.
- `app/dungeon_catalog.py`: catálogo de DGs e metadados.
- `app/main_window.py`: motor/estado do Belial, configurações, integração com compacto e janela normal legada.
- `app/widgets/compact_window.py`: UI compacta e arte do personagem.
- `app/widgets/header_widget.py`: `HeaderArtWidget`, caminhos das imagens e cabeçalho legado.
- `app/widgets/settings_dialog.py`: editor atual; abas Geral e Belial.
- `app/config_manager.py`: defaults, validação, carregamento e salvamento das preferências.
- `app/profile_manager.py`: perfil e validação das mecânicas.
- `app/design_system/`: tokens e temas.
- `tests/`: testes unittest; `assets/`: artes; `build_release.ps1`: pacote Windows.

## Prioridade imediata

**Bug reportado:** trocar a arte em Configurações não alterou visualmente a imagem no compacto para o usuário. A implementação já possui `compact_art`, `set_character_art()` e prévia no diálogo, mas isso **não comprova** que o fluxo funcione na tela real.

Investigue o fluxo completo e o estado do widget, inclusive geometria, pintura, `raise_()`, `update()`, visibilidade, caminho do arquivo e persistência. Verifique que o usuário esteja modificando **Imagem do timer compacto** e não **Imagem da Belial (modo normal)**. Não considere o problema resolvido apenas porque o valor no JSON mudou. Adicione regressão e solicite teste visual no Windows quando necessário.

## Padrões de implementação
- Fazer mudanças pequenas, testáveis e focadas; evitar refatorações amplas sem necessidade.
- Reutilizar a lógica validada do timer; não duplicar motores para novas DGs.
- Separar configurações globais de preferências exclusivas de uma DG.
- Manter interface e documentação em português brasileiro.
- Respeitar os padrões de estilo do projeto; preservar a paleta dark-fantasy da Central.
- Evitar quebrar sinais Qt, ciclo de vida das janelas, persistência e compatibilidade com Python 3.12.
- Se alterar chaves de configuração, fornecer default, validação e migração compatível.
- Não alterar arte, conteúdo ou cronograma de mecânicas sem requisito confirmado.
- Não apagar funcionalidades legadas antes de haver substituição e testes.
- Não modificar arquivos não relacionados nem sobrescrever alterações locais do usuário.
- Não criar commits ou fazer push automaticamente sem instrução explícita na tarefa local.

## Rotina para cada tarefa
1. Ler `ROADMAP.md` e os arquivos envolvidos.
2. Descrever brevemente causa/abordagem, quando for bug.
3. Implementar correção mínima com testes.
4. Executar `py -3.12 -m unittest discover -s tests -v`.
5. Para UI, executar `py -3.12 main.py` e validar manualmente no Windows quando possível.
6. Informar arquivos modificados, comportamento esperado, testes executados e limitações.
7. Atualizar `ROADMAP.md` quando uma etapa mudar de estado.

**Importante:** testes Qt em `offscreen` não substituem inspeção visual real. Nunca afirmar que testou a interface manualmente se não testou.

## Comandos rápidos (PowerShell)
```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 -m unittest discover -s tests -v
py -3.12 main.py
```

## Trabalhando com Codex local

Abra a pasta raiz clonada no VS Code, mantenha este `AGENTS.md` na raiz e peça ao agente para ler `ROADMAP.md` antes de começar. Sugestão de primeira tarefa:

> Leia AGENTS.md e ROADMAP.md. Investigue o bug P0 da arte do Belial no compacto. Corrija a causa, acrescente testes e execute a suíte. Preserve o retorno à Central e não faça commit/push sem minha confirmação.

## Segurança de escopo

Não presumir acesso ao computador, GitHub ou execução do usuário. Relatar claramente o que foi efetivamente verificado.
