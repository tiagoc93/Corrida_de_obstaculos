import pygame, os, random, time
#import playsound

ob1 = 0
ob2 = 0
larguraJanela = 640
alturaJanela = 400

pygame.font.init()
fontePontuacao = pygame.font.SysFont('arial', 25, bold=True, italic=True)
#playsound.playsound('musicaFundo.mp3', block=False)

imagemPersonagem = [
    pygame.image.load(os.path.join('imagens', 'papainoel.png')),
    pygame.image.load(os.path.join('imagens', 'papainoelDeitado.png')),
]
imagemObstaculo = [
    pygame.image.load(os.path.join('imagens', 'obs1.png')),
    pygame.image.load(os.path.join('imagens', 'obs2.png'))
]
imagemChao = pygame.transform.scale2x(pygame.image.load(os.path.join('imagens', 'chao.png')))
imagemFundo = pygame.image.load(os.path.join('imagens', 'bg.png'))
imagemFundoPontos = pygame.image.load(os.path.join('imagens', 'fundoPontos.png'))

class Papainoel:
    imagens = imagemPersonagem
    noChao = False

    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy
        self.velocidadePersonagem = 0
        self.tempoJogo = 0
        self.imagem = self.imagens[0]

    def pular(self):
        #Para baixo -> positivo, para cima -> negativo
        if self.posy >= 240:
            self.velocidadePersonagem = -11
            self.tempoJogo = 0

    def movimento(self):
        self.tempoJogo += 1
        aceleracao = 3
        deslocamentoPersonagem = self.velocidadePersonagem * self.tempoJogo \
                                 + (aceleracao * (self.tempoJogo**2))/2

        if deslocamentoPersonagem > 11:
            deslocamentoPersonagem = 11
        elif deslocamentoPersonagem < 0:
            deslocamentoPersonagem -= 10

        self.posy += deslocamentoPersonagem

        if self.imagens.index(self.imagem) == 0:
            if self.posy > 240:
                self.posy = 240
                self.noChao = True
        elif self.imagens.index(self.imagem) == 1:
            if self.posy > 260:
                self.posy = 260
                self.noChao = True

    def desenhar_personagem(self, janela):
        centroImagem = self.imagem.get_rect(topleft=(self.posx, self.posy)).center
        envoltorio = self.imagem.get_rect(center = centroImagem)
        janela.blit(self.imagem, envoltorio.topleft)

    def superficie_personagem(self):
        return pygame.mask.from_surface(self.imagem)

class Obstaculo:
    velocidadeObstaculo = 10
    proxObstaculo = 0

    def __init__(self, posx):
        self.posx = posx
        self.alturaObstaculo = 0
        self.posicaoObstaculoBaixo = 0
        self.posicaoObstaculoAlto = 0
        self.obstaculoCima = pygame.transform.flip(imagemObstaculo[0], False, True)
        self.obstaculoBaixo = imagemObstaculo[1]
        self.passouObstaculo = False
        self.escolher_obstaculo()

    def escolher_obstaculo(self):
        global ob1, ob2
        self.proxObstaculo = random.randint(1, 2)
        if self.proxObstaculo == 1:
            ob2 = 0
            ob1 += 1
            if ob1 <= 3:
                self.alturaObstaculo = 260
                self.posicaoObstaculoBaixo = self.alturaObstaculo
            else:
                self.alturaObstaculo = 55
                self.posicaoObstaculoAlto = self.alturaObstaculo - self.obstaculoBaixo.get_height()
                self.proxObstaculo = 2
                ob2 += 1
                ob1 = 0
        elif self.proxObstaculo == 2:
            ob1 = 0
            ob2 += 1
            if ob2 <= 3:
                self.alturaObstaculo = 55
                self.posicaoObstaculoAlto = self.alturaObstaculo - self.obstaculoBaixo.get_height()
            else:
                self.alturaObstaculo = 260
                self.posicaoObstaculoBaixo = self.alturaObstaculo
                self.proxObstaculo = 1
                ob1 += 1
                ob2 = 0

    def movimento(self):
        self.posx -= self.velocidadeObstaculo

    def desenhar_obstaculo(self, janela):
        if self.proxObstaculo == 1:
            janela.blit(self.obstaculoBaixo, (self.posx, self.posicaoObstaculoBaixo))
        elif self.proxObstaculo == 2:
            janela.blit(self.obstaculoCima, (self.posx, self.posicaoObstaculoAlto))

    def testar_colisao(self, papaiNoel):
        papaiNoelSuperficie = papaiNoel.superficie_personagem()
        obstaculoBaixoSuperficie = pygame.mask.from_surface(self.obstaculoBaixo)
        obstaculoCimaSuperficie = pygame.mask.from_surface(self.obstaculoCima)

        testeColisao = False
        if self.proxObstaculo == 1:
            distanciaBaixo = (self.posx - papaiNoel.posx, self.posicaoObstaculoBaixo - round(papaiNoel.posy))
            testeColisao = papaiNoelSuperficie.overlap(obstaculoBaixoSuperficie, distanciaBaixo)

        if self.proxObstaculo == 2:
            distanciaCima = (self.posx - papaiNoel.posx, self.posicaoObstaculoAlto - round(papaiNoel.posy))
            testeColisao = papaiNoelSuperficie.overlap(obstaculoCimaSuperficie, distanciaCima)

        return testeColisao

