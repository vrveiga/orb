"""
Nome do Projeto: Simulador de gravitacao Newtoniana

    Descrição: O projeto desenvolvido visa simular a orbita de um planeta entorno de sua estrela. Tal projeto, permite o usuário manipular o peso da estrela e do planeta. Além disso, permite a mudança das componentes no eixo x e y da velociadade do planeta. Para incrementar a análise do movimento, foi disponibilizado os valores da energia potencial, cinética e mecânica, os quais são atualizados no decorrer da simulação quando necessário.

    Autores: 
    Marcelo Martins Conti - NUSP: 15474629
    Vitor Rocha Veiga - NUSP: 15492449
    Matheus Muzza Pires Ferreira - NUSP: 15479468
    João Gabriel Araújo de Bastos - NUSP: 1546263
    Felipe Camargo Cerri  - NUSP: 15451119
    João Pedro Monteiro Machado Junqueira Castelli - NUSP: 15463450

    Este projeto faz parte do processo avaliativo da disciplina 7600105 - Física Básica I (2024) da USP-São Carlos ministrada pela(o) [Prof. Krissia de Zawadzki/Esmerindo de Sousa Bernardes]
"""

import pygame
import numpy as np

from typing import Callable

class Object:
    """
    Classe que representa a estrela e o planeta estarão formando o sistema de órbita. 
    Entradas: 
        mass(tipo float)-> massa do corpo
        radius(tipo int) -> tamanho do raio do corpo
        trail(tipo bool) -> Indica se queremos ou não rastro visível do deslocamento do corpo
    """
    def __init__(self, mass: float, radius: int, trail: bool):
        """
        Inicializa os atributos das instãncias, as quais são:
           mass(float)-> massa,
           radius(int)-> raio,
           trail(bool)-> rastro,
           forces(list)-> lista de forças que atuam(inicializado com um array de funções),
           x,v,a(array) -> são respectivamente posição, velocidade e aceleração do corpo. São inicializados com um array de tamanho 2.Com todas as posições sendo 0.
        """
        self.mass = mass
        self.radius = radius
        self.trail = trail

        self.forces: list[Callable] = []

        self.x = np.array([0] * 2)
        self.v = np.array([0] * 2)
        self.a = np.array([0] * 2)

        self.rect: pygame.Rect = None

    def add_force(self, force: Callable):
        """
        Método de adiciona forças ao vetor de forças do objeto
        Entrada: 
            force(funtion)-> função que será adicionada no vetor de forças
        """
        self.forces.append(force)

class TextUpdater:
    """
    Classe que armazena uma função e a posição do texto que deve aparecer na tela. Chamamos ela para atualizarmos os valores que são apresentados na tela.
    Entrada:
        update()-> função que precisamos receber e que nos retornará o texto novo a ser mostrado,
        position()-> posição em que o texto deve aparecer na tela
    """
    def __init__(self, update: Callable[[], str], position: np.array):
        self.update = update
        self.position = position

