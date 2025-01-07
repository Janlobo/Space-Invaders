import pygame
import random
import time
import math
import numpy as np
# Bibliotecas usadas para gerar um executavel
import os
import sys

# Colocar esse codigo nos PNG e MP3 para funcionar no executavel
#def resource_path(relative_path):
#    try:
#        base_path = sys._MEIPASS
#    except Exception:
#        base_path = os.path.abspath(".")
#    return os.path.join(base_path, relative_path)
# Usar a função ao carregar recursos
#imagem = pygame.image.load(resource_path('nome_da_imagem.png'))
#som = pygame.mixer.Sound(resource_path('nome_do_som.mp3'))

# Inicialização do Pygame e do mixer
pygame.init()
pygame.mixer.init()

# Configurações da tela
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Space Invaders")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERDE = (0, 255, 0)
AMARELO = (255, 255, 0)
VERMELHO = (255, 0, 0)
CINZA_CLARO = (200, 200, 200)

# Canhão do jogador
class Canhao(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_original = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image_original, VERDE, [(0, 30), (40, 30), (30, 5), (10, 5)])
        pygame.draw.rect(self.image_original, BRANCO, (18, 0, 4, 5))
        self.image = self.image_original
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGURA // 2
        self.rect.bottom = ALTURA - 10
        self.velocidade = 5
        self.destruido = False
        self.tempo_destruicao = 0
        self.imagens_destruicao = [
            pygame.image.load(f"Explosao-canhao{i}.png").convert_alpha() for i in range(1, 5)
        ]
        self.indice_destruicao = 0
        self.tempo_explosao = 1.5  # Tempo total da explosão em segundos
        self.tempo_mensagem = 3  # Tempo para exibir a mensagem de vidas restantes

    def mover(self, direcao):
        if not self.destruido:
            if direcao == 'esquerda' and self.rect.left > 0:
                self.rect.x -= self.velocidade
            if direcao == 'direita' and self.rect.right < LARGURA:
                self.rect.x += self.velocidade

    def destruir(self):
        self.destruido = True
        self.tempo_destruicao = time.time()
        self.image = self.imagens_destruicao[0]  # Inicia com a primeira imagem de explosão

    def update(self):
        if self.destruido:
            tempo_atual = time.time()
            tempo_passado = tempo_atual - self.tempo_destruicao
            if tempo_passado > self.tempo_explosao:
                self.tempo_mensagem = tempo_atual
                self.destruido = False
                self.image = self.image_original
                self.rect.centerx = LARGURA // 2
                self.rect.bottom = ALTURA - 10
            else:
                indice = int(tempo_passado / (self.tempo_explosao / 4))  # 4 imagens
                if indice < 4 and indice != self.indice_destruicao:
                    self.indice_destruicao = indice
                    self.image = self.imagens_destruicao[indice]
        else:
            self.image = self.image_original  # Garante que a imagem original seja usada quando não destruído

# Alien
class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo):
        super().__init__()
        self.tipo = tipo
        if tipo == 1:
            self.image1 = pygame.image.load("Alien1.png").convert_alpha()
            self.image2 = pygame.image.load("Alien1.1.png").convert_alpha()
        elif tipo in [2, 3]:
            self.image1 = pygame.image.load("Alien2.png").convert_alpha()
            self.image2 = pygame.image.load("Alien2.2.png").convert_alpha()
        elif tipo in [4, 5]:
            self.image1 = pygame.image.load("Alien3-4.png").convert_alpha()
            self.image2 = pygame.image.load("Alien3-4.2.png").convert_alpha()
        self.image = self.image1
        self.alternador = True
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.destruido = False
        self.tempo_destruicao = 0
        self.imagem_destruicao1 = pygame.image.load("Alien-Destroyed.png").convert_alpha()
        self.imagem_destruicao2 = pygame.image.load("Alien-destroyed2.png").convert_alpha()

    def alternar_imagem(self):
        if not self.destruido:
            self.alternador = not self.alternador
            self.image = self.image1 if self.alternador else self.image2

    def destruir(self):
        self.destruido = True
        self.tempo_destruicao = time.time()
        self.image = self.imagem_destruicao1

    def update(self):
        if self.destruido:
            tempo_atual = time.time()
            if tempo_atual - self.tempo_destruicao > 0.35:
                self.kill()
            elif tempo_atual - self.tempo_destruicao > 0.175:
                self.image = self.imagem_destruicao2

# Tiro
class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(BRANCO)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.velocidade = -10

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.bottom < 0:
            self.kill()

# Nova classe para o tiro do alien
class TiroAlien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill((255, 165, 0))  # Cor laranja
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.velocidade = 5

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > ALTURA:
            self.kill()

# Grupos de sprites
todos_sprites = pygame.sprite.Group()
aliens = pygame.sprite.Group()
tiros = pygame.sprite.Group()
tiros_aliens = pygame.sprite.Group()

