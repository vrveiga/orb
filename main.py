import pygame
import sys
import numpy as np

from engine import Engine, Object
        
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('firebrick4')
        self.color_active = pygame.Color('firebrick1')
        self.color = self.color_inactive
        self.text = text
        self.font = pygame.font.Font("assets/VCR_OSD_MONO.ttf", 26)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Se o usuário clicou no input box
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            
            # Muda a cor do input box
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_DELETE:
                    self.text = self.text[1:]
                elif event.unicode.isprintable():
                    self.text += event.unicode
        
    def update(self):
        # Faz o resize do box
        width = max(150, self.font.render(self.text, True, self.color).get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Renderiza o texto do input box
        txt_surface = self.font.render(self.text, True, self.color)
        screen.blit(txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Sandbox:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('orb')
        
        # Configurações padrão
        self.massa_estrela = 5e16
        self.massa_planeta = 100
        self.posicao_planeta = [110, 100]
        self.velocidade_planeta = [100, -90]
        
        # Criar input boxes
        self.input_massa_estrela = InputBox(450, 100, 200, 32, str(self.massa_estrela))
        self.input_massa_planeta = InputBox(450, 200, 200, 32, str(self.massa_planeta))
        self.input_pos_x = InputBox(450, 300, 150, 32, str(self.posicao_planeta[0]))
        self.input_pos_y = InputBox(610, 300, 150, 32, str(self.posicao_planeta[1]))
        self.input_vel_x = InputBox(450, 400, 150, 32, str(self.velocidade_planeta[0]))
        self.input_vel_y = InputBox(610, 400, 150, 32, str(self.velocidade_planeta[1]))
        
        self.input_boxes = [
            self.input_massa_estrela, 
            self.input_massa_planeta, 
            self.input_pos_x, 
            self.input_pos_y,
            self.input_vel_x,
            self.input_vel_y
        ]
        
        self.font = pygame.font.Font("assets/VCR_OSD_MONO.ttf", 26)
        self.start_button = pygame.Rect(325, 500, 150, 50)

    def run(self):
        running = True
        while running:
            self.screen.fill((0, 0, 0))
            
            # Desenha titulo
            font_title = pygame.font.Font("assets/VCR_OSD_MONO.ttf", 60) #
            title = font_title.render("orb", False, (255, 255, 255)) #
            self.screen.blit(title, (350, 10)) #
            
            # Desenhar labels
            labels = [
                "Massa da Estrela:",
                "Massa do Planeta:",
                "Posição do Planeta:",
                "Velocidade do Planeta:",
            ]
            
            for i, label_text in enumerate(labels):
                label = self.font.render(label_text, True, (255, 255, 255))
                self.screen.blit(label, (50, 105 + i*100))
            
            # Desenhar botão de início
            pygame.draw.rect(self.screen, (0, 255, 0), self.start_button)
            start_text = self.font.render('Começar', True, (0, 0, 0))
            start_text_rect = start_text.get_rect(center=self.start_button.center)
            self.screen.blit(start_text, start_text_rect)
            
            # Processar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                for box in self.input_boxes:
                    box.handle_event(event)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.collidepoint(event.pos):
                        # Coletar e converter valores
                        try:
                            config = {
                                'massa_estrela': float(self.input_massa_estrela.text),
                                'massa_planeta': float(self.input_massa_planeta.text),
                                'posicao_planeta': [
                                    float(self.input_pos_x.text), 
                                    float(self.input_pos_y.text)
                                ],
                                'velocidade_planeta': [
                                    float(self.input_vel_x.text), 
                                    float(self.input_vel_y.text)
                                ]
                            }
                            return config
                        except ValueError:
                            print("Valores inválidos. Por favor, insira números válidos.")
            
            # Atualizar e desenhar input boxes
            for box in self.input_boxes:
                box.update()
                box.draw(self.screen)
            
            pygame.display.flip()
        
        return None

G = 6.6 * 10 ** -11

# NOTE: as funções update_ke e update_pe sempre serão chamadas antes de update_e
class EnergyUpdater:
    def __init__(self, planet: Object, star: Object):
        self.planet = planet
        self.star = star

    # Energia cinética
    def update_ke(self):
        self.ke = 1/2 * self.planet.mass * np.linalg.norm(self.planet.v) ** 2
        return f" T: {self.ke:.2e} "

    # Energia potencial
    def update_pe(self):
        self.pe = -G * self.star.mass * self.planet.mass / np.linalg.norm(self.planet.x)
        return f" V: {self.pe:.2e} "

    # Energia mecânica
    def update_e(self):
        return f" E: {self.ke + self.pe:.2e} "

def main():
    screen = Sandbox()
    config = screen.run()
    
    if config:
        # XXX
        engine = Engine(screen.screen, screen.font)
        
        star = Object(config['massa_estrela'], 12, trail=False)
        planet = Object(config['massa_planeta'], 3, trail=True)
        
        planet.x = np.array(config['posicao_planeta'])
        planet.v = np.array(config['velocidade_planeta'])
        
        planet.add_force(lambda r: -G * config['massa_estrela'] * config['massa_planeta'] * r / np.linalg.norm(r) ** 3)
        
        engine.add_object(star)
        engine.add_object(planet)

        energy_updater = EnergyUpdater(planet, star)

        # Energia cinética, potencial e mecânica do sistema
        engine.add_text_with_updater(energy_updater.update_ke, np.array([10, 500]))
        engine.add_text_with_updater(energy_updater.update_pe, np.array([10, 530]))
        engine.add_text_with_updater(energy_updater.update_e, np.array([10, 560]))
                
        while not engine.done:
            engine.step()
            engine.process_events()
            if engine.reset_event_triggered:
                main()

if __name__ == "__main__":
    main()
