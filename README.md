<div align="center">

# Belial Timer

### Curta a luta. O timer acompanha as mecânicas para você.

<img src="./assets/belial_deitada.png" alt="Belial deitada, arte do Belial Timer" width="520">

Um timer para ajudar a acompanhar as mecânicas da luta contra Belial, com contagem regressiva, avisos e uma janela compacta para deixar na tela.

</div>

<p align="center">
  <img src="https://img.shields.io/badge/feito%20com-Python-blue?logo=python&logoColor=white" alt="Feito com Python">
  <img src="https://img.shields.io/badge/interface-PySide6-41CD52?logo=qt&logoColor=white" alt="Interface PySide6">
  <img src="https://img.shields.io/badge/status-em%20desenvolvimento-orange" alt="Em desenvolvimento">
</p>

---

## Como ele ajuda durante a luta

Depois de apertar **INICIAR**, o timer mostra qual mecânica está acontecendo, quanto falta para a próxima e o que vem depois. Você pode deixar os avisos sonoros ligados para receber um lembrete sem precisar ficar olhando para a janela.

Na sequência real, o timer começa contando até a **Remoção dos Buffs**, que acontece em T+5. Quando essa contagem termina, ele já mostra o tempo até o próximo evento.

## Do seu jeito

- **Janela normal ou compacta:** escolha a visualização que fica melhor na sua tela. A janela compacta pode ser arrastada; dê dois cliques nela para voltar à janela normal.
- **Imagem da Belial:** escolha entre as artes sentada e deitada e veja uma prévia nas configurações.
- **Avisos:** ligue ou desligue os bipes e os alertas visuais.
- **Transparência:** ajuste o fundo e as letras. Você pode mudar cada um separadamente ou vinculá-los.
- **Mecânicas:** escolha a sequência real ou a de teste e, se quiser, personalize os nomes e horários.
- **Posição das janelas:** o programa lembra onde você deixou cada modo. Se aquela área da tela não estiver mais disponível, ele traz a janela de volta para uma área visível.

O botão **RESETAR** para a contagem e deixa o timer pronto para começar de novo. O atalho `Ctrl+Shift+O` restaura a opacidade do fundo e das letras para 100%.

## Baixar para Windows

Quando houver uma versão publicada, baixe `BelialTimer-windows-x64.zip` na página **Releases** do GitHub. Extraia o ZIP inteiro e abra `BelialTimer.exe` dentro da pasta `BelialTimer`. Mantenha os arquivos juntos; o executável precisa deles para abrir.

Como o programa ainda não tem assinatura digital, o Windows pode mostrar um aviso de reputação. Baixe o ZIP somente da página oficial de Releases do projeto.

## Executar pelo código

Para testar o código-fonte, é necessário ter o Python instalado no Windows.

1. Instale o **Python 3.12**, caso ainda não tenha.
2. Baixe este projeto pelo botão **Code → Download ZIP** no GitHub e extraia os arquivos.
3. Abra o PowerShell dentro da pasta extraída.
4. Instale os componentes necessários:

   ```powershell
   py -3.12 -m pip install -r requirements.txt
   ```

5. Inicie o Belial Timer:

   ```powershell
   py -3.12 main.py
   ```

O arquivo `requirements.txt` instala apenas o necessário para usar o programa. As ferramentas para gerar uma versão distribuível ficam separadas em `requirements-build.txt`.

## Preparar uma versão para download

O pacote é uma pasta compactada (ZIP); ainda não há instalador. Para preparar o pacote a partir do código-fonte, instale as ferramentas de build e execute:

```powershell
py -3.12 -m pip install -r requirements-build.txt
.\build_release.ps1
```

O ZIP será criado em `dist/BelialTimer-windows-x64.zip`. Ao enviar uma tag `v*` para o GitHub, uma versão de teste é compilada no Windows e publicada automaticamente na página **Releases**.

Sugestões para deixar o timer melhor são bem-vindas!
