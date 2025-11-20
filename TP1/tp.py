#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%


import pandas as pd
import duckdb as dd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#%% Funciones
def normalizarColumna(col:str) -> str:
    res = f"REPLACE(TRIM(UPPER({col})), 'Á', 'A')"
    res = f"REPLACE({res}, 'É','E')"
    res = f"REPLACE({res}, 'Í','I')"
    res = f"REPLACE({res}, 'Ó','O')"
    res = f"REPLACE({res}, 'Ú','U')"
    res = f"REPLACE({res}, '§','')"
    res = f"REPLACE({res}, 'º','')"
    res = f"REPLACE({res}, '°','')"
    res = f"REPLACE({res}, 'Ü','U')"
    res = f"REPLACE({res}, '''','')"
    res = f"REPLACE({res},'.', '')"
    res = f"REPLACE ({res}, 'CIUDAD DE BUENOS AIRES','CABA')"
    
    return res
def consultarCantNivelesPorDepto(nivel:str, nombreDelCount:str):
    consulta =  f"""
                   SELECT Provincia, Departamento, COUNT({nivel}) as {nombreDelCount}
                   FROM Establecimientos
                   WHERE {nivel} = '1'
                   GROUP BY Departamento, Provincia;
                   """
    return dd.sql(consulta).df()

def limpiarCodArea(area:str):
    sacar = 'AREA #'
    return area.replace(sacar, '')

def consultarPobPorRangos(edad_minima:int, edad_maxima:int, nombre_poblacion:str) -> pd.DataFrame:
    consulta = f"""
                SELECT 
                    Cod_Departamento, Departamento, 
                    SUM(Casos) as {nombre_poblacion}
                FROM padron_pob_limpio
                WHERE Edad >= {edad_minima} AND Edad <= {edad_maxima}
                GROUP BY Cod_Departamento, Departamento;
                """
    return dd.sql(consulta).df()

def agregarColumnaProvincia(nombre_df:str, nombre_col_pob:str):
    consultaAgregarProvinciaAPoblaciones = f"""
        SELECT 
            deptos.Provincia,
            {nombre_df}.Departamento,
            {nombre_df}.{nombre_col_pob}
        FROM {nombre_df}
        INNER JOIN tabla_deptos_provincia as deptos
        ON {nombre_df}.Cod_Departamento = deptos.Cod_Departamento;
        """
    return dd.sql(consultaAgregarProvinciaAPoblaciones).df()

def join_poblacion_cant(pob:str, col_pob:str, cant:str, col_cant:str):
    consulta = f"""
        SELECT 
            {cant}.Provincia,
            {cant}.Departamento,
            {cant}.{col_cant},
            {pob}.{col_pob}
        FROM {cant}
        INNER JOIN {pob}
        ON {cant}.Departamento = {pob}.Departamento AND {cant}.Provincia = {pob}.Provincia
        """
    return dd.sql(consulta).df()

#%% GQM
"""
Datos Críticos afectados:
    - Departamentos
    - Provincias
Entre y dentro de las tablas de EE y Departamentos por actividad y Género encontramos tuplas(Provincia, Departamento), escritas de distinta manera.
Estrategia:
    1- Agrupar filas por los atributos de calidad.
    2- Contar la cantidad de dicho atributo
    3- Identificar diferencias
"""

columnas_ee = 'A,L,N,U:AA'
Establecimientos = pd.read_excel("2022_padron_oficial_establecimientos_educativos.xlsx", 
                                 skiprows=6, usecols= columnas_ee)

deptos_actividad_genero = pd.read_csv('Datos_por_departamento_actividad_y_sexo.csv')

# Agrupo y cuento el numero de tuplas
consulta = """
SELECT
    Jurisdicción AS Provincia,
    Departamento
FROM Establecimientos
"""
ee = dd.sql(consulta).df()

# Veces que aparece cada departamento
consulta = """
SELECT
    Provincia,
    Departamento,
    COUNT(Departamento) AS Apariciones
FROM ee
GROUP BY Provincia, Departamento
ORDER BY Apariciones ASC;
"""

registrosEE = dd.sql(consulta).df()

p = normalizarColumna("Provincia")
d = normalizarColumna("Departamento")

consulta = f"""
SELECT
    {p} AS Provincia,
    {d} AS Departamento,
    COUNT(Departamento) AS Apariciones
FROM ee
GROUP BY Provincia, Departamento
ORDER BY Apariciones ASC
"""
registrosNormalizados = dd.sql(consulta).df()

# Busco problemas de consistencia por el número de apariciones normalizando las columnas de registrosEE y luego haciendo un join.
consulta = f"""
SELECT
    {p} AS Provincia,
    {d} AS Departamento,
    Apariciones
FROM registrosEE
"""

registrosEE = dd.sql(consulta).df()

# Hago el join y me quedo solo donde difieren en numero de apariciones.
consulta = """
SELECT *
FROM registrosEE AS r
FULL JOIN registrosNormalizados AS rn
ON r.Provincia = rn.Provincia AND r.Departamento = rn.Departamento
"""

