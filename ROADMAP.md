# Roadmap — BelialTimer

> Estado de referência: 20/11/2026. Atualize este documento conforme as mudanças forem implementadas e testadas.
> "Implementado" significa presente no código; não implica validação visual no Windows.

## Visão do produto

O BelialTimer está evoluindo de um timer exclusivo do Belial para uma **Central de DGs** de Digimon Masters Online. O painel principal é um menu com aparência fixa por enquanto. O jogador prepara as preferências antes de entrar na DG; cada DG poderá ter sua própria tela, mecânicas e timer, com preferências gerais compartilhadas.

**Decisões confirmadas**
- **Pesadelo e Belial são a mesma DG**: não criar cartões duplicados.
- **Central de DGs** é a entrada do aplicativo; a janela compacta é a interface principal do timer do Pesadelo.
- Botões **X** e **CENTRAL** do compacto retornam ao painel, em vez de encerrar o aplicativo.
- Preferências de fundo, letras e alertas devem ser **globais para as telas/timers de DGs**, não para o visual fixo do painel.
- Perfil de mecânicas, sequência e modo de teste atuais são **exclusivos do Belial/Pesadelo**.
- Artes sentada, deitada e cotovelo devem poder ser escolhidas para o compacto; a janela normal legada tem seletor separado.
- Não inventar mecânicas, NPCs ou dificuldades ainda não confirmados.

## Situação atual

### Implementado no código
- [x] Central de DGs com seis cartões, busca por nome/sigla/NPC e filtros de dificuldade.
- [x] Pesadelo abre o timer existente do Belial no modo compacto.
- [x] Retorno do timer à Central via X/CENTRAL.
- [x] Botão Configurações na barra lateral da Central.
- [x] Editor existente com abas **Geral** e **Belial** (antiga Mecânicas).
- [x] Configuração persistente de `compact_art` com opções `cotovelo`, `sentada` e `deitada`.
- [x] Pré-visualização da arte compacta no editor.
- [x] Testes automatizados para catálogo, dashboard, configurações e compacto.

### Pendente de validação / problema relatado
- [ ] **P0 — Imagem selecionada não altera visualmente o compacto**, segundo teste manual do usuário. A seleção e o método de aplicação existem no código, mas o resultado visual ainda não foi confirmado. Investigar renderização, geometria, visibilidade, atualização do widget e comportamento após salvar/reabrir. Não declarar corrigido sem teste manual.
- [ ] Confirmar no Windows a persistência da imagem escolhida após reiniciar o aplicativo.
- [ ] Confirmar que preferências globais de fundo/letras realmente afetam o compacto, e não apenas a janela normal.

## Próximas etapas

### P0 — Corrigir e estabilizar o compacto
- [ ] Reproduzir a falha da troca de arte no Windows.
- [ ] Conferir `SettingsDialog.compact_art_combo` → `MainWindow.open_settings()` → `CompactWindow.set_character_art()` → `HeaderArtWidget`.
- [ ] Verificar o posicionamento e o recorte de cada arte no compacto; preservar legibilidade do contador e dos botões.
- [ ] Testar atualização após clicar OK, reabrir a DG e reiniciar o aplicativo.
- [ ] Acrescentar testes de regressão que validem a seleção e o caminho da imagem.
- [ ] Evitar quebrar o retorno à Central ou o arraste do compacto.

**Concluído quando:** as três artes aparecem corretamente no compacto, a escolha persiste e o usuário confirma o comportamento visual.

### P1 — Configurações gerais e por DG
- [ ] Separar claramente **preferências globais** (fundo, letras, som, alertas) das opções **Belial** (mecânicas, horários, teste).
- [ ] Fazer preferências globais atuarem sobre as telas compactas e futuras telas de DG, sem modificar a aparência fixa da Central.
- [ ] Melhorar a organização do editor para não expor opções da janela normal legada como se fossem do compacto.
- [ ] Decidir, com base em teste real, se a janela normal legada pode ser removida ou mantida como recurso secundário.
- [ ] Garantir compatibilidade com `config.json` existente, incluindo migração de chaves quando necessário.

**Concluído quando:** mudar uma preferência geral afeta o compacto e pode ser reutilizado pelas futuras DGs; opções de mecânicas do Belial não vazam para outras DGs.

### P2 — Base reutilizável de DGs
- [ ] Definir interface comum para tela de DG, preferências e ciclo de vida.
- [ ] Separar lógica de timer, visualização e dados específicos do Belial sem reescrever a lógica validada desnecessariamente.
- [ ] Planejar como cada DG define suas próprias dificuldades e mecânicas.
- [ ] Preservar busca, filtros e navegação da Central.
- [ ] Adicionar testes para navegação e configurações compartilhadas.

**Concluído quando:** uma nova DG puder ser adicionada sem copiar o timer inteiro do Belial.

### P3 — Conteúdo das outras DGs
- [ ] Imperador Digimon — MDG (Normal/Fácil).
- [ ] Base do Imperador — CDGN/CDGE.
- [ ] Destruição e Regeneração — SDG (Normal/Fácil).
- [ ] DarkWeb — DW (dificuldades ainda não cadastradas).
- [ ] Terra do Nunca — NEVER (dificuldades ainda não cadastradas).
- [ ] Coletar e validar mecânicas e regras com o usuário antes de implementar alertas/timers.

**Concluído quando:** cada DG tiver conteúdo validado e testes apropriados; não inventar dados.

### P4 — Polimento e distribuição
- [ ] Refinar responsividade, acessibilidade, contraste e disposição de artes.
- [ ] Atualizar README, imagens e documentação de uso.
- [ ] Revisar build Windows, assets e fluxo de Releases.
- [ ] Fazer validação manual em Windows e regressão automatizada.

## Registro de validação

Último resultado de testes **informado pelo usuário antes das alterações recentes**: 90 testes aprovados. Depois foram adicionados novos testes e mudanças; executar a suíte para obter a contagem atual. Não usar uma contagem esperada como prova de execução.

Comandos:
```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 -m unittest discover -s tests -v
py -3.12 main.py
```

## Regra de manutenção

Ao concluir uma tarefa, atualizar a caixa correspondente, registrar o teste realizado e manter README/AGENTS.md coerentes. Para tarefas ainda não verificadas no Windows, marcar **implementado, aguardando validação**, não **concluído**.
