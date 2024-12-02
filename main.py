import pygame
import sys
import numpy as np

from engine import Engine, Object
        
class InputBox:
    """
    Classe responsável por exibir e gerenciar caixas de entrada de texto interativas em uma interface gráfica usando o pygame.

    Através das funções é possível que sejam exibidas inserções e alterações nos valores de inicilização da simulação
    feitas pelo usuário diretamente na interface gráfica do menu, cada caixa reage conforme cliques do mouse que 
    habilitam a escrita indicada por mudanças de cor (ativo/inativo), além disso a as caixas possuem 
    redimensionamento automático para acomodar o conteúdo textual.

    Atributos:
        rect (pygame.Rect): Retângulo delimitador da caixa de entrada.
        color_inactive (pygame.Color): Cor da borda quando a caixa está inativa (não selecionada).
        color_active (pygame.Color): Cor da borda quando a caixa está ativa (selecionada para alterações).
        color (pygame.Color): Cor atual da borda (ativa ou inativa).
        text (str): Texto inserido na caixa.
        font (pygame.font.Font): Fonte usada para renderizar o texto.
        active (bool): Indica se a caixa está ativa (habilitada para entrada de texto).
    """
    def __init__(self, x, y, w, h, text=''):
        """
        Inicializa os atributos do novo objeto 

        Parâmetros:
            x (int): Coordenada X do canto superior esquerdo da caixa.
            y (int): Coordenada Y do canto superior esquerdo da caixa.
            w (int): Largura inicial da caixa.
            h (int): Altura da caixa.
            text (str): Texto inicial da caixa (padrão: string vazia).
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('firebrick4')
        self.color_active = pygame.Color('firebrick1')
        self.color = self.color_inactive
        self.text = text
        self.font = pygame.font.Font("assets/Terminus.ttf", 32)
        self.active = False

    def handle_event(self, event):
        """
        Gerencia eventos relacionados à interação com a caixa de entrada.

        Parâmetros:
            event (pygame.event.Event): Evento capturado pelo pygame.

        Comportamentos:
            - Clique do mouse aaltera o estado da caixa (ativo/inativo).
            - Entradas do teclado são adicionadas ao texto da caixa se a caixa estiver ativa.
            - Backspace remove o último caractere inserido se a caixa estiver ativa.
            - DELETE remove o primeiro caractere inserido se a caixa estiver ativa.
        """
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
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_DELETE:
                    self.text = self.text[1:]
                elif event.unicode.isprintable():
                    self.text += event.unicode
        
    def update(self):
        """
        Ajusta dinamicamente a largura da caixa de entrada com base no conteúdo atual.

        O tamanho mínimo da caixa é definido por padrao, mas ela se expande caso necessário para
        acomodar o texto inserido, essa atualização é chamada sempre que o conteúdo muda.
        """
        # Faz o resize do box
        width = max(80, self.font.render(self.text, False, self.color).get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        """
        Renderiza a caixa de entrada e seu conteúdo na tela.

        Parâmetros:
            screen (pygame.Surface): Superfície do pygame onde a caixa será desenhada.

        Comportamentos:
            - Desenha a borda da caixa com a cor correspondente ao estado (ativo/inativo).
            - Centraliza o texto dentro da caixa e o desenha.
        """
        # Renderiza o texto do input box
        txt_surface = self.font.render(self.text, False, self.color)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        screen.blit(txt_surface, txt_rect)
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Sandbox:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('orb')
        
        # Configurações padrão
        self.massa_estrela = 5
        self.massa_planeta = 100
        self.posicao_planeta = [110, 100]
        self.velocidade_planeta = [100, -90]
        
        # Criar input boxes
        self.input_massa_estrela = InputBox(520, 130, 200, 42, str(self.massa_estrela))
        self.input_massa_planeta = InputBox(520, 230, 200, 42, str(self.massa_planeta))
        self.input_pos_x = InputBox(520, 330, 150, 42, str(self.posicao_planeta[0]))
        self.input_pos_y = InputBox(610, 330, 150, 42, str(self.posicao_planeta[1]))
        self.input_vel_x = InputBox(520, 430, 150, 42, str(self.velocidade_planeta[0]))
        self.input_vel_y = InputBox(610, 430, 150, 42, str(self.velocidade_planeta[1]))
        
        self.input_boxes = [
            self.input_massa_estrela, 
            self.input_massa_planeta, 
            self.input_pos_x,
            self.input_pos_y,
            self.input_vel_x,
            self.input_vel_y
        ]
        
        self.font = pygame.font.Font("assets/Terminus.ttf", 32)
        self.start_button = pygame.Rect(325, 510, 150, 50)

    def run(self):
        running = True
        while running:
            self.screen.fill([20] * 3)
            
            # Desenha titulo
            font_title = pygame.font.Font("assets/Terminus.ttf", 96) #
            title = font_title.render("orb", False, (255, 255, 255)) #
            self.screen.blit(title, (330, 20)) #
            
            # Desenhar labels
            labels = [
                "Massa da Estrela (1e16 kg):",
                "Massa do Planeta (kg):",
                "Posição do Planeta (m):",
                "Velocidade do Planeta (m/s):",
            ]
            
            for i, label_text in enumerate(labels):
                label = self.font.render(label_text, False, (255, 255, 255))
                self.screen.blit(label, (50, 135 + i*100))

            label = self.font.render("x", False, 'firebrick4')
            self.screen.blit(label, (550, 295))
            label = self.font.render("y", False, 'firebrick4')
            self.screen.blit(label, (640, 295))
            
            # Desenhar botão de início
            pygame.draw.rect(self.screen, 'firebrick1', self.start_button)
            start_text = self.font.render('Começar', False, (20, 20, 20))
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
                                'massa_estrela': float(self.input_massa_estrela.text) * 1e16,
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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        try:
                            config = {
                                'massa_estrela': float(self.input_massa_estrela.text) * 1e16,
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
        return f" T: {' ' if self.ke >= 0 else ''}{self.ke:.2e}"

    # Energia potencial
    def update_pe(self):
        self.pe = -G * self.star.mass * self.planet.mass / np.linalg.norm(self.planet.x)
        return f" V: {' ' if self.pe >= 0 else ''}{self.pe:.2e}"

    # Energia mecânica
    def update_e(self):
        self.e = self.ke + self.pe
        
        return f" E: {' ' if self.e >= 0 else ''}{self.e:.2e}"

def main():
    screen = Sandbox()
    config = screen.run()
    
    if config:
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

        # Mostra a posição do viewport
        engine.add_text_with_updater(lambda: f"({engine.viewport_center[0]:.3g}, {engine.viewport_center[1]:.3g})", np.array([10, 10]))

        # Mostra key/mouse binds
        engine.add_text_with_updater(lambda: " ctrl +/-: mudar zoom", np.array([450, 500]))
        engine.add_text_with_updater(lambda: "r: reset, esc: pausar", np.array([450, 530]))
        engine.add_text_with_updater(lambda: "  mouse: mover câmera", np.array([450, 560]))

        while not engine.done:
            engine.step()
            engine.process_events()
            if engine.reset_event_triggered:
                main()

if __name__ == "__main__":
    main()