resultados = dd.sql(consulta).df()


print("Tamaño de registros:", len(registrosEE))
print("Tamaño de registros normalizados:", len(registrosNormalizados))
print("Tamaño de resultados: ", len(resultados))

# Comparaciones.
# Tamaño de registros: 528
# Tamaño de registros normalizados: 528
# Tamaño de resultados:  528
# Por lo tanto no hay inconsistencias en la escritura dentro del dataset o nuestra normalizacion no la toma en cuenta.

#%% GQM - Repito el proceso para Departamentos por act...

deptos_actividad_genero = pd.read_csv('Datos_por_departamento_actividad_y_sexo.csv')

#obtengo datos
consulta = """
SELECT
    provincia AS Provincia,
    departamento AS Departamento,
    COUNT(Departamento) AS Apariciones
FROM deptos_actividad_genero
WHERE anio = 2022
GROUP BY Provincia, Departamento
ORDER BY Apariciones ASC;
"""

registrosAct = dd.sql(consulta).df()

# Normalizado
consulta = f"""
SELECT
    {p} AS Provincia,
    {d} AS Departamento,
    COUNT(Departamento) AS Apariciones
FROM deptos_actividad_genero
WHERE anio = 2022
GROUP BY Provincia, Departamento
ORDER BY Apariciones ASC;
"""

registrosActNormalizado = dd.sql(consulta).df()

# Normalizo las columnas para hacer el join
consulta = f"""
SELECT
    {p} AS Provincia,
    {d} AS Departamento,
    Apariciones
FROM registrosAct
"""

registrosAct = dd.sql(consulta).df()

#join
consulta = """
SELECT *
FROM registrosAct AS r
FULL JOIN registrosActNormalizado AS rn
ON r.Provincia = rn.Provincia AND r.Departamento = rn.Departamento
"""

resultados = dd.sql(consulta).df()


print("Tamaño de registros:", len(registrosAct))
print("Tamaño de registros normalizados:", len(registrosActNormalizado))
print("Tamaño de resultados: ", len(resultados))

# Comparaciones
# Tamaño de registros: 527
# Tamaño de registros normalizados: 527
# Tamaño de resultados:  527

# Tampoco hay inconsistencias dentro de este df pero sí se ve que se obtuvo un fila menos
# Entonces busco esta tupla que está de mas o de menos

# Departamentos que están en registrosEE pero no en registrosAct
consulta_diff_EE_Act = """ 
SELECT Provincia, Departamento
FROM registrosEE
EXCEPT
SELECT Provincia, Departamento
FROM registrosAct;
"""
diff_EE_Act = dd.sql(consulta_diff_EE_Act).df()

# Departamentos que están en registrosAct pero no en registrosEE
consulta_diff_Act_EE = """
SELECT Provincia, Departamento
FROM registrosAct
EXCEPT
SELECT Provincia, Departamento
FROM registrosEE;
"""
diff_Act_EE = dd.sql(consulta_diff_Act_EE).df()

print(len(diff_EE_Act), "tuplas aparecen en la tabla de EE pero no en la tabla de Actividad y Genero") #29
# 29 tuplas aparecen en la tabla de EE pero no en la tabla de Actividad y Genero

print(len(diff_Act_EE), "tuplas aparece en tabla de Actividad y Genero pero no en la tabla de EE") #28
# 28 tuplas aparece en tabla de Actividad y Genero pero no en la tabla de EE

""" Sigo sin ver cual está de mas o de menos pero pude diferencias en la escritura: 
        - CABA y CIUDAD... -> se pierden las comunas
        - GENERAL ... y GRAL ...
        - OHIGGINS Y O HIGGINS
        - hay un nombre que lleva punto (.)

El total de datos (tuplas)
"""
#%% GQM - Metricas
cantEE = len(registrosEE)
unicosEE = len(diff_EE_Act)
cantAct = len(registrosAct)
unicosAct = len(diff_Act_EE)
coincidencias = cantEE - unicosEE   # tambien pueden caluclar a partir de registrosAct
union = cantEE + cantAct - coincidencias


jacard = round((coincidencias / union)*100, 2)
print("Los atributos coinciden en un", jacard, "% por indice de jaccard.")

coincidenciaEEvsAct = round((coincidencias/cantEE)*100,2)
print("Los atributos de Establecimientos edcuativos coinciden en un " + str(coincidenciaEEvsAct) + "% sobre dataset Departamentos Actividad Genero")

coincidenciaActVsEE = round((coincidencias/cantAct)*100, 2)
print("Los atributos de Departamentos Actividad Genero coinciden en un " + str(coincidenciaActVsEE) + "% sobre dataset Establecimientos edcuativos")

diffSimetrica = round(((unicosAct + unicosEE)/ union)*100, 2)
print("La perdida atributos sobre pares provincia, departamento es del " + str(diffSimetrica) + "%")
#%%Limpieza del Dataset Establecimientos Educativos


