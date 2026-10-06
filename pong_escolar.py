"""Pong escolar para dois jogadores — feito com Python e Pygame.

Controles durante a partida:
    Jogador 1: W / S
    Jogador 2: seta para cima / seta para baixo

Menu: mouse ou Enter/Espaço. F11 alterna tela cheia; Esc volta ao menu/sai.
"""

import math
import struct
import sys

import pygame 

# Resolução virtual do jogo. Em tela cheia, a imagem é ajustada para a tela
# mantendo a proporção (podem aparecer faixas pretas nas laterais ou em cima).
LARGURA = 960
ALTURA = 540
FPS = 60
PONTOS_PARA_VENCER = 10

# Paleta simples, inspirada em jogos retrô (cores originais, sem copiar arte).
PRETO = (10, 14, 18)
BRANCO = (235, 242, 232)
VERDE = (100, 230, 160)
CINZA = (115, 130, 132)


class Sons:
    """Gera bipes simples em memória. Não precisa de arquivos de áudio."""

    def __init__(self):
        self.ativos = False
        self.batida = None
        self.ponto = None
        try:
            # Som mono, 16 bits. A falha do dispositivo de áudio não impede o jogo.
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.batida = self._criar_tom(660, 0.055)
            self.ponto = self._criar_tom(330, 0.18)
            self.ativos = True
        except pygame.error:
            print("Aviso: áudio indisponível; o jogo continuará sem efeitos sonoros.")

    @staticmethod
    def _criar_tom(frequencia, duracao):
        taxa = 22050
        total = int(taxa * duracao)
        amostras = bytearray()
        for i in range(total):
            # Envelope descendente para o som terminar suavemente.
            envelope = 1.0 - (i / total)
            valor = int(9000 * envelope * math.sin(2 * math.pi * frequencia * i / taxa))
            amostras.extend(struct.pack("<h", valor))
        return pygame.mixer.Sound(buffer=bytes(amostras))

    def tocar_batida(self):
        if self.ativos:
            self.batida.play()

    def tocar_ponto(self):
        if self.ativos:
            self.ponto.play()


class Raquete:
    """Raquete vertical que pode ser controlada por um jogador."""

    def __init__(self, x, teclas):
        self.largura = 14
        self.altura = 92
        self.rect = pygame.Rect(x, ALTURA // 2 - self.altura // 2,
                                self.largura, self.altura)
        self.tecla_cima, self.tecla_baixo = teclas
        self.velocidade = 430  # pixels por segundo

    def atualizar(self, teclas_pressionadas, dt):
        movimento = 0
        if teclas_pressionadas[self.tecla_cima]:
            movimento -= 1
        if teclas_pressionadas[self.tecla_baixo]:
            movimento += 1
        self.rect.y += int(movimento * self.velocidade * dt)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(ALTURA, self.rect.bottom)

    def desenhar(self, tela):
        pygame.draw.rect(tela, BRANCO, self.rect, border_radius=3)


class Bola:
    """Bola com velocidade crescente durante as trocas e ao longo da partida."""

    def __init__(self):
        self.tamanho = 14
        self.rect = pygame.Rect(0, 0, self.tamanho, self.tamanho)
        self.velocidade_base = 340.0
        self.velocidade = self.velocidade_base
        self.vx = self.velocidade_base
        self.vy = 100.0
        self.tempo_aceleracao = 0.0
        self.reiniciar(direcao=1)

    def reiniciar(self, direcao=None):
        self.rect.center = (LARGURA // 2, ALTURA // 2)
        self.velocidade = self.velocidade_base
        if direcao is None:
            direcao = 1 if pygame.time.get_ticks() % 2 == 0 else -1
        self.vx = self.velocidade * direcao
        self.vy = self.velocidade * 0.30
        self.tempo_aceleracao = 0.0

    def atualizar(self, dt, raquete_esquerda, raquete_direita, sons):
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)

        # Quica no teto e no chão.
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy = abs(self.vy)
            sons.tocar_batida()
        elif self.rect.bottom >= ALTURA:
            self.rect.bottom = ALTURA
            self.vy = -abs(self.vy)
            sons.tocar_batida()

        # Quica nas raquetes apenas quando está indo em direção a elas.
        if self.vx < 0 and self.rect.colliderect(raquete_esquerda.rect):
            self.rect.left = raquete_esquerda.rect.right
            self._rebater(raquete_esquerda)
            sons.tocar_batida()
        elif self.vx > 0 and self.rect.colliderect(raquete_direita.rect):
            self.rect.right = raquete_direita.rect.left
            self._rebater(raquete_direita)
            sons.tocar_batida()

        # Aceleração suave e contínua, limitada para manter a partida jogável.
        self.tempo_aceleracao += dt
        if self.tempo_aceleracao >= 1.0:
            self.tempo_aceleracao -= 1.0
            fator = 1.025
            nova_velocidade = min(math.hypot(self.vx, self.vy) * fator, 760.0)
            angulo = math.atan2(self.vy, self.vx)
            self.vx = math.cos(angulo) * nova_velocidade
            self.vy = math.sin(angulo) * nova_velocidade

    def _rebater(self, raquete):
        # O ponto de contato altera o ângulo: acertar perto das pontas
        # manda a bola mais para cima ou para baixo.
        diferenca = self.rect.centery - raquete.rect.centery
        proporcao = diferenca / (raquete.altura / 2)
        angulo = proporcao * math.radians(55)
        direcao = 1 if self.vx < 0 else -1
        velocidade = min(math.hypot(self.vx, self.vy) * 1.06, 760.0)
        self.vx = math.cos(angulo) * velocidade * direcao
        self.vy = math.sin(angulo) * velocidade

    def desenhar(self, tela):
        pygame.draw.rect(tela, VERDE, self.rect)


