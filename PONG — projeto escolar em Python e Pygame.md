# PONG — projeto escolar em Python e Pygame

Jogo de tênis de mesa de arcade para **dois jogadores no mesmo teclado**. O visual é retrô e original: fundo escuro, linha central pontilhada e raquetes simples, sem usar imagens ou gráficos proprietários.

## Arquivos do projeto

- `main.py` — jogo completo: menus, desenho, controles, colisões, pontuação, aceleração e efeitos sonoros sintetizados.
- `requirements.txt` — lista a dependência Python necessária (Pygame).
- `README.md` — estas instruções e explicação do código.
- `.gitignore` — evita guardar arquivos temporários e pastas de ambiente virtual.

Não é necessário baixar imagens, músicas, fontes ou outros dados. Depois de instalar o Pygame, o jogo não precisa de internet, servidor ou banco de dados.

## Requisitos

- Python 3.9 ou mais recente (Python 3.10+ recomendado).
- Teclado; dois jogadores usam o mesmo teclado.
- Para criar o executável: conexão à internet durante a instalação do PyInstaller; o executável final pode ser usado sem internet.

## Instalar e executar

Abra o Terminal (macOS/Linux) ou PowerShell/Prompt de Comando (Windows), entre na pasta do projeto e rode:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```
Se o PowerShell bloquear a ativação, use o Prompt de Comando:
```bat
.venv\Scripts\activate.bat
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Instale a dependência e inicie o jogo:

```bash
python -m pip install -r requirements.txt
python main.py
```

Em alguns computadores, o comando pode ser `python3` em vez de `python`.

## Como jogar

1. No menu, clique em **INICIAR** ou pressione **Enter/Espaço**.
2. Jogador 1, à esquerda: **W** sobe e **S** desce.
3. Jogador 2, à direita: **↑** sobe e **↓** desce.
4. Marque pontos fazendo a bola passar pela raquete adversária. O primeiro a **10 pontos** vence.
5. Após a vitória, clique em **JOGAR NOVAMENTE** ou pressione **Enter/Espaço**.
6. **F11** alterna entre janela e tela cheia. **Esc** durante a partida volta ao menu; no menu ou na tela de vitória, fecha o jogo.

O mouse é usado apenas nos botões dos menus. Não move as raquetes. Se o computador não tiver saída de áudio disponível, a partida continua sem som.

## Mostrar o jogo em uma TV por HDMI

1. Ligue uma ponta do cabo HDMI ao computador e a outra a uma entrada HDMI da TV.
2. Na TV, selecione a entrada correta (por exemplo, **HDMI 1** ou **HDMI 2**).
3. No computador, escolha como usar a segunda tela:
   - **Windows:** pressione `Win + P` e escolha **Duplicar** para mostrar a mesma imagem nas duas telas, ou **Estender** para usar a TV como tela separada.
   - **macOS:** abra **Ajustes do Sistema → Monitores**; ative o espelhamento ou organize as telas. Os nomes podem variar conforme a versão.
   - **Linux:** abra **Configurações → Monitores/Telas** e selecione **Espelhar** ou configure a TV como tela externa. Os nomes variam por ambiente gráfico.
4. Execute `python main.py`. Pressione **F11** para preencher a tela. Se estiver no modo **Estender**, arraste a janela do jogo para a TV antes de usar F11.
5. Se quiser o áudio na TV, selecione a TV/HDMI como dispositivo de saída de som nas configurações de áudio do sistema.

A resolução do jogo é ajustada para caber na tela mantendo a proporção. Dependendo do formato da TV, podem surgir pequenas faixas pretas; isso evita distorcer a imagem.

## Criar um executável para apresentar na escola (PyInstaller)

O PyInstaller precisa ser instalado no mesmo sistema operacional no qual o executável será usado. Faça o processo no Windows para gerar para Windows, no macOS para macOS e no Linux para Linux.

Com o ambiente virtual ativado, instale o empacotador:

```bash
python -m pip install pyinstaller
```

Na pasta que contém `main.py`, gere o executável:

**Windows**
```powershell
python -m PyInstaller --onefile --windowed --name PongEscolar main.py
```
O arquivo será `dist\PongEscolar.exe`.

**macOS / Linux**
```bash
python -m PyInstaller --onefile --windowed --name PongEscolar main.py
```
O resultado ficará em `dist/PongEscolar` (no macOS pode ser necessário assinar ou autorizar a execução, conforme as regras do computador).

Para apresentar, copie o executável produzido na pasta `dist` para um pendrive ou para o computador da escola. Teste-o antes da apresentação. É recomendável testar também no mesmo sistema operacional e arquitetura do computador da escola. O primeiro início pode levar alguns segundos. Alguns antivírus podem examinar executáveis PyInstaller na primeira execução.

Se preferir uma pasta mais fácil de diagnosticar em vez de um arquivo único, retire `--onefile`; o aplicativo e seus componentes ficarão dentro de uma pasta em `dist`.

## Como o código está organizado (`main.py`)

1. **Constantes iniciais** (`LARGURA`, `ALTURA`, cores e `PONTOS_PARA_VENCER`): definem o tamanho lógico da tela, a paleta e a meta de pontos. São os valores mais simples de personalizar.
2. **`Sons`**: cria tons curtos diretamente na memória com ondas senoidais. Não carrega arquivos externos. Se não houver dispositivo de áudio, desativa os efeitos e mantém o jogo funcionando.
3. **`Raquete`**: guarda o retângulo, as teclas e a velocidade de uma raquete; `atualizar` lê as teclas e limita o movimento à tela; `desenhar` mostra a raquete.
4. **`Bola`**: guarda posição e velocidade. `atualizar` move a bola, rebate no teto/chão e nas raquetes e aumenta sua velocidade aos poucos. `_rebater` muda o ângulo conforme o ponto em que a bola acerta a raquete. `reiniciar` reposiciona a bola após um ponto.
5. **Funções de desenho**: `desenhar_texto` centraliza texto; `desenhar_botao` desenha os botões; `preparar_tela` escala a imagem para janela ou tela cheia; `desenhar_campo` pinta fundo, linha central e placar.
6. **`main()`**: inicializa o Pygame e controla o ciclo principal do jogo. Lê teclado/mouse, atualiza os objetos, verifica gols, troca entre menu/partida/vitória e redesenha a tela a cada quadro.
7. **Bloco final `if __name__ == "__main__"`**: chama `main()` quando o arquivo é executado diretamente.

### Ideias para personalização

- Mudar `PONTOS_PARA_VENCER` para outra quantidade.
- Alterar cores e tamanho das raquetes nas constantes/classes.
- Ajustar `velocidade_base`, `fator` ou o limite `760.0` na classe `Bola`.
- Alterar os textos do menu e as teclas indicadas na tela.

## Resumo para apresentar o projeto

O programa usa o ciclo principal do Pygame para ler eventos, atualizar a posição da bola e das raquetes e desenhar cada quadro. O tempo entre quadros (`dt`) faz com que os movimentos sejam proporcionais ao tempo, em vez de depender diretamente da velocidade do computador. As colisões são detectadas com retângulos (`pygame.Rect`), e o placar aumenta quando a bola sai pelas laterais. A velocidade cresce gradualmente para deixar as trocas mais desafiadoras.
