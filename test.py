import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, num=101)
y = np.cos(-x**2 / 9.0)
xnew = np.linspace(0, 10, num=11)
ynew = np.interp(xnew, x, y)
print(len(x))
print(len(xnew))
print(len(y))
print(len(ynew))
plt.plot(xnew, ynew, '-', label='linear interp')
plt.plot(x, y, 'o', label='data')
plt.legend(loc='best')
plt.show()