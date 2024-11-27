import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

v0 = 40
ang = np.deg2rad(45)
g = 9.81
y0 = 20

v0x = v0 * np.cos(ang)
v0y = v0 * np.sin(ang)

tempo_total = (v0y + np.sqrt(v0y**2 + 2 * g * y0)) / g

t = np.linspace(0, tempo_total, 500)
    
x = v0x * t
y = y0 + v0y * t - 0.5 * g * t**2

plt.figure(figsize=(10,6))
plt.plot(x, y, 'r--')
plt.show()