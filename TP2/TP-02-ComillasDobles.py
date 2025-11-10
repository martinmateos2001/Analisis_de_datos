#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 10:31:07 2025

@author: Estudiante
"""
"""
Nombre del grupo: "Comillas Dobles"
Participantes:
- Martin Mateos
- Salvador Durand
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
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedGroupKFold, StratifiedKFold
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report, f1_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier, plot_tree

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

# cuento el numero de datos que pertenecen a cada clase
conteo_clases = df_datos['label'].value_counts()

# Creo el gráfico de barras
plt.bar(conteo_clases.index, conteo_clases.values)
plt.title("Cantidad de ejemplos por clase")
plt.xlabel("Clase")
plt.ylabel("Cantidad de imágenes")
plt.xticks(range(10))
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

# matriz de confusion 700 pixeles y 3 vecinos
cm = confusion_matrix(y_test, y_pred, labels=[4, 5])

plt.figure(figsize=(5,4))
sb.heatmap(cm, annot=True, fmt='d', cmap='Blues',
           xticklabels=[4, 5], yticklabels=[4, 5])
plt.xlabel('Predicción')
plt.ylabel('Valor real')
plt.title('Matriz de confusión para 700 atributos (clases 4 y 5)')
plt.show()

#%% Comparacion de modelos KNN 

k_vecinos = [3, 5, 7, 9, 11]
pixeles = [3, 10, 100, 300, 500, 700, 784]
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

top3 = df_resultados.nlargest(3, 'Accuracy')
print(top3)

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

# Visualizamos la matriz de confusion del mejor modelo
# Reentreno - sabemos los valores del print top 3 que son todos los pixeles y 3 vecinos
modelo = KNeighborsClassifier(n_neighbors=3)
modelo.fit(x_train, y_train)
y_pred = modelo.predict(x_test)

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sb.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=[4, 5], yticklabels=[4, 5])
plt.xlabel('Predicción')
plt.ylabel('Valor real')
plt.title('Matriz de confusión')
plt.show()


#%% Construcción de los datos dev y held out para el decision tree

x = df_datos.drop('label', axis = 1).values
y = df_datos['label'].values

x_dev, x_held, y_dev, y_held = train_test_split(x, y, test_size= 0.2, random_state= 42, stratify = y)


print("Datos de desarrollo: ", x_dev.shape)
print("Datos de validacion (held out):", x_held.shape)
print("Datos de etiquetas de desarrollo: ", y_dev.shape)
print("Datos de etiquetas de validación (held out): ", y_held.shape)
#%% Prueba de las distintas profundidades

depths = [i for i in range(1,9, 2)] + [10] # 1, 3, 5, 7 para acortar el tiempo de ejecucion.

mean_scores = []

for d in depths:
    tree = DecisionTreeClassifier(max_depth = d, random_state= 42, criterion='entropy')
    scores = cross_val_score(tree,x_dev, y_dev, cv=4, scoring = 'accuracy') # cv=5 -> cv=4
    mean_scores.append(np.mean(scores))


print(f"Profundidad = {d}, accuracy promedio = {np.mean(scores):.4f}")
best_depth = depths[np.argmax(mean_scores)]
print(f"\n Mejor profundidad seleccionada: {best_depth}")

# El coste era alto ahora tarda mucho menos : ), sigue seleccionando la profundidad mas alta.
# Por lo menos en mi pc tardo aprox 5min antes de los cambios, ahora son aprox 2

#%% Seleccionamos la mejor profundidad

best_tree = DecisionTreeClassifier(max_depth= best_depth, random_state= 42)
best_tree.fit(x_dev, y_dev)

# Visualizar el arbol
plt.figure(figsize=(25, 12))
plot_tree(best_tree, filled=True, max_depth=3, fontsize=8)
plt.title("Árbol de Decisión con profundidad parcial 3 (Máxima profunidad = 10)")
plt.show()
#%% Visualizamos metricas

# comparación de rendimiento x max profundidad

plt.figure(figsize=(8,5))
plt.plot(depths, mean_scores, marker='o', linestyle='-', color='blue')
plt.title('Exactitud promedio vs profundidad del árbol')
plt.xlabel('Profundidad máxima (10)')
plt.ylabel('Exactitud promedio (accuracy)')
plt.xticks(depths)
plt.grid(True)
plt.show()

# Mejor arbol
y_pred = best_tree.predict(x_held)


print("\n reporte de Clasificacion: ")
print(classification_report(y_held, y_pred))
cm = confusion_matrix(y_held, y_pred)

# print("\n Matriz de confusion: \n", cm)

#imagen de la matriz
plt.figure(figsize=(6, 5))
sb.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicción')
plt.ylabel('Valor real')
plt.title('Matriz de confusión')
plt.show()

#%% Cross validation para comparar

tree = DecisionTreeClassifier(random_state=42)

param_grid = {
    'max_depth' : depths, 
    'min_samples_split' : [2,5,10], 
    'min_samples_leaf' : [2], 
    'criterion' : ['gini', 'entropy'] }

cv = StratifiedKFold(n_splits= 4, shuffle= True, random_state=42)

grid_search = GridSearchCV(
    estimator = tree, 
    param_grid = param_grid, 
    cv=cv, 
    scoring = 'accuracy', 
    n_jobs = -1, 
    verbose = 1)

grid_search.fit(x_dev, y_dev)

#Guardo los resultados de los árboles
resultados = pd.DataFrame(grid_search.cv_results_)

print("Mejores parametros encontrados")
print(grid_search.best_params_)
print(f"Mejor exactitud promedio en validacion: {grid_search.best_score_:.3f}")

# Mejores parametros encontrados
# {'criterion': 'entropy', 'max_depth': 10, 'min_samples_leaf': 2, 'min_samples_split': 5}
# Mejor exactitud promedio en validacion: 0.716

#%% Predicciones
# Busco el mejor el arbol
mejor_arbol = grid_search.best_estimator_

# Visualizar el arbol
plt.figure(figsize=(25, 12))
plot_tree(mejor_arbol, filled=True, max_depth=3, fontsize=8)
plt.title("Árbol de Decisión con profundidad parcial 3 (Máxima profunidad = 10)")
plt.show()

# Lo entreno
mejor_arbol.fit(x_dev, y_dev)

# Predicciones
y_pred_held = mejor_arbol.predict(x_held)

# Vizualizacion matriz de confusion 

cm = confusion_matrix(y_held, y_pred_held)

plt.figure(figsize=(6, 5))
sb.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicción')
plt.ylabel('Valor real')
plt.title('Matriz de confusión')
plt.show()
