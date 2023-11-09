import matplotlib.pyplot as plt, mpld3
import numpy as np

# Define a function using lambda
stock = lambda A, amp, angle, phase: A * angle + amp * np.sin(angle + phase)

# Define parameters
theta = np.linspace(0., 2 * np.pi, 250) # x-axis
np.random.seed(100)
noise = 0.2 * np.random.random(250)
y = stock(.1, .2, theta, 1.2) + noise # y-axis

N = 9
x = np.linspace(0, 6*np.pi, N)

mean_stock = (stock(.1, .2, x, 1.2))
np.random.seed(100)
upper_stock = mean_stock + np.random.randint(N) * 0.02
lower_stock = mean_stock - np.random.randint(N) * 0.015

plt.plot(x, mean_stock, color = 'darkorchid', label = r'$y = \gamma \sin(\theta + \phi_0)$')

plt.fill_between(x, upper_stock, lower_stock, alpha = .1, color = 'darkorchid')
plt.grid(alpha = .2)

plt.xlabel(r'$\theta$ (rad)', labelpad = 15)
plt.ylabel('y', labelpad = 15)
plt.legend()
#plt.savefig('fill_between.png', dpi = 300, bbox_inches = 'tight', pad_inches = .1)
plt.show()