columnas_ee = 'A,L,N,U:AA'
"""
A - Jurisdiccion
L - Departamento
N - Común
U - Jardin maternal
V - Jardin de infantes
W - Primario
X - Secundario
Y - Secundario - INET
Z - SNU
AA - SNU - INET
"""


Establecimientos = pd.read_excel("2022_padron_oficial_establecimientos_educativos.xlsx", 
                                 skiprows=6, usecols= columnas_ee)

#Eliminamos los establecimientos que no son comunes
#Eliminamos Cueanexo
jur = normalizarColumna("Jurisdicción")
dep = normalizarColumna("Departamento")

elimino = f"""
            SELECT 
                {jur} as Provincia, 
                {dep} as Departamento, 
                "Nivel inicial - Jardín maternal" as Maternal,
                "Nivel inicial - Jardín de infantes" as Jardin, 
                Primario, Secundario,
                "Secundario - INET" as SecuInet, 
                "SNU" as Snu, "SNU - INET" as SnuInet
                
            FROM Establecimientos
            WHERE Común = '1';
          """

Establecimientos = dd.sql(elimino).df()
Establecimientos.to_excel('Establecimientos_limpio.xlsx')


#%% Buscamos la cantidad de establecimientos Educativos que hay de cada nivel de modalidad común
cant_maternales_depto = consultarCantNivelesPorDepto('Maternal', 'Maternales')
cant_jardin_depto = consultarCantNivelesPorDepto('Jardin', 'Jardines')
cant_primaria_depto = consultarCantNivelesPorDepto('Primario', 'Primarios')
cant_secundaria_depto = consultarCantNivelesPorDepto('Secundario', 'Secundarios')
cant_secuInet_depto = consultarCantNivelesPorDepto("SecuInet", 'SecundariosInet')
cant_snu_depto = consultarCantNivelesPorDepto("Snu", 'SNUs')
cant_snuInet_depto = consultarCantNivelesPorDepto("SnuInet", 'SNUsInet')
#%% Reconstrucción del padron limpio

padron_poblacional = pd.read_excel("padron_poblacion.xlsX", skiprows=12, header=None)

padron_pob_limpio = pd.DataFrame(columns=['Cod_Departamento', 'Departamento', 'Edad', 'Casos'])
areas = []
deptos = []
edades = []
casos = []



area_actual = ""
depto_actual = ""
for index, row in padron_poblacional.iterrows():
    primera_celda = str(row[1])
    segunda_celda = str(row[2])
    if (pd.notnull(row[1])):
        primera_celda = primera_celda.strip()
        segunda_celda = segunda_celda.strip()
        if ("AREA" in primera_celda):
            area_actual= limpiarCodArea(primera_celda)
            depto_actual =  segunda_celda
        elif (primera_celda.isdigit()):
            areas.append(area_actual)
            deptos.append(depto_actual)
            edades.append(int(primera_celda))
            casos.append(int(segunda_celda))
        elif ("RESUMEN" in primera_celda):
            break

            

padron_pob_limpio['Cod_Departamento'] = areas
padron_pob_limpio['Departamento'] = deptos
padron_pob_limpio['Edad'] = edades
padron_pob_limpio['Casos'] = casos

# modifico datos para que coincidan con las otras tablas


deptos = normalizarColumna("Departamento")
consultaNormalizarDeptos =  f"""
                                SELECT 
                                    Cod_Departamento,
                                    {deptos} AS Departamento,
                                    Edad,
                                    Casos
                                FROM padron_pob_limpio
                            """
padron_pob_limpio = dd.sql(consultaNormalizarDeptos).df()

#%% busco la cantidad de personas que hay respecto a cada nivel educativo
"""
maternal es [0, 2]
infantes es [3, 5]
primaria es [6, 12]
secundaria es [12, 18]
secuInet es [12, 19]
snu y snuInet > 18 años
"""
#prueba = consultarPobPorRangos(0, 2, "asdf")


pob_maternal_depto = consultarPobPorRangos(0, 2, "Poblacion_Maternal")
pob_jardin_depto = consultarPobPorRangos(3, 5, "Poblacion_Jardin")
# Se solapan las poblaciones de 12 años
pob_primaria_depto = consultarPobPorRangos(6, 12, "Poblacion_Primaria")
pob_secu_depto = consultarPobPorRangos(12, 18, "Poblacion_Secundaria")
pob_secuInet_depto = consultarPobPorRangos(12, 18, "Poblacion_Secundaria_Inet")
pob_terciaria_joven = consultarPobPorRangos(18, 25, 'Poblacion_Terciaria_Joven')
pob_terciaria_mayor = consultarPobPorRangos(25, 54, 'Poblacion_Terciaria_Mayor')


#%% Datos por Departamento, Actividad y Género 

deptos_actividad_genero = pd.read_csv('Datos_por_departamento_actividad_y_sexo.csv')