# Criação do canhão
canhao = Canhao()
todos_sprites.add(canhao)

# Criação dos aliens
for linha in range(5):
    for coluna in range(11):
        x = 50 + coluna * 50
        y = 50 + linha * 40
        if linha == 0:
            tipo = 1
        elif linha < 3:
            tipo = 2
        elif linha == 3:
            tipo = 4
        else:
            tipo = 5
        alien = Alien(x, y, tipo)
        todos_sprites.add(alien)
        aliens.add(alien)

# Variáveis do jogo
pontuacao = 0
vidas = 3
tempo_inicio = time.time()
direcao_aliens = 1
velocidade_inicial_aliens = 1
velocidade_aliens = velocidade_inicial_aliens
ultimo_movimento = time.time()
total_aliens_inicial = 55  # 5 linhas * 11 colunas
fator_aumento_velocidade = 1.5  # Aumenta o fator para um aumento mais rápido
aliens_destruidos = 0
tipos_aliens_atiradores = set([5])
fator_aumento_final = 1.4  # Aumento adicional de 40% para os últimos 2 aliens
fator_dobra_ultimo_alien = 20 # Aumento adicional 

# Definir um volume padrão para todos os sons
VOLUME_PADRAO = 0.5  # Valor entre 0.0 e 1.0

# Carregue os sons
som_explosao_alien = pygame.mixer.Sound("AlienExplosion.mp3")
som_explosao_alien.set_volume(VOLUME_PADRAO)
som_tiro_canhao = pygame.mixer.Sound("CanonShot.mp3")
som_tiro_canhao.set_volume(VOLUME_PADRAO * 0.2)
som_movimento_aliens = pygame.mixer.Sound("movimentoAliens.mp3")
som_movimento_aliens.set_volume(VOLUME_PADRAO * 0.6)
som_canhao_destruido = pygame.mixer.Sound("CanhaoDestruido.mp3")
som_canhao_destruido.set_volume(VOLUME_PADRAO)
som_aviso_nave_mae = pygame.mixer.Sound("MotherShipWarnning.mp3")
som_aviso_nave_mae.set_volume(VOLUME_PADRAO * 0.3)
som_explosao_nave_mae = pygame.mixer.Sound("MotherShipExplosion.mp3")
som_explosao_nave_mae.set_volume(VOLUME_PADRAO * 0.4)

# Se você estiver usando música de fundo
pygame.mixer.music.load("musica_fundo.mp3")
pygame.mixer.music.set_volume(VOLUME_PADRAO * 0.7)

# Carregue as imagens dos ícones de som
icone_som_on = pygame.image.load("IconFalanteON.png")
icone_som_off = pygame.image.load("IconFalanteOFF.png")
icone_som_on = pygame.transform.scale(icone_som_on, (30, 30))  # Ajuste o tamanho conforme necessário
icone_som_off = pygame.transform.scale(icone_som_off, (30, 30))  # Ajuste o tamanho conforme necessário

# Variável para controlar o estado do som
som_ativado = True

# Loop principal do jogo
rodando = True
clock = pygame.time.Clock()
fonte = pygame.font.Font(None, 36)
fonte_grande = pygame.font.Font(None, 42)
fonte_pequena = pygame.font.Font(None, 24)
mensagem_vidas = None
tempo_fim_mensagem = 0
tempo_pisca = 0
mostrar_vida = True

def reiniciar_jogo():
    global canhao, aliens, tiros, tiros_aliens, todos_sprites, pontuacao, vidas
    global tempo_inicio, tipos_aliens_atiradores, velocidade_aliens, aliens_destruidos
    global total_aliens_inicial, blocos_protecao, nave_mae, tempo_ultima_aparicao_nave_mae
    
    # Limpar todos os grupos de sprites
    todos_sprites.empty()
    aliens.empty()
    tiros.empty()
    tiros_aliens.empty()
    
    # Recriar o canhão
    canhao = Canhao()
    todos_sprites.add(canhao)
    
    # Recriar os aliens
    aliens = criar_aliens()
    todos_sprites.add(aliens)
    
    # Recriar os blocos de proteção
    blocos_protecao = criar_blocos_protecao()
    todos_sprites.add(blocos_protecao)
    
    # Resetar variáveis
    pontuacao = 0
    vidas = 3
    velocidade_aliens = velocidade_inicial_aliens
    tempo_inicio = time.time()
    tipos_aliens_atiradores = set([5])
    aliens_destruidos = 0
    nave_mae = None
    tempo_ultima_aparicao_nave_mae = 0
    
    # Parar sons
    canal_som_nave_mae.stop()
    pygame.mixer.music.play(-1)  # Reiniciar música de fundo

