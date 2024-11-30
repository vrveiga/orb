import pygame
import numpy as np

from typing import Callable, Self

class Object:
    def __init__(self, mass: float, radius: int, trail: bool):
        self.mass = mass
        self.radius = radius
        self.trail = trail

        self.forces: list[Callable] = []

        self.r = np.array([0] * 2)
        self.v = np.array([0] * 2)
        self.a = np.array([0] * 2)

        self.rect = None

    def add_force(self, force: Callable):
        self.forces.append(force)
        
class Engine:
    WINDOW_SIZE = np.array([800, 600])
    
    BACKGROUND_COLOR = [20] * 3
    FOREGROUND_COLOR = [255] * 3

    DELTA = 0.01

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        self.screen.fill(self.BACKGROUND_COLOR)
    
        self.clock = pygame.time.Clock()

        self.objects = []

        self.quit_event_triggered = False

    def add_object(self, object: Object):
        self.objects.append(object)

    def step(self):
        modified_rects = []

        def coordinate_to_pygame(x):
            return (x + [1/2, 3/2] * self.WINDOW_SIZE) % self.WINDOW_SIZE

        for object in self.objects:
            if object.forces:
                # Aproximação usando o algoritmo velocity-verlet
                v_prime = object.v + 1/2 * object.a * self.DELTA
                new_r = object.r + v_prime * self.DELTA
                F = sum(f(object.r) for f in object.forces)
                new_a = F / object.mass
                new_v = v_prime + 1/2 * new_a * self.DELTA

                object.r = new_r
                object.v = new_v
                object.a = new_a

            new_coords = coordinate_to_pygame(object.r)

            if object.rect:
                pygame.draw.rect(self.screen, self.BACKGROUND_COLOR, object.rect)
                
            modified_rects.append(object.rect)
            object.rect = pygame.draw.circle(self.screen, self.FOREGROUND_COLOR, new_coords, object.radius)
            modified_rects.append(object.rect)

        pygame.display.update(modified_rects)
        self.clock.tick(60)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_event_triggered = True
                break

    @property
    def done(self) -> bool:
        return self.quit_event_triggered
    
def main():
    engine = Engine()

    G = 500

    m_star = 1e4
    m_planet = 10

    star = Object(m_star, 30, trail=False)
    planet = Object(m_planet, 5, trail=True)

    planet.r = np.array([110, 100])
    planet.v = np.array([100, -90])

    planet.add_force(lambda r: -G * m_star * m_planet * r / np.linalg.norm(r) ** 3)

    engine.add_object(star)
    engine.add_object(planet)

    while not engine.done:
        engine.step()
        engine.process_events()

if __name__ == "__main__":
    main()