#Tambien hay que poner todo en mayusculas y sin acentos.
deptos = normalizarColumna("departamento")
provincia = normalizarColumna("provincia")
consultaDatos2022 = f"""
                        SELECT 
                            in_departamentos AS Cod_Departamento,
                            {deptos} AS Departamento,
                            provincia_id AS Id_Provincia,
                            {provincia} AS Provincia,
                            clae6,
                            UPPER(genero) AS Genero,
                            Empleo,
                            Establecimientos,
                            empresas_exportadoras AS Exportadoras
                        FROM deptos_actividad_genero
                        WHERE anio = 2022
                    """

deptos_actividad_genero = dd.sql(consultaDatos2022).df()

deptos_actividad_genero.to_excel('exportacion_actividad_genero.xlsx')

#%% Tablas auxialiares, filtradas desde el dataset deptos_actividad_genero

consultaTablaProvincias =   """
                                SELECT DISTINCT 
                                    Id_Provincia, 
                                    Provincia
                                FROM deptos_actividad_genero;
                            """
tabla_provincias = dd.sql(consultaTablaProvincias).df()

consultaTablaDeptos =   """
                            SELECT DISTINCT 
                                Cod_Departamento, 
                                Departamento, 
                                Id_Provincia
                            FROM  deptos_actividad_genero
                            ORDER BY Cod_Departamento ASC;
                        """
tabla_deptos = dd.sql(consultaTablaDeptos).df()


#%% Formo la tabla del punto uno

"""
Las tablas de poblacion se ven 
|Cod_Departamento|Departamento|Poblacion_X|

Las tablas de cant EE de nivel X por depto se ven
|Provincia|Departamento|Xs|

El problema es que si hacemos inner join por nombre de departamento podemos mezclar con los que son de distintas 
provincias.
Para ello voy a utilizar la tabla_deptos también.

1- Agregar la provincia a los pob_X_depto
2- inner join por Departamento y Provincia
"""

consultaDeptosProvinciaNombre = """
SELECT Cod_Departamento, Departamento, tabla_provincias.Provincia
FROM tabla_deptos
INNER JOIN tabla_provincias
ON tabla_deptos.Id_Provincia = tabla_provincias.Id_Provincia;
"""

tabla_deptos_provincia = dd.sql(consultaDeptosProvinciaNombre).df()

pob_maternal_depto = agregarColumnaProvincia("pob_maternal_depto", "Poblacion_Maternal")
pob_jardin_depto = agregarColumnaProvincia("pob_jardin_depto", "Poblacion_Jardin")
pob_primaria_depto = agregarColumnaProvincia("pob_primaria_depto", "Poblacion_Primaria")
pob_secu_depto = agregarColumnaProvincia("pob_secu_depto", "Poblacion_Secundaria")
pob_secuInet_depto = agregarColumnaProvincia("pob_secuInet_depto", "Poblacion_Secundaria_Inet")
pob_terciaria_joven = agregarColumnaProvincia("pob_terciaria_joven", "Poblacion_Terciaria_Joven")
pob_terciaria_mayor = agregarColumnaProvincia("pob_terciaria_mayor", "Poblacion_Terciaria_Mayor")

#%%Join de cant establecimientos por nivel por depto y su poblacion

maternalesYpoblacion = join_poblacion_cant("pob_maternal_depto", "Poblacion_Maternal", 
                                             "cant_maternales_depto", "Maternales")

jardinesYpoblacion = join_poblacion_cant("pob_jardin_depto", "Poblacion_Jardin", 
                                      "cant_jardin_depto", "Jardines")

primariasYpoblacion = join_poblacion_cant("pob_primaria_depto", "Poblacion_Primaria", 
                                        "cant_primaria_depto", "Primarios")

secundariasYpoblacion = join_poblacion_cant("pob_secu_depto", "Poblacion_Secundaria", 
                                          "cant_secundaria_depto", "Secundarios")

secuInetYpoblacion = join_poblacion_cant("pob_secuInet_depto", "Poblacion_Secundaria_Inet", 
                                        "cant_secuInet_depto", "SecundariosInet")

snuYpoblacion = join_poblacion_cant("pob_terciaria_joven", "Poblacion_Terciaria_Joven", 
                                   "cant_snu_depto", "SNUs")
snuInetYpoblacion = join_poblacion_cant("pob_terciaria_mayor", "Poblacion_Terciaria_Mayor", 
                                       "cant_snuInet_depto", "SNUsInet")

#%% Punto 1 resultado - Join de la cantidad de establecimiento por nivel y sus respectivas poblaciones

# Genero diccionario para poder iterar las consultas de JOIN, la primera queda comentada pues se hizo en una variable aparte

diccJ = {
        # "maternalesYpoblacion": 
        #     {
        #         "pob":"Poblacion_Maternal",
        #         "cant" : "Maternales"
        #     },
        # "jardinesYpoblacion":
        #     {
        #         "pob":"Poblacion_Jardin",
        #         "cant" :"Jardines"
        #     },
        "primariasYpoblacion":
            {
                "pob": "Poblacion_Primaria",
                "cant": "Primarios"
            },
        "secundariasYpoblacion":
            {
                "pob": "Poblacion_Secundaria",
                "cant": "Secundarios"
            },
        "secuInetYpoblacion":
            {
                "pob":"Poblacion_Secundaria_Inet",
                "cant":"SecundariosInet"
            },
        "snuYpoblacion":
            {
                "pob":"Poblacion_Terciaria_Joven",
                "cant": "SNUs"                
            },
        "snuInetYpoblacion":
            {
                "pob":"Poblacion_Terciaria_Mayor",
                "cant":"SNUsInet"
            }
        }



    
