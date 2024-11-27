import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider

def calculate(v0, ang, y0, g):
    ang  = np.deg2rad(ang)

    v0x = v0 * np.cos(ang)
    v0y = v0 * np.sin(ang)

    total_time = (v0y + np.sqrt(v0y**2 + 2 * g * y0)) / g

    t = np.linspace(0, total_time, 500)
        
    x = v0x * t
    y = y0 + v0y * t - 0.5 * g * t**2

    return x, y

def update(val):
    v0 = s_v0.val
    ang = s_ang.val
    y0 = s_y0.val
    g = s_g.val

    ax.clear()

    x, y = calculate(v0, ang, y0, g)
    ax.plot(x, y, 'r--')
    ax.grid(True)

    fig.canvas.draw_idle() #


fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(left=0.1, bottom=0.25) #

x, y = calculate(20, 45, 0, 9.8)

ax.plot(x, y, 'r--')
ax.grid(True)

# cria sliders
ax_v0 = plt.axes([0.2, 0.1, 0.65, 0.03])
s_v0 = Slider(ax_v0, 'Velocidade Inicial (m/s)', 1, 50, valinit=20)

ax_ang = plt.axes([0.2, 0.06, 0.65, 0.03])
s_ang = Slider(ax_ang, 'Ângulo (graus)', 0, 90, valinit=45)

ax_y0 = plt.axes([0.2, 0.02, 0.65, 0.03])
s_y0 = Slider(ax_y0, 'Altura Inicial (m/s²)', 0, 100, valinit=0)

ax_g = plt.axes([0.2, 0.04, 0.65, 0.03])
s_g = Slider(ax_g, 'Gravidade (m/s²)', 1, 20, valinit=9.8)

s_v0.on_changed(update)
s_ang.on_changed(update)
s_y0.on_changed(update)
s_g.on_changed(update)

plt.show()