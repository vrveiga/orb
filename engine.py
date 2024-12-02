import pygame
import numpy as np

from collections import deque

from typing import Callable

class Object:
    def __init__(self, mass: float, radius: int, trail: bool):
        self.mass = mass
        self.radius = radius
        self.trail = trail

        self.forces: list[Callable] = []

        self.x = np.array([0] * 2)
        self.v = np.array([0] * 2)
        self.a = np.array([0] * 2)

        self.rect: pygame.Rect = None

    def add_force(self, force: Callable):
        self.forces.append(force)

class TextUpdater:
    def __init__(self, update: Callable[[], str], position: np.array):
        self.update = update
        self.position = position

class Engine:
    BACKGROUND_COLOR = [20] * 3
    FOREGROUND_COLOR = [255] * 3

    DELTA = 1e-5

    TRAIL_PERIOD = 30
    N_MAX_TRAILS = 50
    
    def __init__(self, surface: pygame.Surface, font: pygame.font.Font):
        self.surface = surface
        self.font = font

        # Assumimos que o tamanho da tela não irá mudar
        self.surface_size = np.array(surface.get_size())

        self.surface.fill(self.BACKGROUND_COLOR)
        pygame.display.update()
    
        self.clock = pygame.time.Clock()

        self.objects: list[Object] = []
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
        self.objects.append(object)

    def step(self):
        modified_rects = []

        # Verifica se um objeto de raio `radius` com coordenadas `x` no sistema de coordenadas canônico precisa ser exibido
        def should_be_displayed(x, radius):
            viewport_coords = self.viewport_scale * (x - self.viewport_center)
            w_half, h_half = self.surface_size / 2

            if -w_half - radius <= viewport_coords[0] <= w_half + radius:
                if -h_half - radius <= viewport_coords[1] <= h_half + radius:
                    return True

            return False

        # Converte do sistema de coordenadas canônico para o sistema de coordenadas do
        # viewport, para então converter para o sistema de coordenadas do pygame
        def coordinate_to_pygame(x, radius):
            return self.pygame_coord_factor * (self.viewport_scale * (x - self.viewport_center) + [1/2, -1/2] * self.surface_size)

        if self.paused:
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
            self.surface.fill(self.BACKGROUND_COLOR)

            for trail_coord, v_unit in self.trails.items():
                if not should_be_displayed(trail_coord, 1):
                    continue

                new_coords = coordinate_to_pygame(trail_coord - 4 / self.viewport_scale * v_unit, 1)
                
                pygame.draw.rect(self.surface, self.FOREGROUND_COLOR, [*new_coords, 1, 1])

            for object in self.objects:
                if not should_be_displayed(object.x, object.radius):
                    continue

                new_coords = coordinate_to_pygame(object.x, object.radius)
                
                if object.rect:
                    object.rect = pygame.draw.circle(self.surface, self.FOREGROUND_COLOR, new_coords, max(2, self.viewport_scale * object.radius))

            for updater in self.text_updaters:
                text = updater.update()
                rendered_text = self.font.render(text, False, self.FOREGROUND_COLOR, self.BACKGROUND_COLOR)
                rendered_rect = self.surface.blit(rendered_text, updater.position)
                
            self.redraw = False
            self.clock.tick(60)

            pygame.display.update()
            
            return

        trail_coords = list(self.trails.keys())

        for object in self.objects:
            if object.forces:
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
                    self.trails.pop(first_trail_coord)

                    trail_rect = pygame.draw.rect(self.surface, self.BACKGROUND_COLOR, [*coordinate_to_pygame(first_trail_coord, 1), 1, 1])
                    modified_rects.append(trail_rect)

                v_unit = object.v / np.linalg.norm(object.v)

                trail_coord = object.x - (object.radius + 2) * v_unit

                if should_be_displayed(trail_coord, 1):
                    trail_rect = pygame.draw.rect(self.surface, self.FOREGROUND_COLOR, [*coordinate_to_pygame(trail_coord - 4 / self.viewport_scale * v_unit, 1), 1, 1])

                    modified_rects.append(trail_rect)

                self.trails[tuple(trail_coord)] = v_unit

            # Desenhar o objeto na nova posição
            if should_be_displayed(object.x, object.radius):
                new_coords = coordinate_to_pygame(object.x, object.radius)

                old_rect = object.rect
                modified_rects.append(old_rect)
            
                if old_rect:
                    pygame.draw.circle(self.surface, self.BACKGROUND_COLOR, object.rect.center, max(2, self.viewport_scale * object.radius))

                object.rect = pygame.draw.circle(self.surface, self.FOREGROUND_COLOR, new_coords, max(2, self.viewport_scale * object.radius))
                modified_rects.append(object.rect)

            # Remove rastros que devem ser "apagados" (algum objeto já desenhou por cima deles)
            for trail_coord in trail_coords[:-1]:
                if np.linalg.norm(object.x - trail_coord) <= object.radius:
                    self.trails.pop(trail_coord, None)
                            
        for updater in self.text_updaters:
            text = updater.update()
            rendered_text = self.font.render(text, False, self.FOREGROUND_COLOR, self.BACKGROUND_COLOR)
            rendered_rect = self.surface.blit(rendered_text, updater.position)

            modified_rects.append(rendered_rect)

        pygame.display.update(modified_rects)
        self.clock.tick(60)

        self.ticks += 1

    def add_text_with_updater(self, update: Callable[[], str], position: np.array):
        self.text_updaters.append(TextUpdater(update, position))

    def process_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.quit_event_triggered = True
                    break
                case pygame.MOUSEBUTTONDOWN if event.button == 1:
                    self.dragging = True
                    self.drag_start = np.array(event.pos)

                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
                case pygame.MOUSEMOTION if self.dragging:
                    self.viewport_center = self.viewport_center + 1 / self.viewport_scale * self.pygame_coord_factor * (self.drag_start - event.pos)
                    self.redraw = True

                    self.drag_start = np.array(event.pos)

                case pygame.MOUSEBUTTONUP if event.button == 1:
                    self.dragging = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                case pygame.KEYDOWN if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_MINUS:
                     if self.viewport_scale > 0.2:
                         self.viewport_scale /= 1.2
                         self.redraw = True
                case pygame.KEYDOWN if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_EQUALS:
                    if self.viewport_scale < 8:
                        self.viewport_scale *= 1.2
                        self.redraw = True
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
                case pygame.KEYDOWN if event.key == pygame.K_r:
                    self.reset_event_triggered = True

    @property
    def done(self) -> bool:
        return self.quit_event_triggered or self.reset_event_triggered