consultaPrimerJoin =    """
                            SELECT 
                                m.*,
                                j.Jardines,
                                j.Poblacion_Jardin
                            FROM maternalesYpoblacion AS m
                            INNER JOIN jardinesYpoblacion AS j
                            ON m.Departamento = j.Departamento AND m.Provincia = j.Provincia
                        """
    
uniones = dd.sql(consultaPrimerJoin).df()
    
for k,v in diccJ.items():
    #Sin estos reemplazos sintacticos, el codigo se rompe.

    pob = v["pob"]
    cant = v["cant"]
    
    consulta = f"""
        SELECT
            uniones.*,
            {k}.{cant},
            {k}.{pob}
        FROM uniones
        INNER JOIN {k}
        ON uniones.Departamento = {k}.Departamento AND uniones.Provincia = {k}.Provincia
        """
    
    uniones=dd.sql(consulta).df()

#%% Resultado P2
consultaTotalEmpleados = """
                            SELECT DISTINCT Provincia, Departamento, COUNT(Empleo) AS 'Cantidad total de empleados en 2022'
                            FROM deptos_actividad_genero
                            GROUP BY Provincia, Departamento
                            ORDER BY Provincia ASC, "Cantidad total de empleados en 2022" DESC;
                            """
                            
empleados_por_departamento = dd.sql(consultaTotalEmpleados).df()

#%% Ejercicio 3

ee = pd.read_excel("2022_padron_oficial_establecimientos_educativos.xlsx", 
                                 skiprows=6, usecols= columnas_ee)

"""Explicación de la consulta:
    Obtenemos la cantidad de establecimientos educativos comunes por departamento.
    - Borramos espacios en los extremos TRIM.
    - Los numeros de la columna son Chars así que los convertimos, si no puede hacerlo devuelve null.
    - COALESCE reemplaza nulls por 0.
"""

provincias = normalizarColumna("Jurisdicción")
deptos = normalizarColumna("Departamento")
consultaTotalEE =   f"""
                    SELECT DISTINCT 
                        {provincias} AS Provincia,
                        {deptos} AS Departamento,
                        SUM(COALESCE(TRY_CAST(TRIM(Común) AS DOUBLE),0)) AS Cant_EE
                    FROM ee
                    GROUP BY Provincia, Departamento;
                    """
total_establicimientos_departamento = dd.sql(consultaTotalEE).df()


consultaCantEmpresasExpMujeres =    """
                                    SELECT
                                        Provincia,
                                        Departamento,
                                        SUM(Exportadoras) AS Cant_Expo_Mujeres
                                    FROM deptos_actividad_genero
                                    WHERE Genero = 'MUJERES'
                                    GROUP BY Provincia, Departamento;
                                    """
df_cant_expo_mujeres = dd.sql(consultaCantEmpresasExpMujeres).df()

"""
Entonces tengo las tablas de cantidad de empresas exportadoras que emplean mujeres, el total de establecimientos educativos comunes
y me falta la poblacion total por departamento.

Piden que la tabla se vea:
Provincia | Departamento | Cant_Expo_Mujeres | Cant_EE | Población
"""

consultaJoin =  """
                SELECT 
                    m.Provincia,
                    m.Departamento,
                    m.Cant_Expo_Mujeres,
                    e.Cant_EE
                FROM df_cant_expo_mujeres AS m
                INNER JOIN total_establicimientos_departamento AS e
                ON m.Provincia = e.Provincia AND m.Departamento = e.Departamento;
                """
df_punto3 = dd.sql(consultaJoin).df()

consultaPobDeptos = """
                    SELECT
                        Cod_Departamento,
                        Departamento,
                        SUM(Casos) AS Poblacion
                    FROM padron_pob_limpio
                    GROUP BY Cod_Departamento, Departamento
                    """

df_pob_deptos = dd.sql(consultaPobDeptos).df()

# Tengo que añadirle a esta tabla la columna de provincias para hacer el join con el df_punto3

consultaAgregoProv = """
SELECT
    dp.Provincia,
    d.Departamento,
    d.Poblacion
FROM df_pob_deptos AS d
INNER JOIN (
    SELECT
        d.Cod_Departamento,
        p.Provincia
    FROM tabla_deptos AS d
    INNER JOIN tabla_provincias AS p
    ON d.Id_Provincia = p.Id_provincia) AS dp
ON d.Cod_Departamento = dp.Cod_Departamento
"""

df_pob_deptos = dd.sql(consultaAgregoProv).df()

#Termino de hacer el join final