def desenhar_texto(tela, fonte, texto, cor, centro):
    """Desenha uma linha de texto centralizada no ponto indicado."""
    imagem = fonte.render(texto, True, cor)
    retangulo = imagem.get_rect(center=centro)
    tela.blit(imagem, retangulo)
    return retangulo


def desenhar_botao(tela, fonte, texto, caixa, mouse_pos, pressionado=False):
    """Desenha um botão simples e retorna sua área clicável."""
    sobre = caixa.collidepoint(mouse_pos)
    cor = VERDE if sobre else BRANCO
    pygame.draw.rect(tela, cor, caixa, width=2, border_radius=6)
    rotulo = fonte.render(texto, True, cor)
    tela.blit(rotulo, rotulo.get_rect(center=caixa.center))
    return caixa


def preparar_tela(janela, superficie, tamanho_janela):
    """Escala a tela virtual para caber na janela sem deformar o jogo."""
    largura, altura = tamanho_janela
    escala = min(largura / LARGURA, altura / ALTURA)
    destino = (int(LARGURA * escala), int(ALTURA * escala))
    imagem = pygame.transform.scale(superficie, destino)
    janela.fill((0, 0, 0))
    janela.blit(imagem, ((largura - destino[0]) // 2,
                         (altura - destino[1]) // 2))
    pygame.display.flip()


def desenhar_campo(tela, fonte_placar, pontos):
    """Desenha o fundo, a linha central e os dois placares."""
    tela.fill(PRETO)
    for y in range(12, ALTURA, 28):
        pygame.draw.rect(tela, CINZA, (LARGURA // 2 - 2, y, 4, 15))
    desenhar_texto(tela, fonte_placar, str(pontos[0]), BRANCO,
                   (LARGURA // 2 - 72, 55))
    desenhar_texto(tela, fonte_placar, str(pontos[1]), BRANCO,
                   (LARGURA // 2 + 72, 55))


def main():
    pygame.init()
    pygame.display.set_caption("PONG — Dois jogadores")
    janela = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
    superficie = pygame.Surface((LARGURA, ALTURA))
    relogio = pygame.time.Clock()
    sons = Sons()

    fonte_titulo = pygame.font.Font(None, 100)
    fonte_grande = pygame.font.Font(None, 58)
    fonte_media = pygame.font.Font(None, 34)
    fonte_pequena = pygame.font.Font(None, 25)

    raquete_esquerda = Raquete(42, (pygame.K_w, pygame.K_s))
    raquete_direita = Raquete(LARGURA - 42 - 14,
                              (pygame.K_UP, pygame.K_DOWN))
    bola = Bola()
    pontos = [0, 0]
    estado = "menu"  # estados possíveis: menu, jogo, vitoria
    vencedor = 0
    tela_cheia = False
    tamanho_janela = (LARGURA, ALTURA)
    executando = True
    # Áreas dos botões existem desde o início, inclusive antes do primeiro desenho.
    botao_iniciar = pygame.Rect(LARGURA // 2 - 130, 275, 260, 62)
    botao_reiniciar = pygame.Rect(LARGURA // 2 - 145, 310, 290, 58)
    botao_sair = pygame.Rect(LARGURA // 2 - 145, 385, 290, 58)

    while executando:
        dt = min(relogio.tick(FPS) / 1000.0, 0.04)
        mouse_pos = pygame.mouse.get_pos()
        # Converte coordenadas do mouse para a tela virtual usada pelo menu.
        if tela_cheia:
            largura_atual, altura_atual = janela.get_size()
            escala_atual = min(largura_atual / LARGURA, altura_atual / ALTURA)
            origem_x = (largura_atual - LARGURA * escala_atual) / 2
            origem_y = (altura_atual - ALTURA * escala_atual) / 2
            mouse_virtual = ((mouse_pos[0] - origem_x) / escala_atual,
                             (mouse_pos[1] - origem_y) / escala_atual)
        else:
            largura_atual, altura_atual = tamanho_janela
            escala_atual = min(largura_atual / LARGURA, altura_atual / ALTURA)
            origem_x = (largura_atual - LARGURA * escala_atual) / 2
            origem_y = (altura_atual - ALTURA * escala_atual) / 2
            mouse_virtual = ((mouse_pos[0] - origem_x) / escala_atual,
                             (mouse_pos[1] - origem_y) / escala_atual)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False
            elif evento.type == pygame.VIDEORESIZE and not tela_cheia:
                tamanho_janela = (max(480, evento.w), max(300, evento.h))
                janela = pygame.display.set_mode(tamanho_janela, pygame.RESIZABLE)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    tela_cheia = not tela_cheia
                    if tela_cheia:
                        janela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        janela = pygame.display.set_mode(tamanho_janela, pygame.RESIZABLE)
                elif evento.key == pygame.K_ESCAPE:
                    if estado == "jogo":
                        estado = "menu"
                    else:
                        executando = False
                elif estado == "menu" and evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    pontos = [0, 0]
                    bola.reiniciar()
                    estado = "jogo"
                elif estado == "vitoria" and evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    pontos = [0, 0]
                    bola.reiniciar()
                    estado = "jogo"
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # O mouse é consultado somente nos menus/tela de vitória;
                # não controla raquetes durante a partida.
                if estado == "menu" and botao_iniciar.collidepoint(mouse_virtual):
                    pontos = [0, 0]
                    bola.reiniciar()
                    estado = "jogo"
                elif estado == "vitoria":
                    if botao_reiniciar.collidepoint(mouse_virtual):
                        pontos = [0, 0]
                        bola.reiniciar()
                        estado = "jogo"
                    elif botao_sair.collidepoint(mouse_virtual):
                        executando = False

        if estado == "jogo":
            teclas = pygame.key.get_pressed()
            raquete_esquerda.atualizar(teclas, dt)
            raquete_direita.atualizar(teclas, dt)
            bola.atualizar(dt, raquete_esquerda, raquete_direita, sons)

            if bola.rect.right < 0:
                pontos[1] += 1
                sons.tocar_ponto()
                if pontos[1] >= PONTOS_PARA_VENCER:
                    vencedor = 2
                    estado = "vitoria"
                else:
                    bola.reiniciar(direcao=-1)
            elif bola.rect.left > LARGURA:
                pontos[0] += 1
                sons.tocar_ponto()
                if pontos[0] >= PONTOS_PARA_VENCER:
                    vencedor = 1
                    estado = "vitoria"
                else:
                    bola.reiniciar(direcao=1)

        desenhar_campo(superficie, fonte_grande, pontos)
        if estado == "jogo":
            raquete_esquerda.desenhar(superficie)
            raquete_direita.desenhar(superficie)
            bola.desenhar(superficie)
            desenhar_texto(superficie, fonte_pequena, "W / S", CINZA,
                           (75, ALTURA - 24))
            desenhar_texto(superficie, fonte_pequena, "↑ / ↓", CINZA,
                           (LARGURA - 75, ALTURA - 24))
        elif estado == "menu":
            desenhar_texto(superficie, fonte_titulo, "PONG", VERDE,
                           (LARGURA // 2, 155))
            desenhar_texto(superficie, fonte_media, "DOIS JOGADORES • UM TECLADO",
                           BRANCO, (LARGURA // 2, 225))
            desenhar_botao(superficie, fonte_media, "INICIAR", botao_iniciar,
                           mouse_virtual)
            desenhar_texto(superficie, fonte_pequena,
                           "Clique ou pressione Enter / Espaço", CINZA,
                           (LARGURA // 2, 370))
            desenhar_texto(superficie, fonte_pequena,
                           "P1: W / S     P2: ↑ / ↓", BRANCO,
                           (LARGURA // 2, 425))
            desenhar_texto(superficie, fonte_pequena,
                           "F11: tela cheia     Esc: sair", CINZA,
                           (LARGURA // 2, 465))
        else:  # tela de vitória
            desenhar_texto(superficie, fonte_titulo, f"JOGADOR {vencedor} VENCEU!",
                           VERDE, (LARGURA // 2, 175))
            desenhar_texto(superficie, fonte_media, f"PLACAR  {pontos[0]}  —  {pontos[1]}",
                           BRANCO, (LARGURA // 2, 250))
            desenhar_botao(superficie, fonte_media, "JOGAR NOVAMENTE",
                           botao_reiniciar, mouse_virtual)
            desenhar_botao(superficie, fonte_media, "SAIR",
                           botao_sair, mouse_virtual)
            desenhar_texto(superficie, fonte_pequena,
                           "Enter / Espaço para jogar novamente", CINZA,
                           (LARGURA // 2, 475))

        preparar_tela(janela, superficie, janela.get_size())

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
