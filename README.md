# Belial Timer

Protótipo funcional da interface do Belial Timer, com uma sequência de teste curta para validar o timer e as mecânicas.

O ponto de entrada atual é `main.py`. O arquivo `ui_v1.py` permanece como lançador compatível com comandos e referências anteriores.

A aplicação está organizada assim:

```text
BelialTimer_UI_v1/
├── main.py
├── ui_v1.py
├── app/
│   ├── main_window.py
│   ├── alert_scheduler.py
│   ├── alert_system.py
│   ├── config_manager.py
│   ├── events.py
│   ├── profile_manager.py
│   ├── timer_engine.py
│   └── widgets/
│       ├── background_widget.py
│       ├── compact_window.py
│       ├── header_widget.py
│       ├── mechanic_panel.py
│       ├── settings_dialog.py
│       └── timeline_widget.py
├── assets/
└── tests/
```

O pacote `app` mantém a janela principal e as responsabilidades de configuração, eventos, timer e alertas. Os componentes visuais reutilizáveis ficam em `app/widgets`. Essa organização separa cálculo e coordenação da pintura, sem redesenhar a interface.

`app/main_window.py` monta e coordena a aplicação:

- timer aguardando início manual pelo botão `INICIAR`;
- seleção entre sequência de teste e sequência real do Belial;
- alertas sonoros e visuais;
- timeline com símbolos próprios e estados de anterior, atual e próximo, transição de backgrounds e modo compacto;
- botões inferiores na ordem `INICIAR | RESETAR | SOM | ALERTA | COMPACTO`; `RESETAR` para a contagem, zera o cronômetro e devolve o botão para `INICIAR`;
- personagem Belial em PNG transparente sobreposta à esquerda entre o cabeçalho e o painel de mecânica; no modo compacto, Belial fica apoiada sobre o painel de controles;
- botões de configurações (engrenagem) e fechar (`X`) no canto superior direito;
- modo compacto independente e arrastável, com duplo clique para retornar à janela principal;
- botões `NORMAL` e `X` no modo compacto para retornar e fechar o aplicativo;
- janela de configurações para som, alertas visuais, sequência de eventos e escolha da arte do modo normal (sentada ou deitada), com pré-visualização das imagens;
- edição local do perfil de mecânicas na própria tela de configurações.
- opacidade configurável do fundo (incluindo imagens) e das letras (0–100%) nas duas janelas; os botões mantêm contraste para continuarem legíveis, as barras podem ser vinculadas ou independentes, e `Ctrl+Shift+O` restaura ambas a 100%.

`app/config_manager.py` concentra a leitura, validação e gravação das preferências.

`app/events.py` mantém as sequências de teste e real em uma única fonte de dados, separada da interface. A sequência real usa os horários confirmados até T+12:08, começa com Remoção dos Buffs em T+5 e mantém identificadores próprios para ocorrências repetidas. Os horários da sequência são verificados por testes automatizados.

Na sequência real, Remoção dos Buffs é exibida desde o início do timer, com contagem regressiva até T+5. Ao chegar a esse horário, o countdown passa imediatamente a contar até o Laser em T+20. Cada ocorrência usa somente seu horário de início; não há durações configuráveis. O relógio monotônico começa em zero no clique de iniciar.

Na aba **Mecânicas** das configurações, os nomes e horários de início podem ser personalizados, mantendo fixa a ordem das 20 ocorrências. Os bipes das mecânicas permanecem como alertas sonoros do cronograma. O botão de restauração retorna o perfil padrão.

`app/alert_system.py` contém a reprodução dos alertas sonoros em threads, sem bloquear a interface.

`app/timer_engine.py` mantém o relógio monotônico e emite ticks para a interface; também calcula, sem depender do desenho, o evento atual, o próximo evento e o tempo restante.

`app/alert_scheduler.py` controla quando cada aviso sonoro deve ser emitido uma única vez por evento; suas regras são testadas sem abrir a interface.

O widget `TimelineWidget` está isolado em `app/widgets/timeline_widget.py`; mantém os estados passado/atual/próximo, os ícones e a animação discreta, com testes próprios.

O widget `MainPanelBackground` está em `app/widgets/mechanic_panel.py`, mantendo a transição dos backgrounds e o retorno ao fundo-base sem alterar a apresentação.

Os widgets do cabeçalho, incluindo a arte com fade, o status da luta e o timer geral, foram isolados em `app/widgets/header_widget.py`; a dimensão e os elementos visuais aprovados foram preservados.

O fundo da janela principal, com gradiente, halo e bordas, foi isolado em `app/widgets/background_widget.py` e tem teste de renderização Qt.

O diálogo de configurações foi isolado em `app/widgets/settings_dialog.py`; ele reúne as abas de preferências gerais e mecânicas. Preferências e perfis são validados e persistidos em `config.json`.

O modo compacto foi isolado em `app/widgets/compact_window.py`. Ele mantém a janela arrastável, os botões de iniciar, voltar ao modo normal e fechar, e compartilha os widgets de estado com o timer principal.

O timer começa pelo botão `INICIAR` na janela principal ou no modo compacto. O botão `RESETAR` para o timer, zera a contagem e deixa o aplicativo pronto para iniciar novamente.
As preferências de som, alertas visuais, modo compacto, sequência selecionada, perfil personalizado e posições das janelas são salvas em `config.json` no diretório de configurações do usuário do Windows (normalmente `%APPDATA%\Belial Timer`). Posições salvas são reposicionadas dentro de um monitor disponível caso o monitor original não esteja conectado. Sem configuração salva, o aplicativo inicia na sequência real; a sequência de teste pode ser selecionada nas configurações. Se o arquivo estiver inválido ou corrompido, informa o problema e continua com os padrões.

## Instalação

Recomendado usar Python 3.12:

```powershell
py -3.12 -m pip install -r requirements.txt
```

## Executar

```powershell
py -3.12 main.py
```

Para compatibilidade, `py -3.12 ui_v1.py` continua iniciando a mesma aplicação.

## Testes

```powershell
py -3.12 -m unittest discover -s tests
```

## Estado do protótipo

A sequência de teste e a sequência real ficam separadas no código. O arquivo ainda não está empacotado como executável.