def criar_aliens():
    aliens = pygame.sprite.Group()
    for linha in range(5):
        for coluna in range(11):
            x = 50 + coluna * 50
            y = 50 + linha * 40
            if linha == 0:
                tipo = 1
            elif linha < 3:
                tipo = 2
            elif linha == 3:
                tipo = 4
            else:
                tipo = 5
            alien = Alien(x, y, tipo)
            aliens.add(alien)
    return aliens

def criar_blocos_protecao():
    blocos = pygame.sprite.Group()
    posicoes_x = [LARGURA * (i + 1) // 5 - 30 for i in range(4)]
    for x in posicoes_x:
        bloco = BlocoProtecao(x, ALTURA - 100)  # Ajuste o 100 conforme necessário
        blocos.add(bloco)
    return blocos

def aliens_atingiram_canhao(aliens, canhao):
    global vidas, rodando, canal_som_nave_mae

    for alien in aliens:
        if alien.rect.bottom >= canhao.rect.top:
            canhao.destruir()
            tocar_som(som_canhao_destruido)
            tempo_inicio_destruicao = time.time()
            
            # Renderizar a cena com o canhão destruído por 2 segundos
            while time.time() - tempo_inicio_destruicao < 2:
                tela.fill(PRETO)
                todos_sprites.draw(tela)
                pygame.display.flip()
                clock.tick(60)
            
            vidas = 0  # Zera as vidas para acionar o game over
            canal_som_nave_mae.stop()  # Para o som da nave-mãe
            
            # Pergunta se deseja continuar o jogo
            tela.fill(PRETO)
            texto_game_over = fonte.render("Game Over! Os aliens invadiram!", True, VERMELHO)
            texto_rect = texto_game_over.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
            tela.blit(texto_game_over, texto_rect)

            texto_jogar_novamente = fonte.render("Deseja jogar novamente? (S/N)", True, BRANCO)
            texto_rect = texto_jogar_novamente.get_rect(center=(LARGURA // 2, ALTURA // 2 + 50))
            tela.blit(texto_jogar_novamente, texto_rect)

            pygame.display.flip()

            esperando_resposta = True
            while esperando_resposta:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        rodando = False
                        esperando_resposta = False
                    elif evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_s:
                            mostrar_tela_inicial()
                            return False  # Retorna False para continuar o jogo
                        elif evento.key == pygame.K_n:
                            rodando = False
                            esperando_resposta = False
            
            return True  # Retorna True se o jogo deve terminar

    return False  # Retorna False se nenhum alien atingiu o canhão

def reiniciar_fase():
    global aliens, todos_sprites, tiros_aliens, pontuacao, velocidade_aliens
    todos_sprites.empty()
    aliens.empty()
    tiros_aliens.empty()
    
    criar_aliens()
    
    todos_sprites.add(canhao)
    velocidade_aliens = velocidade_inicial_aliens

# Função para tocar som
def tocar_som(som):
    if som_ativado:
        som.play()

# Classe para a NaveMae
class NaveMae(pygame.sprite.Sprite):
    def __init__(self, largura_tela):
        super().__init__()
        self.image1 = pygame.image.load("MotherShip1.png").convert_alpha()
        self.image2 = pygame.image.load("MotherShip2.png").convert_alpha()
        self.image = self.image1
        self.rect = self.image.get_rect()
        self.largura_tela = largura_tela
        self.velocidade = 2
        self.direcao = random.choice([-1, 1])  # -1 para esquerda, 1 para direita
        self.rect.y = 30  # Posição vertical fixa
        self.rect.x = -self.rect.width if self.direcao == 1 else self.largura_tela
        self.tempo_troca_imagem = 0
        self.tempo_inicio = time.time()
        self.duracao = random.uniform(7, 12)  # Duração aleatória entre 7 e 12 segundos
        self.destruida = False
        self.explosao_imagens = [pygame.image.load(f"Explosao-canhao{i}.png").convert_alpha() for i in range(1, 5)]
        self.explosao_index = 0
        self.tempo_ultima_explosao = 0
        self.atirando = False
        self.tempo_inicio_tiro = 0
        self.duracao_tiro = 3  # Duração do tiro em segundos
        self.tiros_ativos = pygame.sprite.Group()  # Novo grupo para controlar os tiros ativos

    def update(self):
        global nave_mae  # Declare nave_mae como global
        
        if self.destruida:
            agora = pygame.time.get_ticks()
            if agora - self.tempo_ultima_explosao > 100:  # Troca a imagem a cada 100ms
                self.explosao_index += 1
                if self.explosao_index >= len(self.explosao_imagens):
                    self.kill()  # Remove a NaveMae do jogo
                    nave_mae = None  # Define nave_mae como None
                    canal_som_nave_mae.stop()
                else:
                    self.image = self.explosao_imagens[self.explosao_index]
                    self.tempo_ultima_explosao = agora
        else:
            tempo_atual = time.time()
            if tempo_atual - self.tempo_inicio > self.duracao:
                self.parar_tiros()  # Novo método para parar os tiros
                canal_som_nave_mae.stop()
                self.kill()
                nave_mae = None  # Define nave_mae como None
                return

            if self.atirando:
                if tempo_atual - self.tempo_inicio_tiro > self.duracao_tiro:
                    self.atirando = False
            else:
                self.rect.x += self.velocidade * self.direcao
                
                # Troca de imagem a cada 0.5 segundos
                if tempo_atual - self.tempo_troca_imagem > 0.5:
                    self.image = self.image2 if self.image == self.image1 else self.image1
                    self.tempo_troca_imagem = tempo_atual

                # Inverte a direção se atingir as bordas da tela
                if (self.direcao == 1 and self.rect.right > self.largura_tela) or \
                   (self.direcao == -1 and self.rect.left < 0):
                    self.direcao *= -1

        # Verifica se saiu da tela
        if self.rect.right < 0 or self.rect.left > self.largura_tela:
            self.parar_tiros()
            canal_som_nave_mae.stop()
            self.kill()
            nave_mae = None  # Define nave_mae como None

    def iniciar_tiro(self):
        if not self.atirando:
            self.atirando = True
            self.tempo_inicio_tiro = time.time()

    def destruir(self):
        self.destruida = True
        canal_som_nave_mae.stop()
        tocar_som(som_explosao_nave_mae)
        self.explosao_index = 0
        self.tempo_ultima_explosao = pygame.time.get_ticks()

    def parar_tiros(self):
        for tiro in self.tiros_ativos:
            tiro.kill()
        self.tiros_ativos.empty()

# No código principal, adicione:
nave_mae = None
canal_som_nave_mae = pygame.mixer.Channel(0)  # Use o canal 0 para o som da NaveMae
ultimo_tiro_nave_mae = 0
tempo_ultima_aparicao_nave_mae = 0
tempo_minimo_entre_navemaes = 30  # segundos

# Adicione esta nova classe após as outras classes
class BlocoProtecao(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.largura = 60
        self.altura = 50
        self.image = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mascara = np.zeros((self.altura, self.largura), dtype=int)
        self.cor = (255, 165, 0)  # Laranja
        self.desenhar()

    def desenhar(self):
        self.image.fill((0, 0, 0, 0))
        for y in range(self.altura):
            for x in range(self.largura):
                if self.mascara[y, x] < 3:
                    if y < 10:  # Arredondar as arestas superiores
                        if (x < 10 and (x-10)**2 + (y-10)**2 > 100) or \
                           (x >= self.largura-10 and (x-(self.largura-11))**2 + (y-10)**2 > 100):
                            continue
                    if y > self.altura - 15 and self.largura//2 - 10 < x < self.largura//2 + 10:
                        continue  # Criar o espaço em forma de trapézio na parte inferior
                    cor = [max(0, c - 50 * self.mascara[y, x]) for c in self.cor]
                    self.image.set_at((x, y), cor)

    def colide_com_ponto(self, x, y):
        x_rel = int(x - self.rect.x)
        y_rel = int(y - self.rect.y)
        if 0 <= x_rel < self.largura and 0 <= y_rel < self.altura:
            return self.mascara[y_rel, x_rel] < 3
        return False

    def dano(self, x, y, direcao):
        x_rel = int(x - self.rect.x)
        y_rel = int(y - self.rect.y)
        
        passo = 1 if direcao > 0 else -1
        
        while 0 <= y_rel < self.altura:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x_rel + dx, y_rel + dy
                    if 0 <= nx < self.largura and 0 <= ny < self.altura:
                        if dx*dx + dy*dy <= 2:  # Pequeno círculo
                            self.mascara[ny, nx] = min(3, self.mascara[ny, nx] + 1)
            
            y_rel += passo

        self.desenhar()

        # Verifique se o bloco está completamente destruído
        if np.all(self.mascara >= 3):
            self.kill()  # Remove o bloco se estiver completamente destruído

# No código principal, após a criação dos aliens:

# Criação dos blocos de proteção
blocos_protecao = criar_blocos_protecao()
todos_sprites.add(blocos_protecao)

# No loop principal do jogo, substitua a lógica de colisão por:

# Colisões com os blocos de proteção
for bloco in blocos_protecao:
    # Colisão com tiros dos aliens
    for tiro in tiros_aliens:
        if bloco.rect.collidepoint(tiro.rect.center):
            if bloco.colide_com_ponto(tiro.rect.centerx, tiro.rect.centery):
                bloco.dano(tiro.rect.centerx, tiro.rect.centery, 1)  # 1 para direção para baixo
                tiro.kill()
    
    # Colisão com tiros do canhão
    for tiro in tiros:
        if bloco.rect.collidepoint(tiro.rect.center):
            if bloco.colide_com_ponto(tiro.rect.centerx, tiro.rect.centery):
                bloco.dano(tiro.rect.centerx, tiro.rect.centery, -1)  # -1 para direção para cima
                tiro.kill()
    
    # Colisão com tiros da nave mãe (se existir)
    if nave_mae and nave_mae.tiros_ativos:
        for tiro in nave_mae.tiros_ativos:
            if bloco.rect.collidepoint(tiro.rect.center):
                if bloco.colide_com_ponto(tiro.rect.centerx, tiro.rect.centery):
                    bloco.dano(tiro.rect.centerx, tiro.rect.centery, 1)  # 1 para direção para baixo
                    tiro.kill()

# ... (resto do código existente) ...

def mostrar_tela_inicial():
    tela.fill(PRETO)  

    pygame.mixer.music.play(-1, fade_ms=3000)  # Fade in de 3 segundos

    # Fonte grande para "SPACE INVADERS"
    fonte_grande = pygame.font.Font(None, 72)
    texto_titulo = fonte_grande.render("SPACE INVADERS", True, (0, 0, 255))  # Azul
    rect_titulo = texto_titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
    tela.blit(texto_titulo, rect_titulo)
    
    # Fonte menor para as instruções
    fonte_pequena = pygame.font.Font(None, 36)
    texto_som = fonte_pequena.render("CTRL + S = retira o som.", True, BRANCO)
    rect_som = texto_som.get_rect(center=(LARGURA // 2, rect_titulo.bottom + 50))
    tela.blit(texto_som, rect_som)
    texto_movimento = fonte_pequena.render("Movimento: Setas < >", True, BRANCO)
    rect_movimento = texto_movimento.get_rect(center=(LARGURA // 2, rect_som.bottom + 30))
    tela.blit(texto_movimento, rect_movimento)
    texto_tiro = fonte_pequena.render("Atirar: Barra de espaço", True, BRANCO)
    rect_tiro = texto_tiro.get_rect(center=(LARGURA // 2, rect_movimento.bottom + 30))
    tela.blit(texto_tiro, rect_tiro)
    
    # Instrução para iniciar o jogo
    texto_iniciar = fonte_pequena.render("Pressione qualquer tecla para iniciar", True, VERDE)
    rect_iniciar = texto_iniciar.get_rect(center=(LARGURA // 2, rect_tiro.bottom + 50))
    tela.blit(texto_iniciar, rect_iniciar)
  
    pygame.display.flip()
    
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False  # Sair do jogo
            if evento.type == pygame.KEYDOWN:
                return True  # Iniciar o jogo

    return False  # Caso o loop seja interrompido de alguma forma

# No código principal, antes do loop principal do jogo
if mostrar_tela_inicial():
    # Iniciar o jogo
    rodando = True
    # ... resto do código para iniciar o jogo ...
else:
    rodando = False

# Loop principal do jogo
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                if len(tiros) == 0:
                    tiro = Tiro(canhao.rect.centerx, canhao.rect.top)
                    todos_sprites.add(tiro)
                    tiros.add(tiro)
                    tocar_som(som_tiro_canhao)
            elif evento.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                som_ativado = not som_ativado
                if not som_ativado:
                    pygame.mixer.stop()
                    canal_som_nave_mae.stop()

    # Movimento do canhão
    if not canhao.destruido:
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            canhao.mover('esquerda')
        if teclas[pygame.K_RIGHT]:
            canhao.mover('direita')

    # Atualização
    todos_sprites.update()

    # Movimento dos aliens
    agora = time.time()
    if agora - ultimo_movimento > (velocidade_inicial_aliens / velocidade_aliens):
        mover_para_baixo = False
        for alien in aliens:
            alien.rect.x += 10 * direcao_aliens
            alien.alternar_imagem()
            if alien.rect.right > LARGURA or alien.rect.left < 0:
                mover_para_baixo = True
        
        tocar_som(som_movimento_aliens)
        
        if mover_para_baixo:
            for alien in aliens:
                alien.rect.y += 5
            direcao_aliens *= -1
        ultimo_movimento = agora

    # Atualização da velocidade dos aliens
    aliens_restantes = len(aliens)
    if aliens_restantes > 0:
        progresso = 1 - (aliens_restantes / total_aliens_inicial)
        fator = math.exp(progresso * 2) - 1  # Função exponencial para aumento mais rápido
        velocidade_aliens = velocidade_inicial_aliens * (1 + fator * fator_aumento_velocidade)
        
        # Aumento adicional para os últimos 2 aliens
        if aliens_restantes == 2:
            velocidade_aliens *= fator_aumento_final

        if aliens_restantes <= 1:
            velocidade_aliens = fator_aumento_final * fator_dobra_ultimo_alien

    # Lógica para os tiros dos aliens
    if random.randint(1, 100) == 1:  # 1% de chance de atirar a cada frame
        if len(tiros_aliens) < 2:
            aliens_atiradores = []
            for tipo in sorted(tipos_aliens_atiradores, reverse=True):
                aliens_atiradores.extend([alien for alien in aliens if alien.tipo == tipo])
            
            if aliens_atiradores:
                alien_atirador = random.choice(aliens_atiradores)
                tiro_alien = TiroAlien(alien_atirador.rect.centerx, alien_atirador.rect.bottom)
                todos_sprites.add(tiro_alien)
                tiros_aliens.add(tiro_alien)

    # Atualização dos tiros dos aliens
    tiros_aliens.update()

    # Colisões
    for tiro in tiros:
        aliens_atingidos = pygame.sprite.spritecollide(tiro, aliens, False)
        for alien in aliens_atingidos:
            if not alien.destruido:
                pontuacao += 5 if alien.tipo == 1 else (3 if alien.tipo == 2 else 1)
                alien.destruir()
                tiro.kill()
                
                tocar_som(som_explosao_alien)
                
                aliens_destruidos += 1
                
                # Atualizamos a velocidade após cada destruição
                aliens_restantes = len(aliens)
                if aliens_restantes > 0:
                    progresso = 1 - (aliens_restantes / total_aliens_inicial)
                    fator = math.exp(progresso * 2) - 1
                    velocidade_aliens = velocidade_inicial_aliens * (1 + fator * fator_aumento_velocidade)
                    
                    # Aumento adicional para os últimos 2 aliens
                    if aliens_restantes == 2:
                        velocidade_aliens *= fator_aumento_final
                
                    # Aumento adicional para o último alien
                    if aliens_restantes <= 1:
                        velocidade_aliens = velocidade_aliens * fator_dobra_ultimo_alien
                
                # Se um alien do tipo 5 foi destruído, adiciona o tipo 4 aos atiradores
                if alien.tipo == 5 and 4 not in tipos_aliens_atiradores:
                    tipos_aliens_atiradores.add(4)
                # Se um alien do tipo 4 foi destruído, adiciona o tipo 3 aos atiradores
                elif alien.tipo == 4 and 3 not in tipos_aliens_atiradores:
                    tipos_aliens_atiradores.add(3)
                # Se um alien do tipo 3 foi destruído, adiciona o tipo 2 aos atiradores
                elif alien.tipo == 3 and 2 not in tipos_aliens_atiradores:
                    tipos_aliens_atiradores.add(2)
                # Se um alien do tipo 2 foi destruído, adiciona o tipo 1 aos atiradores
                elif alien.tipo == 2 and 1 not in tipos_aliens_atiradores:
                    tipos_aliens_atiradores.add(1)

    # Colisão dos tiros dos aliens com o canhão
    if not canhao.destruido and pygame.sprite.spritecollide(canhao, tiros_aliens, True):
        vidas -= 1
        canhao.destruir()
        tocar_som(som_canhao_destruido)
        if vidas <= 0:
            tela.fill(PRETO)
            texto_game_over = fonte.render("Game Over! A Terra foi invadida.", True, VERMELHO)
            texto_rect = texto_game_over.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
            tela.blit(texto_game_over, texto_rect)

            texto_jogar_novamente = fonte.render("Deseja jogar novamente? (S/N)", True, BRANCO)
            texto_rect = texto_jogar_novamente.get_rect(center=(LARGURA // 2, ALTURA // 2 + 50))
            tela.blit(texto_jogar_novamente, texto_rect)

            pygame.display.flip()

            esperando_resposta = True
            while esperando_resposta:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        rodando = False
                        esperando_resposta = False
                    elif evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_s:
                            reiniciar_jogo()
                            esperando_resposta = False
                        elif evento.key == pygame.K_n:
                            rodando = False
                            esperando_resposta = False
            else:
                mensagem_vidas = f"Você tem {vidas} vidas restantes."
                tempo_fim_mensagem = time.time() + 2  # 2 segundos para exibir a mensagem

    # Remova os aliens destruídos do grupo de aliens, mas mantenha-os em todos_sprites
    aliens = pygame.sprite.Group([alien for alien in aliens if not alien.destruido])

    # Atualização do tempo de pisca
    tempo_atual = time.time()
    if tempo_atual - tempo_pisca > 0.5:  # Pisca a cada 0.5 segundos
        tempo_pisca = tempo_atual
        mostrar_vida = not mostrar_vida

    # Lógica para a NaveMae
    if nave_mae is None:
        tempo_atual = time.time()
        if (tempo_atual - tempo_ultima_aparicao_nave_mae > tempo_minimo_entre_navemaes and
            random.randint(1, 1000) == 1):  # 0.1% de chance de aparecer a cada frame
            nave_mae = NaveMae(LARGURA)
            todos_sprites.add(nave_mae)
            tempo_ultima_aparicao_nave_mae = tempo_atual
            # Tocar o som de aviso quando a NaveMae aparecer
            if som_ativado:
                canal_som_nave_mae.play(som_aviso_nave_mae, loops=-1)

    if nave_mae and not nave_mae.destruida:
        if not nave_mae.atirando and random.randint(1, 500) == 1:
            nave_mae.iniciar_tiro()

        if nave_mae.atirando:
            agora = time.time()
            if agora - nave_mae.tempo_inicio_tiro <= nave_mae.duracao_tiro:
                if agora - ultimo_tiro_nave_mae > 0.1:  # Tiro a cada 0.1 segundos
                    tiro_nave_mae = TiroAlien(nave_mae.rect.centerx, nave_mae.rect.bottom)
                    todos_sprites.add(tiro_nave_mae)
                    tiros_aliens.add(tiro_nave_mae)
                    nave_mae.tiros_ativos.add(tiro_nave_mae)  # Adiciona o tiro ao grupo de tiros ativos da NaveMae
                    ultimo_tiro_nave_mae = agora

        # Colisão dos tiros com a NaveMae
        tiros_colididos = pygame.sprite.spritecollide(nave_mae, tiros, True)
        if tiros_colididos:
            pontuacao += 20
            nave_mae.destruir()

    # Verificar se a NaveMae saiu da tela ou foi destruída
    if nave_mae is not None:
        if nave_mae.rect.right < 0 or nave_mae.rect.left > LARGURA:
            nave_mae.parar_tiros()
            nave_mae.kill()
            nave_mae = None
            canal_som_nave_mae.stop()
        elif nave_mae.destruida and nave_mae.explosao_index >= len(nave_mae.explosao_imagens):
            nave_mae.kill()
            nave_mae = None
            canal_som_nave_mae.stop()

    # Colisão dos tiros da NaveMae com o canhão
    if nave_mae and not nave_mae.destruida:
        if not canhao.destruido and pygame.sprite.spritecollide(canhao, tiros_aliens, True):
            vidas -= 1
            canhao.destruir()
            tocar_som(som_canhao_destruido)
            if vidas <= 0:
                tela.fill(PRETO)
                texto_game_over = fonte.render("Game Over! A Terra foi invadida.", True, VERMELHO)
                texto_rect = texto_game_over.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
                tela.blit(texto_game_over, texto_rect)

                texto_jogar_novamente = fonte.render("Deseja jogar novamente? (S/N)", True, BRANCO)
                texto_rect = texto_jogar_novamente.get_rect(center=(LARGURA // 2, ALTURA // 2 + 50))
                tela.blit(texto_jogar_novamente, texto_rect)

                pygame.display.flip()

                esperando_resposta = True
                while esperando_resposta:
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            rodando = False
                            esperando_resposta = False
                        elif evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_s:
                                reiniciar_jogo()
                                esperando_resposta = False
                            elif evento.key == pygame.K_n:
                                rodando = False
                                esperando_resposta = False
            else:
                mensagem_vidas = f"Você tem {vidas} vidas restantes."
                tempo_fim_mensagem = time.time() + 2  # 2 segundos para exibir a mensagem

    # Verificar se todos os aliens foram destruídos
    if len(aliens) == 0:
        tela.fill(PRETO)
        texto_vitoria = fonte.render("Parabéns! Você destruiu todas as naves", True, VERDE)
        texto_vitoria2 = fonte.render("e evitou a invasão neste momento.", True, VERDE)
        texto_rect = texto_vitoria.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
        texto_rect2 = texto_vitoria2.get_rect(center=(LARGURA // 2, ALTURA // 2))
        tela.blit(texto_vitoria, texto_rect)
        tela.blit(texto_vitoria2, texto_rect2)

        texto_continuar = fonte.render("Deseja prosseguir? (S/N)", True, BRANCO)
        texto_rect_continuar = texto_continuar.get_rect(center=(LARGURA // 2, ALTURA // 2 + 50))
        tela.blit(texto_continuar, texto_rect_continuar)

        pygame.display.flip()

        esperando_resposta = True
        while esperando_resposta:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                    esperando_resposta = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_s:
                        reiniciar_jogo()
                        esperando_resposta = False
                    elif evento.key == pygame.K_n:
                        rodando = False
                        esperando_resposta = False

    # Colisões com os blocos de proteção
    for bloco in blocos_protecao:
        # Colisão com tiros dos aliens
        for tiro in tiros_aliens:
            if bloco.rect.collidepoint(tiro.rect.center):
                if bloco.colide_com_ponto(tiro.rect.centerx, tiro.rect.centery):
                    bloco.dano(tiro.rect.centerx, tiro.rect.centery, 1)  # 1 para direção para baixo
                    tiro.kill()
        
        # Colisão com tiros do canhão
        for tiro in tiros:
            if bloco.rect.collidepoint(tiro.rect.center):
                if bloco.colide_com_ponto(tiro.rect.centerx, tiro.rect.centery):
                    bloco.dano(tiro.rect.centerx, tiro.rect.centery, -1)  # -1 para direção para cima
                    tiro.kill()
        
        # Colisão com tiros da nave mãe (se existir)
        if nave_mae and nave_mae.tiros_ativos:
            for tiro in nave_mae.tiros_ativos:
                if bloco.rect.collidepoint(tiro.rect.center):
                    if bloco.colide_com_ponto(tiro.rect.centerx, tiro.rect.centery):
                        bloco.dano(tiro.rect.centerx, tiro.rect.centery, 1)  # 1 para direção para baixo
                        tiro.kill()

    # Verificar se os aliens atingiram o nível do canhão
    if aliens_atingiram_canhao(aliens, canhao):
        break  # Sai do loop principal se o jogo deve terminar

    # Atualização de todos os sprites
    todos_sprites.update()

    # Desenho
    tela.fill(PRETO)
    todos_sprites.draw(tela)
    tiros_aliens.draw(tela)

    # Preparar textos
    texto_pontuacao = fonte_pequena.render(f"Pontos: {pontuacao}", True, BRANCO)
    texto_tempo = fonte_pequena.render(f"Tempo: {int(time.time() - tempo_inicio)}s", True, BRANCO)
    velocidade_relativa = velocidade_aliens / velocidade_inicial_aliens
    texto_velocidade = fonte_pequena.render(f"Vel: {velocidade_relativa:.2f}x", True, CINZA_CLARO)
    cor_vida = AMARELO if vidas == 1 else BRANCO
    texto_vidas = fonte_pequena.render(f"Vidas: {vidas}", True, cor_vida)

    # Calcular posições
    espaco = 20  # Espaço entre os textos
    largura_total = (texto_pontuacao.get_width() + texto_tempo.get_width() + 
                     texto_velocidade.get_width() + texto_vidas.get_width() + 3 * espaco)
    x_inicial = (LARGURA - largura_total) // 2

    # Exibir informações
    tela.blit(texto_pontuacao, (x_inicial, 10))
    x_inicial += texto_pontuacao.get_width() + espaco
    tela.blit(texto_tempo, (x_inicial, 10))
    x_inicial += texto_tempo.get_width() + espaco
    tela.blit(texto_velocidade, (x_inicial, 10))
    x_inicial += texto_velocidade.get_width() + espaco
    
    if vidas > 1 or mostrar_vida:
        tela.blit(texto_vidas, (x_inicial, 10))

    # Exibir mensagem de vidas restantes
    if mensagem_vidas and time.time() < tempo_fim_mensagem:
        texto_vidas = fonte.render(mensagem_vidas, True, BRANCO)
        texto_rect = texto_vidas.get_rect(center=(LARGURA // 2, ALTURA // 2))
        tela.blit(texto_vidas, texto_rect)
    elif time.time() >= tempo_fim_mensagem:
        mensagem_vidas = None

    # Exibir ícone de som
    icone_som = icone_som_on if som_ativado else icone_som_off
    tela.blit(icone_som, (LARGURA - 40, 10))  # Posiciona o ícone no canto superior direito

    # Obter o tempo atual
    tempo_atual = time.time()

    # Preparar os textos
    texto_tempo_atual = fonte_pequena.render(f"Tempo atual: {tempo_atual:.2f}", True, BRANCO)
    texto_ultima_aparicao = fonte_pequena.render(f"Última aparição: {tempo_ultima_aparicao_nave_mae:.2f}", True, BRANCO)
    texto_diferenca = fonte_pequena.render(f"Diferença: {tempo_atual - tempo_ultima_aparicao_nave_mae:.2f}", True, BRANCO)

    # Preparar o texto para o valor de nave_mae
    if nave_mae is None:
        texto_nave_mae = fonte_pequena.render("Nave Mãe: None", True, BRANCO)
    else:
        texto_nave_mae = fonte_pequena.render(f"Nave Mãe: Presente (x: {nave_mae.rect.x})", True, BRANCO)

    # Posicionar e desenhar os textos
 #   tela.blit(texto_tempo_atual, (10, ALTURA - 120))
 #   tela.blit(texto_ultima_aparicao, (10, ALTURA - 90))
 #    tela.blit(texto_diferenca, (10, ALTURA - 60))
 #   tela.blit(texto_nave_mae, (10, ALTURA - 30))

    pygame.display.flip()
    clock.tick(60)

# Finalização
pygame.quit()