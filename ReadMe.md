# Orb
## Simulador de lançamento com força gravitacional

### Descrição básica do projeto
Orb é o simulador físico que usa força gravitacional para calcular a trajetória de um planeta ao redor de uma estrela e a energia envolvida no sistema. A ideia foi conseguir visualizar como diferentes condições iniciais mudam a trajetória e velocidade do planeta e a troca de energia potencial e cinética ao longo do tempo.  
Para isso, criamos um programa em python que simula a gravitação newtoniana, com uma interface gráfica que permite ao usuário definir os parâmetros iniciais, visualizar o movimento planetário e recomeçar várias vezes.

<p align="center">
  <img width="500" height="500" src="https://github.com/user-attachments/assets/38b0ac0d-52c4-433b-b747-387982ce115b">
</p>


<p align="center">
  <img src="https://github.com/user-attachments/assets/527425c7-c758-4220-837a-aa20c485ea4f">
</p>

## Conceitos de Física e Modelo Matemático:

### 1. Sistema adotado
Adotando que a massa da estrela ($$M$$) é muito maior qua a massa do planeta ($$m$$), logo, podemos assumir que o centro de massa do sistema se encontra no centro da estrela. Além disso, como a trajetória criada por uma força central é plana, podemos usar o sistema polar de coordenadas $$(r, θ)$$. Tal que:

$$\vec{r} = r \hat{r}$$
$$\vec{v} = \dot{r} \hat{r} + r \dot{\theta} \hat{\theta}$$

onde:
- $$\hat{r}$$ é o versor na direção radial;
- $$\hat{\theta}$$ é o versor na direção tangencial.

Dessa forma, podemos escrever o módulo da velocidade como:

$$v^2 = \dot{r^2} + r^2 \dot{\theta^2}$$

#### 2. Momento angular
Podemos escrever o vetor momento angular da seguinte forma:

$$\vec{L} = \vec{r} \times \vec{p} = m \vec{r} \times \vec{\dot{r}} = m r^2 \dot{\theta} \hat{k},$$

$$L = m r^2 \dot{\theta}$$

Isolando $$\dot{\theta}$$ temos:

$$\dot{\theta} = \frac{L}{mr^2}$$

#### 3. Energia total 
Logo, a energia total do sistema pode ser escrita como, energia cinética ($$E_c$$) mais Energia potencial ($$E_{pot}$$)

$$E = E_c + E_{pot} = m\frac{v^2}{2} -\frac{k}{r} = m\frac{(\dot{r^2} + r^2 \dot{\theta^2})}{2} -\frac{k}{r}$$

Sendo 
- $$k = GMm$$,
- $$G$$ = Constante Gravitacional

Substituindo $$\dot{\theta}$$ pela equação isolada anteriormente, temos:

$$E = \frac{1}{2} m \dot{r}^2 + \frac{L^2}{2 m r^2} - \frac{K}{r}$$

Reescrevendo em função de $$\frac{dr}{dt}$$

$$E = \frac{1}{2} m {(\frac{dr}{dt}})^2 + \frac{L^2}{2 m r^2} - \frac{K}{r}$$

#### 4. $$d\theta$$ em função da Energia 
Sabendo que:

$$\dot{\theta} = \frac{d\theta}{dt} = \frac{L}{mr^2}$$

$$dt = \frac{mr^2 d\theta}{L}$$

Logo, substituindo na última equação de Energia encontrada:

$$E = \frac{L^2}{2 m r^4} \left( \frac{dr}{d\theta} \right)^2 + \frac{L^2}{2 m r^2} - \frac{K}{r}$$

isolando $$d\theta$$ em função $$dr$$ temos:

$$d\theta = \frac{dr}{\sqrt{\frac{2m E}{L^2}r^4 + \frac{2m K}{L^2}r^3 - r^2}} = \frac{dr}{r^2 \sqrt{\frac{2m E}{L^2} + \frac{2m K}{L^2} r^{-1} - r^{-2}}}$$

#### 5. Solução para $$r$$ 
Após integrar de ambos os lados, encontramos a seguinte solução:

$$\frac{1}{r} = \frac{m K}{L^2}\left[ 1 + e \cos(\theta - \theta_0) \right],$$

onde:

- $$e = \sqrt{1 + 2 \frac{E}{\epsilon}}$$ 
- $$\epsilon = \frac{m K^2}{L^2}$$

Evidenciando uma orbita eliptica.

#### 6. Análise da Orbita
Atráves da equação encontrada da excentricidade, 

$$e = \sqrt{1 + 2 \frac{E}{\epsilon}}$$

podemos montar a seguinte tabela: 

| Excentricidade | Energia | tipo de Orbita |
| ------ | ------ | ------ | 
| $$e > 1$$ | $$E>0$$ | Hiperbole|
| $$e = 1$$ | $$E=0$$ | Parábola |
| $$e<1$$ | $$E < 0$$ | Elipese |
| $$e=0$$ | $$E = -\frac{\epsilon}{2}$$ | Circunferência |

#### 7. Método adotado no nosso simulador

Utilizamos coordenada cartesianas, em que a origem se encontra no centro de massa da estrela. E de acordo com a segunda lei de Newton, temos:

