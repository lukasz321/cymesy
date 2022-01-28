import numpy as np
import matplotlib.pyplot as plt, mpld3
from matplotlib.patches import ConnectionPatch
# Define a function using lambda
stock = lambda A, amp, angle, phase: A * angle + amp * np.sin(angle + phase)

# Define parameters 
theta = np.linspace(0., 2 * np.pi, 250) # x-axis
np.random.seed(100)
noise = 0.2 * np.random.random(250)
y = stock(.1, .2, theta, 1.2) + noise # y-axis

# Create main container with size of 6x5
fig = plt.figure(figsize=(6, 5))
plt.subplots_adjust(bottom = 0., left = 0, top = 1., right = 1)

# Create first axes, the top-left plot with green plot
sub1 = fig.add_subplot(2,2,1) # two rows, two columns, fist cell
sub1.plot(theta, y, color = 'green')
sub1.set_xlim(1, 2)
sub1.set_ylim(0.2, .5)
sub1.set_ylabel('y', labelpad = 15)

# Create second axes, the top-left plot with orange plot
sub2 = fig.add_subplot(2,2,2) # two rows, two columns, second cell
sub2.plot(theta, y, color = 'orange')
sub2.set_xlim(5, 6)
sub2.set_ylim(.4, 1)

# Create third axes, a combination of third and fourth cell
sub3 = fig.add_subplot(2,2,(3,4)) # two rows, two colums, combined third and fourth cell
sub3.plot(theta, y, color = 'darkorchid', alpha = .7)
sub3.set_xlim(0, 6.5)
sub3.set_ylim(0, 1)
sub3.set_xlabel(r'$\theta$ (rad)', labelpad = 15)
sub3.set_ylabel('y', labelpad = 15)

# Create blocked area in third axes
sub3.fill_between((1,2), 0, 1, facecolor='green', alpha=0.2) # blocked area for first axes
sub3.fill_between((5,6), 0, 1, facecolor='orange', alpha=0.2) # blocked area for second axes

# Create left side of Connection patch for first axes
con1 = ConnectionPatch(xyA=(1, .2), coordsA=sub1.transData, 
                       xyB=(1, .3), coordsB=sub3.transData, color = 'green')
# Add left side to the figure
fig.add_artist(con1)

# Create right side of Connection patch for first axes
con2 = ConnectionPatch(xyA=(2, .2), coordsA=sub1.transData, 
                       xyB=(2, .3), coordsB=sub3.transData, color = 'green')
# Add right side to the figure
fig.add_artist(con2)

# Create left side of Connection patch for second axes
con3 = ConnectionPatch(xyA=(5, .4), coordsA=sub2.transData, 
                       xyB=(5, .5), coordsB=sub3.transData, color = 'orange')
# Add left side to the figure
fig.add_artist(con3)

# Create right side of Connection patch for second axes
con4 = ConnectionPatch(xyA=(6, .4), coordsA=sub2.transData, 
                       xyB=(6, .9), coordsB=sub3.transData, color = 'orange')
# Add right side to the figure
fig.add_artist(con4)
plt.show()
# Save figure with nice margin
plt.savefig('zoom_effect_2.png', dpi = 300, bbox_inches = 'tight', pad_inches = .1)
