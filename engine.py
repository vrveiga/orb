import pygame
import numpy as np

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

        self.rect = None

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

        self.ticks = 0

        self.quit_event_triggered = False

    def add_object(self, object: Object):
        self.objects.append(object)

    def step(self):
        modified_rects = []

        def coordinate_to_pygame(x):
            return (x + [1/2, 3/2] * self.surface_size) % self.surface_size

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

            new_coords = coordinate_to_pygame(object.x)

            old_rect = object.rect
            modified_rects.append(old_rect)
            
            if old_rect:
                pygame.draw.circle(self.surface, self.BACKGROUND_COLOR, object.rect.center, object.radius)

            object.rect = pygame.draw.circle(self.surface, self.FOREGROUND_COLOR, new_coords, object.radius)
            modified_rects.append(object.rect)

            if old_rect and object.trail:
                if self.ticks % self.TRAIL_PERIOD == 0:
                    v_unit = object.v / np.linalg.norm(object.v)
                    trail_coords = [object.rect.centerx - 1 - 5 * v_unit[0], object.rect.centery - 1 - 5 * v_unit[1], 1, 1]
                    trail_rect = pygame.draw.rect(self.surface, self.FOREGROUND_COLOR, trail_coords)
                    modified_rects.append(trail_rect)

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
            if event.type == pygame.QUIT:
                self.quit_event_triggered = True
                break

    @property
    def done(self) -> bool:
        return self.quit_event_triggered