$$
\vec{F} = m\vec{a} = \frac{GMm}{r^2}\hat{r}
$$

$$
\vec{a} = \frac{GM}{r^2}\hat{r}
$$

Com isso podemos adotar o método numérico de **Velocity Verlet**, 
Passo intermediário:

$$
\vec{v}\_{(t+\frac{1}{2}\Delta t)} = \vec{v}\_{(t)} + \frac{1}{2}\vec{a}\_{(t)}\Delta t
$$

$$
\vec{x}\_{(t+\Delta t)} = \vec{x}\_{(t)} + \vec{v}\_{(t+\frac{1}{2}\Delta t)}\Delta t
$$

Logo, podemos encontrar o vetor posição e velocidade final

$$
\vec{x}\_{(t+\Delta t)} = \vec{x}\_{(t)} + \vec{v}\_{(t)} \Delta t + \frac{1}{2}\vec{a}\_{(t)}\Delta t^2
$$

$$
\vec{v}\_{(t+\Delta t)} = \vec{v}\_{(t)} + \frac{1}{2}((\vec{a}\_{(t)} + \vec{a}\_{(t + \Delta t)})\Delta t)
$$

#### 8. Conclusão
Dado a posição inicial do planeta (sua distância inicial em relação à estrela) e sua velocidade, podemos calcular sua energia mecânica total. Com base nessa energia, conseguimos determinar o tipo de órbita, bem como descrever sua trajetória ao longo do tempo.

### Implementação

#### Linguagens e pacotes:
Este projeto utiliza apenas a linguagem Python (o código é compatível com as versões 3.10 e adiante) e as bibliotecas Numpy e Pygame. O Numpy nos permite rapidamente realizar os cálculos com vetores usados na simulação, enquanto o Pygame nos permite facilmente implementar a parte gráfica e interativa.

#### Organização:
O programa foi separado em dois arquivos: a main, onde está a equação da gravitação newtoniana e o comportamento do programa, e a engine, que cuida da atualização das posições, velocidade e aceleração e de todas as burocracias do pygame para atualizar os textos e partículas na tela.

### Como usar

#### Instalação

  Antes de tudo, certifique-se de ter instalado em seu computador o interpretador de Python configurado para as versões 3.10 e mais recentes. No Windows, isso pode ser feito na Microsoft Store, pesquisando "Python" e instalando a versão mais recente, ou ainda usando o Visual Studio Code, com um pacote da linguagem. No Linux, instale o pacote da linguagem que sua distribuição oferece: [Debian/Ubuntu e Fedora](https://python.org.br/instalacao-linux/) ou [Arch](https://wiki.archlinux.org/title/Python_(Portugu%C3%AAs))  
  Após isso, faça o download de nosso repositório no seu computador. É possível fazer isso clicando no botão "Código"(Code) na tela inicial do repositório e em "Download zip", ou, na linha de comando, usando:

  ```sh
  git clone https://github.com/vrveiga/orb.git
```

#### Dependências

  Como dito, o programa usa Pygame e Numpy, bibliotecas do Python que podem ser mais facilmente baixadas usando o instalador oficial de pacotes do Python, o pip:

  ```sh
  pip install numpy
  pip install pygame
  ```
#### Execução
  Tudo instalado, apenas execute, no diretório em que o repositório está, o programa main:

  ```sh
  python main.py
  ```
  
  Uma tela irá aparecer. Nessa interface, você poderá ajustar os parâmetros iniciais clicando nos números e digitando-os. Pode-se ajustar:
  
   - massa da estrela em 1e16 kg
   - massa do planeta em kg
   - posição inicial do planeta em metros
   - velocidade inicial do planeta em m/s

  Após inserir os valores desejados, clique em "Começar" ou aperte a tecla "Enter" e a simulação será apresentada.
  
### Informações sobre o projeto
Este projeto foi desenvolvido por:

```
Felipe Camargo Cerri: felipecamargocerri@usp.br
João Gabriel Araújo de Bastos: joaog.bastos@usp.br
João Pedro Monteiro Machado Junqueira Castelli: jotapcastelli@usp.br
Matheus Muzza Pires Ferreira: matheusmpf@usp.br
Marcelo Martins Conti: marcelo.mmartins@usp.br
Vitor Rocha Veiga: vitorveiga@usp.br
```

## Referências:
(1) Bernardes, E. de S. (2024). Gravitação (Notas de aula). 7600105 - Física Básica I. Universidade de São Paulo, São Carlos.  
(2) Wikipedia contributors. (2024, Setembro 28). Verlet integration. Em Wikipedia, The Free Encyclopedia. Acesso 10:33, Dezembro 3, 2024, de https://en.wikipedia.org/w/index.php?title=Verlet_integration&oldid=1248330084  
(3) Morten Hjorth-Jensen. (2020, Setembro 24). The Verlet method. Em Computational Physics Lectures: Ordinary differential equations. Acesso 10:42, Dezembro 3, 2024, de https://compphysics.github.io/ComputationalPhysics/doc/pub/ode/html/._ode-bs017.html  
(4) Pygame Github organisation. Pygame official documentation. Acesso 10:34, Dezembro 3, 2024, de https://www.pygame.org/docs/  