consultaJoin = """
SELECT
    p.*,
    d.Poblacion
FROM df_punto3 AS p
INNER JOIN df_pob_deptos AS d
ON d.Provincia = p.Provincia AND d.Departamento = p.Departamento
"""

df_punto3 = dd.sql(consultaJoin).df()

#%% Punto 4 - Filtro de Deptos con cant_empleados > cant_empleos_provincia


consultaPromedio = """
SELECT
    Provincia,
    AVG(Empleo) AS Promedio_Empleos
FROM deptos_actividad_genero
GROUP BY Provincia
"""

consultaEmpleadosPorDepto = """
SELECT
    Provincia,
    Departamento,
    SUM(Empleo) AS Empleos
FROM deptos_actividad_genero
GROUP BY Provincia, Departamento
"""

consultaClae3 = """
SELECT
    Provincia,
    Departamento,
    LEFT(LPAD(CAST(clae6 AS VARCHAR), 6, '0'), 3) AS CLAE3,
    Empleo
FROM deptos_actividad_genero
"""

sumaEmpleosClae3 = f"""
SELECT
    Provincia,
    Departamento,
    CLAE3,
    SUM(Empleo) AS Empleos
FROM ({consultaClae3})
GROUP BY Provincia, Departamento, CLAE3
"""

consultaMaximosClae3PorDepto = f"""
SELECT
    Provincia,
    Departamento,
    MAX(Empleos) AS Empleos
FROM ({sumaEmpleosClae3})
GROUP BY Provincia, Departamento
"""

consulta = f"""
SELECT
    d.Provincia,
    d.Departamento,
    d.CLAE3,
    d.Empleos
FROM ({sumaEmpleosClae3}) AS d
INNER JOIN ({consultaMaximosClae3PorDepto}) AS m
ON d.Provincia = m.Provincia AND d.Departamento = m.Departamento AND d.Empleos = m.Empleos
INNER JOIN ({consultaPromedio}) AS p
ON d.Provincia = p.Provincia
INNER JOIN ({consultaEmpleadosPorDepto}) AS e
ON d.Provincia = e.Provincia AND d.Departamento = e.Departamento
WHERE e.Empleos > p.Promedio_Empleos
"""

df_punto4 = dd.sql(consulta).df()

# Con esta consulta podria haber dos CLAE3 con el mismo maximo desempato con el clae minimo
consulta = """
SELECT
    Provincia,
    Departamento,
    MIN(CLAE3) AS CLAE3,
    Empleos
FROM df_punto4
GROUP BY Provincia, Departamento, Empleos
""" 

df_punto4 = dd.sql(consulta).df()

#%% Vizualizacion P1

# Empleados por provincia
consulta = """
SELECT 
    Provincia,
    SUM(Empleo) AS Empleados
FROM deptos_actividad_genero
GROUP BY Provincia
ORDER BY SUM(Empleo) DESC
"""

df_empleados_provincia = dd.sql(consulta).df()

plt.figure(figsize=(10,6))
plt.bar(df_empleados_provincia['Provincia'], df_empleados_provincia['Empleados'])
plt.xticks(rotation=90)  
plt.xlabel("Provincia")
plt.ylabel("Cantidad de empleados (2022)")
plt.title("Cantidad de empleados por provincia en 2022")

#%% Armado del dataFrame agrupado para el P2

df_visualizar = uniones

niveles = ["Maternales", "Jardines", "Primarios", "Secundarios", "SecundariosInet", "SNUs_Joven", "SNUs_Mayor","SNUsInet_Joven", "SNUsInet_Mayor" ]
ee_cols = ["Maternales", "Jardines", "Primarios", "Secundarios", "SecundariosInet", "SNUs", "SNUs", "SNUsInet", "SNUsInet" ]
pop_cols = ["Poblacion_Maternal", "Poblacion_Jardin", "Poblacion_Primaria", "Poblacion_Secundaria", "Poblacion_Secundaria_Inet", "Poblacion_Terciaria_Joven", "Poblacion_Terciaria_Mayor", "Poblacion_Terciaria_Joven", "Poblacion_Terciaria_Mayor"  ]

df_agrupado = pd.DataFrame()

for i in range(len(niveles)):
    nivel = niveles[i]
    ee_col = ee_cols[i]
    pop_col = pop_cols[i]

    temp = df_visualizar[["Departamento", "Provincia", ee_col, pop_col]].copy()
    temp.columns = ["Departamento", "Provincia", "CantidadEE", "PoblacionGrupoEtario"]
    temp["NivelEducativo"] = nivel

    df_agrupado = pd.concat([df_agrupado, temp], ignore_index=True)
    
#%% Visualizacion del P2

plt.figure(figsize=(12,7))
sns.scatterplot(
    data=df_agrupado,
    x="PoblacionGrupoEtario",
    y="CantidadEE",
    hue="NivelEducativo",       # colores por nivel
    palette="tab10",
    alpha=0.6,
    s=80                        # tamaño de los puntos
)

