# -*- coding: utf-8 -*-

#%% importamos las librerias

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#%% PRUEBA - Intento ver el primer caracter.

df_caracteres = pd.read_csv('kuzushiji_full.csv')

primero = df_caracteres.iloc[0, [i for i in range(784)]] 
#selecciono todas las columnas menos label y selecciono la fila cero

primero = np.array(primero).reshape((28, 28))
#Transformo a matriz

plt.imshow(primero, cmap='gray')
plt.show