class Engine:
    """
    Engine: É a classe responsável por controlar a taxa de quadros, configuração da tela da simulação, 
    simulação do movimento do planeta em torno da estrela. 
    A renderização de textos, rastros do movimento também são de responsabilidade da Engine. 
    Nos auxilia no processo de iteratividade, permitindo pausas, movimentação do viewport e zoom.
    """
    BACKGROUND_COLOR = [20] * 3
    FOREGROUND_COLOR = [255] * 3

    DELTA = 1e-5

    TRAIL_PERIOD = 30
    N_MAX_TRAILS = 50
    
    def __init__(self, surface: pygame.Surface, font: pygame.font.Font):
        """
        Entradas:
            surface(object) -> superfície que serão feitas as simulações (receberá o pygame.Surface)
            font(pygame module)-> Recebe a fonte que será utilizada nos textos
        Inicialização de certas instâncias:
            clock-> cria um clock do pygame que permite gerenciar a taxa de atualização
            objects-> lista de objetos que irão participar da simulação
            text_updaters->lista vazia para armazenar os objetos do textUpdater
            pygame_coord_factor-> array com 1 e -1 de elementos, para mudar o fator de coordenadas da simulação para as coordenadas do pygame.
            trails->é usado para gerenciar as posições e características dos rastros que aparecem na tela. É um dicionário que armazena as posições(tuple) e o vetor unitário que indica a direção do movimento quando o ponto foi criado(np.array)
            ticks-> contador de ticks do sistema. Será incrementado a cada interação. Mede o número de ciclos ou passos da simulação.
            drag_start-> array de 2 posições(x,y). Guarda a posição inicial do cursor quando o usuário começa a arrastar o viewport
        """
        self.surface = surface
        self.font = font

        # Assumimos que o tamanho da tela não irá mudar
        self.surface_size = np.array(surface.get_size())

        self.surface.fill(self.BACKGROUND_COLOR) # preenche a tela com a cor definida
        pygame.display.update()
    
        self.clock = pygame.time.Clock()

        self.objects: list[Object] = [] # lista de objetos que vão participar da simulação
        self.text_updaters: list[TextUpdater] = []

        self.pygame_coord_factor = np.array([1, -1])

        # Guarda as coordenadas de cada rastro, no sistema de coordenadas canônico, como chave
        # O valor corresponde ao versor velocidade do objeto que criou o rastro. Dessa forma,
        # o rastro pode ter sua escala ajustada de acordo com a escala do viewport
        self.trails: dict[tuple, np.array] = {}
        
        self.ticks = 0

        # Guarda a origem do sistema de coordenadas do viewport, no sistema de coordenadas canônico
        self.viewport_center = np.array([0] * 2)
        self.viewport_scale = 1

        self.drag_start = np.array([0] * 2)

        self.paused = False

        self.redraw = False
        self.dragging = False
        self.quit_event_triggered = False
        self.reset_event_triggered = False

    def reset(self):
        self.objects.clear()  # Remove os objetos
        self.trails.clear()   # Limpa os rastros
        self.text_updaters.clear()  # Limpa os textos dinâmicos
        self.viewport_center = np.array([0, 0])  # Reseta o centro do viewport
        self.viewport_scale = 1  # Reseta o zoom
        self.reset_event_triggered = False  # Garante que o evento de reset seja desmarcado
        self.redraw = True

    def add_object(self, object: Object):
        """
        Método que armazena os objetos que serão simulados pela Engine.
        Entrada: 
            object-> recebe um objeto que simula um corpo como uma estrela ou um planeta que segue as características do Object.
        """
        self.objects.append(object)

    def step(self):
        """ Será responsável por:
        Atualização da física dos objetos.
        Renderização dos objetos na tela.
        Controle dos rastros dos objetos.
        Atualização de elementos de texto dinâmico.
        Redesenho otimizado das áreas alteradas.
        """
        modified_rects = [] # array que armazena os retângulos que foram alterados na tela. É usada para renderizar apenas o necessário

        def should_be_displayed(x, radius):
            """
            Verifica se um objeto de raio `radius` com coordenadas `x` no sistema de coordenadas canônico está dentro do campo de visão e precisa ser mostrado na tela.
                Entradas:
                    x(array)->array com posição (x,y) do objeto
                    radius(int) -> raio do objeto 

                Saída:
                    retorna true se precisa ser renderizado
                    retorna false se não precisa ser renderizado
            """
            viewport_coords = self.viewport_scale * (x - self.viewport_center)
            w_half, h_half = self.surface_size / 2

            if -w_half - radius <= viewport_coords[0] <= w_half + radius:
                if -h_half - radius <= viewport_coords[1] <= h_half + radius:
                    return True

            return False

        def coordinate_to_pygame(x, radius):
            """
            Converte do sistema de coordenadas canônico para o sistema de coordenadas do viewport. Após isso, o converte para o sistema de coordenadas do pygame.
            Entradas: 
                x(array)-> array com as coordenadas (x,y) do sistema canônico
                radius(int)-> Raio do objeto
            Saída:
                array-> Coordenadas convertidas para o pygame
            """
            return self.pygame_coord_factor * (self.viewport_scale * (x - self.viewport_center) + [1/2, -1/2] * self.surface_size)

        if self.paused:
            """Quando a simulação está pausado ele limita o loop para no máximo 60 interações por segundo;"""

            self.clock.tick(60)
            return

        # Se precisarmos redesenhar tudo, apenas redesenhamos, pulando a física
        # (deixando-a para o próximo timestep). O intuito por trás disso é que 
        # redesenhar tudo geralmente é uma tarefa custosa e, além disso, essa
        # função é usada para implementar arrasto do viewport. Seria estranho
        # se a física continuasse rodando enquanto arrastamos o viewport.
        #
        # Na forma que estamos usando isso não causa problema, no entanto, 
        # poderia gerar um deadlock se usado de forma inadequada.
        if self.redraw:
            """Responsável por redesenhar a tela quando necessário, ocorre após eventos que alteram a visualização como arrastar o viewport. 
            Ela limpa a tela preenchendo com a cor de fundo e depois redesenha os elementos.
            """
            self.surface.fill(self.BACKGROUND_COLOR)

            for trail_coord, v_unit in self.trails.items():
                """ Itera sobre todos os traços armazenados em trails e se ele não estiver na área de visualização ele ignora o rastro. 
                Se ele estiver na área de visualização ele desloca o rastro para sua nova posição, de acordo com a mudança do viewports""" 

                if not should_be_displayed(trail_coord, 1):
                    continue

                new_coords = coordinate_to_pygame(trail_coord - 4 / self.viewport_scale * v_unit, 1)
                
                pygame.draw.rect(self.surface, self.FOREGROUND_COLOR, [*new_coords, 3, 3])
                
            """ Itera sobre todos os objetos,se não tiver no campo de visão ele passa ser realizar ações. 
            Se estiver no campo de visão realizamos certas mudanças no sistema de coordenadas para ir para o sistema de coordeadas do pygame, 
            redesenhando ao final o objeto e redimensionando seu tamanho se necessário
            """
            for object in self.objects:
                if not should_be_displayed(object.x, object.radius):
                    continue

                new_coords = coordinate_to_pygame(object.x, object.radius)
                
                if object.rect:
                    object.rect = pygame.draw.circle(self.surface, self.FOREGROUND_COLOR, new_coords, max(2, self.viewport_scale * object.radius))
                    
            # Parte que renderiza os textos dinamicamente na tela.
            for updater in self.text_updaters:
                text = updater.update()
                rendered_text = self.font.render(text, False, self.FOREGROUND_COLOR, self.BACKGROUND_COLOR)
                rendered_rect = self.surface.blit(rendered_text, updater.position)
                
            self.redraw = False
            self.clock.tick(60)

            pygame.display.update()
            
            return

        # isto gera uma lista de tuplas que guardam as coordenadas dos ultimos pontos de trail
        trail_coords = list(self.trails.keys())

        # em cada step, a engine ira atualizar todos os objetos na seguinte parte:
        for object in self.objects:
            # se o objeto esta sob a ação de forças, atualizaremos sua nova posição, velocidade e aceleração.
            if object.forces:
                # o delta é pequeno (como deveria ser para obter uma boa derivada), então fazemos o calculo 1000 vezes para
                # traçar uma diferença de tempo significativa a cada passo.
                for i in range(1000):
                    # Aproximação usando o algoritmo velocity-verlet
                    v_prime = object.v + 1/2 * object.a * self.DELTA
                    new_x = object.x + v_prime * self.DELTA
                    F = sum(f(object.x) for f in object.forces)
                    new_a = F / object.mass
                    new_v = v_prime + 1/2 * new_a * self.DELTA

                    object.x = new_x
                    object.v = new_v
                    object.a = new_a

            # Verificar se devemos desenhar mais um componente do rastro
            if object.trail and self.ticks % self.TRAIL_PERIOD == 0:
                # Remove o primeiro componente do rastro a ser desenhado quando chegamos ao limite
                if len(self.trails) == self.N_MAX_TRAILS:
                    first_trail_coord = next(iter(self.trails))
                    # pegamos o trail mais velho e retiramos ele do dict trails.
                    self.trails.pop(first_trail_coord)
                    # aqui, desenhamos a cor de background por cima do ponto que deve ser apagado
                    trail_rect = pygame.draw.rect(self.surface, self.BACKGROUND_COLOR, [*coordinate_to_pygame(first_trail_coord, 1), 3, 3])
                    modified_rects.append(trail_rect)

                v_unit = object.v / np.linalg.norm(object.v) #versor velocidade

                # lembrando que radius é o raio do proprio objeto (tamanho display dele), a coord do ponto deve ser um pouco antes do
                # planeta em si para não ser apagado pela renderização do proprio planeta
                trail_coord = object.x - (object.radius + 2) * v_unit

                if should_be_displayed(trail_coord, 1):
                    trail_rect = pygame.draw.rect(self.surface, self.FOREGROUND_COLOR, [*coordinate_to_pygame(trail_coord - 4 / self.viewport_scale * v_unit, 1), 3, 3])

                    modified_rects.append(trail_rect)

                self.trails[tuple(trail_coord)] = v_unit

            # Desenhar o objeto na nova posição
            if should_be_displayed(object.x, object.radius):
                new_coords = coordinate_to_pygame(object.x, object.radius)

                old_rect = object.rect
                modified_rects.append(old_rect)
                # caso a bolinha já foi desenhada antes, ou seja, nao eh o primeiro frame, desenhar a bolinha antiga com a cor de fundo
                if old_rect:
                    pygame.draw.circle(self.surface, self.BACKGROUND_COLOR, object.rect.center, max(2, self.viewport_scale * object.radius))
                # agora desenha a nova posicao da bolinha (planeta) com a cor de destaque
                object.rect = pygame.draw.circle(self.surface, self.FOREGROUND_COLOR, new_coords, max(2, self.viewport_scale * object.radius))
                modified_rects.append(object.rect)

            # Remove rastros que devem ser "apagados" (algum objeto já desenhou por cima deles)
            for trail_coord in trail_coords[:-1]:
                if np.linalg.norm(object.x - trail_coord) <= object.radius:
                    self.trails.pop(trail_coord, None)
                            
        #simples atualização dos textos das energias
        for updater in self.text_updaters:
            text = updater.update()
            rendered_text = self.font.render(text, False, self.FOREGROUND_COLOR, self.BACKGROUND_COLOR)
            rendered_rect = self.surface.blit(rendered_text, updater.position)

            modified_rects.append(rendered_rect)
        #as novas renderizações dos trails, planeta e texto das energias foram append no modified_rects
        #e agora são atualizados no display do pygame
        pygame.display.update(modified_rects)
        # limitar o programa a 60 frames por segundo
        self.clock.tick(60)
        # contador de atualizações da renderização
        self.ticks += 1

    """ 
    entradas: update: uma função que apenas devolve o texto a ser colocado na tela durante a simulacao: energia e instruções
              position: array com dois inteiros que representam as coordenadas onde serao renderizados os textos
              o objetivo desta função é adicionar um objeto TextUpdater a lista text_updaters da engine, e esses atualizadores de texto
              irao colocar as novas energias do sistema na tela durante a simulacao.
    """
    def add_text_with_updater(self, update: Callable[[], str], position: np.array):
        self.text_updaters.append(TextUpdater(update, position))

    """
    entradas: apenas a propria engine
    comportamentos: esta função detecta eventos do pygame e reaje de acordo:
    cliques e arrastos do mouse, teclas do teclado sendo pressianadas
    """
    def process_events(self):
        for event in pygame.event.get():
            match event.type:
                # Saida: coloca true para o evento de fechamento do jogo
                case pygame.QUIT:
                    self.quit_event_triggered = True
                    break
                # o mouse esquerdo foi ativado: ativa o evento de arrasto do mouse
                case pygame.MOUSEBUTTONDOWN if event.button == 1:
                    self.dragging = True
                    self.drag_start = np.array(event.pos)

                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
                # o mouse esta sendo arrastado: a tela deve ser redesenhado e o sistema de coordenadas transladado
                case pygame.MOUSEMOTION if self.dragging:
                    self.viewport_center = self.viewport_center + 1 / self.viewport_scale * self.pygame_coord_factor * (self.drag_start - event.pos)
                    self.redraw = True

                    self.drag_start = np.array(event.pos)

                # se o mouse esquerdo foi liberado: nao esta mais sendo arrastado
                case pygame.MOUSEBUTTONUP if event.button == 1:
                    self.dragging = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                # pressionou ctrl+ -: eh dado zoom out
                case pygame.KEYDOWN if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_MINUS:
                     if self.viewport_scale > 0.2:
                         self.viewport_scale /= 1.2
                         self.redraw = True

                # pressionado ctrl+ +: eh dado zoom in
                case pygame.KEYDOWN if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_EQUALS:
                    if self.viewport_scale < 8:
                        self.viewport_scale *= 1.2
                        self.redraw = True

                # pressionada a tecla ESC: pausa e despausa
                case pygame.KEYDOWN if event.key == pygame.K_ESCAPE:
                    if self.paused:
                        self.redraw = True
                        self.paused = False
                    else:
                        self.paused = True

                        darken_overlay = pygame.Surface(self.surface.get_size())
                        darken_overlay.fill(self.BACKGROUND_COLOR)
                        darken_overlay.set_alpha(180)

                        self.surface.blit(darken_overlay, (0, 0))
                        pygame.display.update()

                # pressionada a tecla r: deve ser dado reset na simulacao, entao o evento de reset eh colocado como true
                case pygame.KEYDOWN if event.key == pygame.K_r:
                    self.reset_event_triggered = True

    #este arroba transforma a funcao done em uma propriedade, ou seja, como se fosse uma variavel booleana do objeto
    @property
    #retorna se a simulacao deve ser finalizada (como true ou false
    def done(self) -> bool:
        return self.quit_event_triggered or self.reset_event_triggered