plt.xscale("log")
# Etiquetas y título
plt.xlabel("Población del grupo etario (escala log)")
plt.ylabel("Cantidad de EE")
plt.title("Relación entre población y cantidad de EE por nivel educativo")


plt.tight_layout()
plt.show()

#%% P3 - filtro cantidad de EE por departamento y provincia y grafico
#datos
consulta = """
SELECT
    Provincia,
    Departamento,
    COUNT(Departamento) AS Cant_EE
FROM Establecimientos
GROUP BY Provincia, Departamento
ORDER BY Provincia ASC
"""

df_p3 = dd.sql(consulta).df()

#orden
consultaMedianas ="""
SELECT
    Provincia,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Cant_EE) AS Mediana
FROM df_p3
GROUP BY Provincia
ORDER BY Mediana ASC
"""

ordenProvincias = dd.sql(consultaMedianas).df()

plt.figure(figsize=(12,6))
sns.boxplot(x='Provincia', y='Cant_EE', data=df_p3, order=ordenProvincias['Provincia'].tolist())
plt.xticks(rotation=90)
plt.title('BoxPlot de cantidad de establecimientos educativos por departamento por provincia.')


#%% P4 - Relación entre la cantidad de empleados cada mil habitantes (para 2022) y de EE cada mil habitantes por departamento.

# df_pob_deptos tiene las poblaciones totales por depto

# Filtro cantidad de empleados por depto
consultaCantEmpleados = """
SELECT
    Provincia,
    Departamento,
    SUM(Empleo) AS Empleados
FROM deptos_actividad_genero
GROUP BY Provincia, Departamento
"""
df_cant_empleados = dd.sql(consultaCantEmpleados).df()

consultaEmpleadosX1000 = """
SELECT
    e.Provincia,
    e.Departamento,
    (e.Empleados / p.Poblacion) * 1000 AS EmpleadosX1000
FROM df_cant_empleados AS e
INNER JOIN df_pob_deptos AS p
ON e.Provincia = p.Provincia AND e.Departamento = p.Departamento
"""

df_empleados_mil = dd.sql(consultaEmpleadosX1000).df()

# busco EE por mil habitantes

consultaCantEE = """
SELECT
    Provincia,
    Departamento,
    COUNT(Departamento) AS Cant_EE
FROM Establecimientos
GROUP BY Provincia, Departamento
"""

df_cant_ee = dd.sql(consultaCantEE).df()

consultaEEX1000 = """
SELECT
    e.Provincia,
    e.Departamento,
    (e.Cant_EE / p.Poblacion) * 1000 AS CantEEX1000
FROM df_cant_ee AS e
INNER JOIN df_pob_deptos AS p
ON e.Provincia = p.Provincia AND e.Departamento = p.Departamento
"""

df_ee_mil = dd.sql(consultaEEX1000).df()

# df final para hacer scatter plot
consulta = """
SELECT
    ee.Provincia AS Provincia,
    ee.CantEEX1000,
    em.EmpleadosX1000
FROM df_ee_mil AS ee
INNER JOIN df_empleados_mil AS em
ON ee.Provincia = em.Provincia AND ee.Departamento = em.Departamento
ORDER BY Provincia ASC
"""

df_p4 = dd.sql(consulta).df()
#%% P4 - Visualizar con Scatter Plot

plt.figure(figsize=(10,6))
sns.scatterplot(
    data=df_p4,
    x='EmpleadosX1000',
    y='CantEEX1000',
    hue='Provincia',
    palette='tab20',
    s=30,
    alpha=0.5)


plt.xlabel('Empleados cada 1000 habitantes')
plt.ylabel('EE cada 1000 habitantes')
plt.title('Relación entre empleo y establecimientos educativos por departamento')
plt.grid(alpha=0.3)

plt.legend(
    title='Provincia',
    bbox_to_anchor=(1.05, 1),
    loc='upper left',
    fontsize=7
)

plt.tight_layout()
plt.show()


#%% P5 -Las 5 actividades (CLAE6) con mayor y menor proporción (respectivamente) 
# de empleadas mujeres, para 2022. Incluir en el gráfico la proporción promedio de empleo femenino.

consulta = """
SELECT
    d.clae6,
    SUM(d.Empleo) / t.Total AS Proporcion_Mujeres
FROM deptos_actividad_genero AS d
JOIN (SELECT
        SUM(Empleo) AS Total
    FROM deptos_actividad_genero
    WHERE Genero='MUJERES') AS t
ON 1=1
WHERE d.Genero = 'MUJERES'
GROUP BY clae6, t.Total
ORDER BY Proporcion_Mujeres DESC
"""


df_proporcion_m = dd.sql(consulta).df()


consultaTops = """
(
    SELECT * FROM df_proporcion_m
    ORDER BY Proporcion_Mujeres DESC
    LIMIT 5
)
UNION ALL
(
    SELECT * FROM df_proporcion_m
    ORDER BY Proporcion_Mujeres ASC
    LIMIT 5
)
"""

df_p5 = dd.sql(consultaTops).df()

