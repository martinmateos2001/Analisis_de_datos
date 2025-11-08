#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 10:31:07 2025

@author: Estudiante
"""

#%% Imports y cargamos archivos
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sb
from scipy.signal import find_peaks
from IPython import get_ipython
import pandas as pd
import sklearn as sck
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedGroupKFold
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report, f1_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier

df_datos = pd.read_csv('kuzushiji_full.csv')

df_etiqueta = pd.read_csv('kmnist_classmap_char.csv')

#%% Exploracion dataframes
print(len(df_datos))

print(len(df_datos.columns))

print(len(df_etiqueta))

# Observamos caracteres
caracter = df_datos.iloc[55,[i for i in range (784)]]

caracter = np.array(caracter).reshape((28,28))

plt.imshow(caracter, cmap = 'gray')
plt.title("Imagen 56")
plt.show


#%% Clase 1


df_clase1 = df_datos.query('label == 1')
arr_clase1 = df_datos.query('label == 1').drop(columns = ['label']).values

x = arr_clase1

y = df_clase1['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 1')
plt.show()



#%% Clase 0

df_clase0 = df_datos.query('label == 0')
arr_clase0 = df_datos.query('label == 0').drop(columns = ['label']).values

x = arr_clase0

y = df_clase0['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 0')
plt.show()

#%% clase 2


df_clase2 = df_datos.query('label == 2')
arr_clase2 = df_datos.query('label == 2').drop(columns = ['label']).values

x = arr_clase2

y = df_clase2['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 2')
plt.show()

#%% clase 3

df_clase3 = df_datos.query('label == 3')
arr_clase3 = df_datos.query('label == 3').drop(columns = ['label']).values

x = arr_clase3

y = df_clase3['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 3')
plt.show()

#%%

df_clase4 = df_datos.query('label == 4')
arr_clase4 = df_datos.query('label == 4').drop(columns = ['label']).values

x = arr_clase4

y = df_clase4['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 4')
plt.show()

#%% 

df_clase5 = df_datos.query('label == 5')
arr_clase5 = df_datos.query('label == 5').drop(columns = ['label']).values

x = arr_clase5

y = df_clase5['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 5')
plt.show()

#%%

df_clase6 = df_datos.query('label == 6')
arr_clase6 = df_datos.query('label == 6').drop(columns = ['label']).values

x = arr_clase6

y = df_clase6['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 6')
plt.show()

#%%

df_clase7 = df_datos.query('label == 7')
arr_clase7 = df_datos.query('label == 7').drop(columns = ['label']).values

x = arr_clase7

y = df_clase7['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 7')
plt.show()

#%%

df_clase8 = df_datos.query('label == 8')
arr_clase8 = df_datos.query('label == 8').drop(columns = ['label']).values

x = arr_clase8

y = df_clase8['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 8')
plt.show()

#%% Funcion para mapa de calor

def mapCalorClase(clase:str):
   y = df_datos.query('label == @clase').drop(columns = ['label']).values
   x = df_datos.query('label == @clase').drop(columns = ['label']).values


   pixel_varianza = np.var(x/255, axis = 0)


   pixel_vsr_img = pixel_varianza.reshape(28,28)


   plt.figure(figsize = (6,6))
   sb.heatmap(pixel_vsr_img, cmap = 'viridis')
   plt.title(f'Mapa de calor de variabilidad por pixel de la clase {clase}')
   plt.show()
   


mapCalorClase(0)
mapCalorClase(1)
mapCalorClase(2)
mapCalorClase(3)
mapCalorClase(4)
mapCalorClase(5)
mapCalorClase(6)
mapCalorClase(7)
mapCalorClase(8)
mapCalorClase(9)

#%%

df_clase9 = df_datos.query('label == 9')
arr_clase9 = df_datos.query('label == 9').drop(columns = ['label']).values

x = arr_clase9/255

y = df_clase9['label'].values

pixel_varianza = np.var(x, axis = 0)

pixel_vsr_img = pixel_varianza.reshape(28,28)

plt.figure(figsize = (6,6))
sb.heatmap(pixel_vsr_img, cmap = 'viridis')
plt.title('Mapa de calor de variabilidad por pixel de la clase 9')
plt.show()

#%% Represenacion por promedio

x= df_datos.drop('label', axis = 1).values
y = df_datos['label'].values

for i in range(10):
    mean_img = x[y == i].mean(axis = 0).reshape(28,28)
    plt.subplot(2, 5, i+1)
    plt.imshow(mean_img, cmap = 'gray')
    plt.title(f'clase{i}')
    plt.axis('off')
    
plt.tight_layout()
plt.show()

#%% Representacion PSA

pca = PCA(n_components=2)
x_pca = pca.fit_transform(x)

plt.figure(figsize = (8,6))
sb.scatterplot(x = x_pca[:, 0], y = x_pca [:, 1], hue=y, palette = 'tab10', s=10)
plt.title('proyeccion PCA de los caracteres')
plt.show()

#%% Representacion por medianas

for i in range(10):
    median_img = np.median(x[y == i], axis = 0).reshape(28,28)
    plt.subplot(2, 5, i+1)
    plt.imshow(median_img, cmap = 'gray')
    plt.title(f'clase{i}')
    plt.axis('off')
    
plt.tight_layout()
plt.show()


#%% Mapas de calor de cada clase

plt.figure(figsize= (10,6))

for i in range (10):
    x_class = x[y == i]
    pixel_var = np.var(x_class, axis =  0)
    pixel_var_img = pixel_var.reshape(28,28)
    plt.subplot(2, 5, i+1)
    sb.heatmap(pixel_var_img, cmap = 'viridis', cbar = False)
    plt.title(f'clase {i}')
    plt.axis('off')
plt.suptitle('Mapas de calor distribuidos por varianza', fontsize=14)
plt.tight_layout()
plt.show()



#%% Clasificacion binaria - df con clases 4 y 5


df_4 = df_datos[y == 4 ]
df_5 = df_datos[y == 5]
df_4y5 = pd.concat ([df_4, df_5])
# df_4y5 = df_datos[(df_datos['label'] == 4) | (df_datos['label'] == 5)]
# print(len(df_4))
# print(len(df_5))
# print(len(df_4y5))

# BUSCAR MISMAS PROPORCIONES DE CLASES
#train, test = sck.model_selection.train_test_split(df_4y5, test_size=0.2, stratify=df_4y5['label'])
#%% PCA de clases 4 y 5

x= df_4y5.drop('label', axis = 1).values
y = df_4y5['label'].values

pca = PCA(n_components=2)
x_pca = pca.fit_transform(x)

plt.figure(figsize = (8,6))
sb.scatterplot(x = x_pca[:, 0], y = x_pca [:, 1], hue=y, palette = 'tab10', s=10)
plt.title('proyeccion PCA de los caracteres')
plt.show()

#%% Separacion de los datos de test y train para clase 4 y clase 5

mask = (y == 4) | (y==5)
x_sub = x[mask]
y_sub = y [mask]

x_train, x_test, y_train, y_test = train_test_split(x_sub, y_sub, test_size = 0.30, random_state =42, stratify = y_sub)

k = 700
selector = SelectKBest(score_func= f_classif, k=k)
x_train_sel = selector.fit_transform(x_train, y_train)
x_test_sel = selector.transform(x_test)

#%% Algoritmo knn con los datos de test y train

k_neigbors = 3
knn = KNeighborsClassifier(n_neighbors = k_neigbors)
knn.fit(x_train_sel, y_train)

y_pred = knn.predict(x_test_sel)

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, pos_label = 5)
rec = recall_score(y_test, y_pred, pos_label = 5)
f1 = f1_score(y_test, y_pred, pos_label = 5)

print(f"Accuracy: {acc: 6f}")
print(f"Precision: {prec: 6f}")
print(f"Recall: {rec: 6f}")
print(f"F1-score: {f1: 6f}")

print("otra forma")
print(classification_report(y_test, y_pred))

print(f"Cantidad de datos usados: {k} ")
print(f"Cantidad de vecinos usados: {k_neigbors}")

#%% Comparacion de modelos KNN 

k_vecinos = [1, 3, 5, 7, 9, 11]
pixeles = [3, 10, 100, 300, 600, 784]
resultados = []

for p in pixeles:
    selector = SelectKBest(f_classif, k=p)
    x_train_sel = selector.fit_transform(x_train, y_train)
    x_test_sel = selector.transform(x_test)
    for k in k_vecinos:
        modelo = KNeighborsClassifier(n_neighbors=k)
        modelo.fit(x_train_sel, y_train)
        y_pred = modelo.predict(x_test_sel)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='macro')
        rec = recall_score(y_test, y_pred, average='macro')
        
        resultados.append((p, k, acc, prec, rec))

df_resultados = pd.DataFrame(resultados, columns=['Pixeles', 'Vecinos', 'Accuracy', 'Precision', 'Recall'])

def rendimientoKNN(metrica:str):
    plt.figure(figsize=(10,6))
    for k in k_vecinos:
        subset = df_resultados[df_resultados['Vecinos'] == k]
        plt.plot(subset['Pixeles'], subset[metrica], marker='o', label=f'k={k}')

    plt.xlabel('Cantidad de atributos seleccionados')
    plt.ylabel(metrica)
    plt.title(f'{metrica} según cantidad de atributos y vecinos')
    plt.legend()
    plt.grid(True)
    plt.show()


rendimientoKNN('Accuracy')
rendimientoKNN('Precision')
rendimientoKNN('Recall')


#%% Construcción de los datos dev y held out para el decision tree

# comento esto porque los valores de x e y no cambian, la pc trabaja de mas :)
# x= df_datos.drop('label', axis = 1).values
# y = df_datos['label'].values



x_dev, x_held, y_dev, y_held = train_test_split(x, y, test_size= 0.2, random_state= 42, stratify = y)


print("Datos de desarrollo: ", x_dev.shape)
print("Datos de validacion (held out):", x_held.shape)

#%% Prueba de las distintas profundidades

depths = range(1,11)
mean_scores = []

for d in depths:
    tree = DecisionTreeClassifier(max_depth = d, random_state= 42)
    scores = cross_val_score(tree,x_dev, y_dev, cv=5, scoring = 'accuracy')
    mean_scores.append(np.mean(scores))
    
print(f"Profundidad = {d}, accuracy promedio = {np.mean(scores):.4f}")
best_depth = depths[np.argmax(mean_scores)]
print(f"\n Mejor profundidad seleccionada: {best_depth}")

#%% Seleccionamos la mejor profundidad

best_tree = DecisionTreeClassifier(max_depth= best_depth, random_state= 42)
best_tree.fit(x_dev, y_dev)


#%% Visualizamos metricas

y_pred = best_tree.predict(x_held)


print("\n reporte de Clasificacion: ")
print(classification_report(y_held, y_pred))
cm = confusion_matrix(y_held, y_pred)

print("\n Matriz de confusion: \n", cm)



#%% Cross validation para comparar

tree = DecisionTreeClassifier(random_state=42)
param_grid = {'max_depth' : [3,5,7,9,1 ], 'min_samples_split' : [2,5,10], 'min_samples_leaf' : [1,2,4], 'criterion' : ['gini', 'entropy'] }

cv = StratifiedGroupKFold(n_splits= 5, shuffle= True, random_state=42)
grid_search = GridSearchCV(estimator = tree, param_grid = param_grid, cv=cv, scoring = 'accuracy', n_jobs = -1, verbose = 1)

grid_search.fit(x_dev, y_dev)

print("Mejores parametros encontrados")
print(grid_search.best_params_)
print(f"Mejor exactitud promedio en validacion: {grid_search.best_score_:.3f}")