class Chao:
    velocidadeChao = 10
    larguraChao = imagemChao.get_width()
    imagem = imagemChao

    def __init__(self, posy):
        self.posy = posy
        self.posxInicial = 0
        self.posxFinal = self.larguraChao

    def movimento(self):
        self.posxInicial -= self.velocidadeChao
        self.posxFinal -= self.velocidadeChao

        if self.posxInicial + self.larguraChao < 0:
            self.posxInicial = self.posxFinal + self.larguraChao
        if self.posxFinal + self.larguraChao < 0:
            self.posxFinal = self.posxInicial + self.larguraChao

    def desenhar_chao(self, janela):
        janela.blit(self.imagem, (self.posxInicial, self.posy))
        janela.blit(self.imagem, (self.posxFinal, self.posy))

def desenhar_janela(janela, noel, obstaculos, chao, pontos):
    janela.blit(imagemFundo, (0, -200))
    noel.desenhar_personagem(janela)
    for obstaculo in obstaculos:
        obstaculo.desenhar_obstaculo(janela)

    texto = fontePontuacao.render(f'Pontuação: {pontos}', True, (255, 255, 255))
    janela.blit(imagemFundoPontos, (larguraJanela - 10 - texto.get_width(), 10))
    janela.blit(texto, (larguraJanela - 10 - texto.get_width(), 10))
    chao.desenhar_chao(janela)
    pygame.display.update()

def main():
    noel = Papainoel(230, 200)
    chao = Chao(340)
    obstaculos = [Obstaculo(700)]
    janela = pygame.display.set_mode((larguraJanela, alturaJanela))
    pontos = 0
    relogio = pygame.time.Clock()
    vivo = True

    while vivo:
        relogio.tick(30)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                vivo = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE: # PULAR
                    noel.imagem = noel.imagens[0]
                    noel.pular()
            if evento.type == pygame.KEYDOWN: # ABAIXAR
                if evento.key == pygame.K_DOWN:
                    noel.imagem = noel.imagens[1]
            if evento.type == pygame.KEYUP: # LEVANTAR
                if evento.key == pygame.K_DOWN:
                    noel.imagem = noel.imagens[0]

        indice_obs = 0
        if vivo:
            if len(obstaculos) > 1 and noel.posx > (obstaculos[0].posx +
                                                    obstaculos[0].obstaculoBaixo.get_width()):
                indice_obs = 1

        noel.movimento()
        chao.movimento()

        novoObstaculo = False
        removerObstaculos = []
        for obstaculo in obstaculos:
            if obstaculo.testar_colisao(noel):
                vivo = False
                time.sleep(1)
                print(f'\n********** Pontuação: {pontos} **********')
            if not obstaculo.passouObstaculo and noel.posx > obstaculo.posx:
                obstaculo.passouObstaculo = True
                novoObstaculo = True
            obstaculo.movimento()
            if obstaculo.posx + obstaculo.obstaculoBaixo.get_width() < 0:
                removerObstaculos.append(obstaculo)

        if novoObstaculo:
            pontos += 1
            distProxObstaculo = 600 + 30 * pontos
            if distProxObstaculo < 960:
                obstaculos.append(Obstaculo(distProxObstaculo))
            else:
                obstaculos.append(Obstaculo(960))
        for obstaculo in removerObstaculos:
            obstaculos.remove(obstaculo)

        for obstaculo in obstaculos:
            if obstaculo.velocidadeObstaculo < 30:
                obstaculo.velocidadeObstaculo = 10 + round(pontos/3)
            else:
                obstaculo.velocidadeObstaculo = 30

            if chao.velocidadeChao < 30:
                chao.velocidadeChao = 10 + round(pontos/3)
            else:
                chao.velocidadeChao = 30

        desenhar_janela(janela, noel, obstaculos, chao, pontos)

if __name__ == '__main__':
    main()