#lo ordeno
consultaOrdenar = """
SELECT *
FROM df_p5
ORDER BY Proporcion_Mujeres ASC
"""
df_p5 = dd.sql(consultaOrdenar).df()

#Busco la proporcion promedio total: empleos mujeres / empleos totales

consultaEmpleosMujer = """
SELECT
    SUM(Empleo) AS Empleos_Mujer
FROM deptos_actividad_genero
WHERE Genero = 'MUJERES'
"""

consultaTotalEmpleos = """
SELECT SUM(Empleo) AS Empleos_Totales
FROM deptos_actividad_genero
"""

consultaPromedioProporcion = f"""
SELECT e.Empleos_Mujer / t.Empleos_Totales AS Proporcion_Promedio
FROM ({consultaEmpleosMujer}) AS e, ({consultaTotalEmpleos}) AS t
"""

prop_prom = dd.sql(consultaPromedioProporcion).df().iloc[0,0]
prop_prom = round(prop_prom, 4)

#%% P5 - Visualizo con grafico de barras

df_p5 = df_p5.sort_values(by='Proporcion_Mujeres', ascending=False)


plt.figure(figsize=(10,6))

sns.barplot(
    data=df_p5,
    x='clae6',
    y='Proporcion_Mujeres',
    palette='viridis',
    order=df_p5['clae6'].tolist()
)
plt.yscale('log')
# línea horizontal del promedio global
plt.axhline(prop_prom, linestyle='--', linewidth=2)

plt.title('Actividades con mayor y menor proporción de empleo femenino (2022)')
plt.xlabel('CLAE6')
plt.ylabel('Proporción de empleo femenino')
plt.tight_layout()
plt.show()



#%% Conclusion - numero de EE es proporcional al numero de EP
consultaEE = """
SELECT
    Provincia,
    Departamento,
    COUNT(Departamento) AS Cant_EE
FROM Establecimientos
GROUP BY Provincia, Departamento
"""
df_ee = dd.sql(consultaEE).df()

consultaEP = """
SELECT
    d.Provincia,
    d.Departamento,
    SUM(m.Establecimientos) AS Cant_EP
FROM deptos_actividad_genero AS d
INNER JOIN (SELECT Provincia, Departamento, MAX(Establecimientos) AS Establecimientos
    FROM deptos_actividad_genero
    GROUP BY Provincia, Departamento) AS m
ON d.Provincia = m.Provincia AND d.Departamento = m.Departamento
GROUP BY d.Provincia, d.Departamento
"""
df_ep = dd.sql(consultaEP).df()



consultaJoin = """
SELECT 
    ee.Provincia,
    ee.Departamento,
    ee.Cant_EE,
    ep.Cant_EP
FROM df_ee AS ee
INNER JOIN df_ep AS ep
ON ee.Provincia = ep.Provincia AND ee.Departamento = ep.Departamento
"""

est_ee_ep = dd.sql(consultaJoin).df()

#%% Visualizo con scatter plot

plt.figure(figsize=(10,6))
sns.scatterplot(
    data=est_ee_ep,
    x='Cant_EE',
    y='Cant_EP',
    hue='Provincia',
    palette='tab20',
    s=30,
    alpha=0.5)

plt.yscale('log')
plt.xlabel('Cantidad de Establecimientos Educativos')
plt.ylabel('Cantidad de Establecimientos Productivos')
plt.title('Relación entre Establecimientos Educativos y Establecimienntos Productivos por departamento')
plt.grid(alpha=0.3)

plt.legend(
    title='Provincia',
    bbox_to_anchor=(1.05, 1),
    loc='upper left',
    fontsize=7
)

plt.tight_layout()
plt.show()




#%% Seria mejor vizualizar sin outliers (Se observan muchos por Cant_EP)

def visualizarScatterPlotSinKOutliers(k:int):
    consultaOutliers = f"""
    SELECT *
    FROM est_ee_ep
    ORDER BY Cant_EP DESC
    LIMIT {k}
    """
    outliers = dd.sql(consultaOutliers).df()
    
    
    consultaSacar = """
    SELECT * 
    FROM est_ee_ep
    EXCEPT
    SELECT *
    FROM outliers
    """
    
    est_ee_ep = dd.sql(consultaSacar).df()
    plt.figure(figsize=(10,6))
    sns.scatterplot(
        data=est_ee_ep,
        x='Cant_EE',
        y='Cant_EP',
        hue='Provincia',
        palette='tab20',
        s=30,
        alpha=0.5)
    
    plt.xlabel('Cantidad de Establecimientos Educativos')
    plt.ylabel('Cantidad de Establecimientos Productivos')
    plt.title(f'Relación entre Establecimientos Educativos y Establecimienntos Productivos por departamento sin {k} outliers')
    plt.grid(alpha=0.3)
    
    plt.legend(
        title='Provincia',
        bbox_to_anchor=(1.05, 1),
        loc='upper left',
        fontsize=7
    )
    
    plt.tight_layout()
    plt.show()

for k in range(3,15, 3):
    visualizarScatterPlotSinKOutliers(k)


















