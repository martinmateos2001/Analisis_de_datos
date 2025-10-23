#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%


import pandas as pd
import duckdb as dd
import numpy as np

#%%Establecimientos: Data frame de Establecimientos Educativos del padròn del 2022


columnas_ee = 'A:C,L,N,U:AA'
"""
A - Jurisdiccion
B - Cueanexo
C - Nombre
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
consultaSoloComunes = """
                      SELECT *
                      FROM Establecimientos
                      WHERE "Común" = '1';

                      """

Establecimientos = dd.sql(consultaSoloComunes).df()

def upperSinTildes(columna:str)->str:
    
    res = f"""
            REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(UPPER({columna}), 'Á', 'A'),
                            'É', 'E'),
                        'Í', 'I'),
                    'Ó', 'O'),
                'Ú', 'U')
            """
    return res

jur = upperSinTildes("Jurisdicción")
dep = upperSinTildes("Departamento")
#Eliminamos Cueanexo
elimino = f"""
            SELECT 
                REPLACE({jur}, 'CIUDAD DE BUENOS AIRES', 'CABA') as Provincia, 
                REPLACE({dep},'1§ DE MAYO', '1 DE MAYO') as Departamento, 
                "Nivel inicial - Jardín maternal" as Maternal,
                "Nivel inicial - Jardín de infantes" as Jardin, 
                Primario, Secundario,
                "Secundario - INET" as SecuInet, 
                "SNU" as Snu, "SNU - INET" as SnuInet
            FROM Establecimientos;
          """

Establecimientos = dd.sql(elimino).df()

#%% Buscamos la cantidad de establecimientos que hay de cada nivel

def consultarCantNivelesPorDepto(nivel:str, nombreDelCount:str):
    consulta =  f"""
                   SELECT Provincia, Departamento, COUNT({nivel}) as {nombreDelCount}
                   FROM Establecimientos
                   WHERE {nivel} = '1'
                   GROUP BY Departamento, Provincia;
                   """
    return dd.sql(consulta).df()

cant_maternales_depto = consultarCantNivelesPorDepto('Maternal', 'Maternales')
cant_jardin_depto = consultarCantNivelesPorDepto('Jardin', 'Jardines')
cant_primaria_depto = consultarCantNivelesPorDepto('Primario', 'Primarios')
cant_secundaria_depto = consultarCantNivelesPorDepto('Secundario', 'Secundarios')
cant_secuInet_depto = consultarCantNivelesPorDepto("SecuInet", 'SecundariosInet')
cant_snu_depto = consultarCantNivelesPorDepto("Snu", 'SNUs')
cant_snuInet_depto = consultarCantNivelesPorDepto("SnuInet", 'SNUsInet')

#%%padron_poblacional = Datos de poblacion por departamento

padron_poblacional = pd.read_excel("padron_poblacion.xlsX", skiprows=12, header=None)

#las ultimas 4 filas no sirven     
f_malas = []   
i:int() = len(padron_poblacional)-5
while(i < len(padron_poblacional)):     #las ultimas 4
    f_malas.append(i)
    i = i + 1

padron_poblacional.drop(index=f_malas, inplace=True, axis=0)

#Elimino la columna vacia y las filas vacias.
padron_poblacional.dropna(axis=1, how='all', inplace=True)
padron_poblacional.dropna(axis=0, how='all', inplace=True)

#%% padron limpio
padron_pob_limpio = pd.DataFrame(columns=['Cod_Departamento', 'Departamento', 'Edad', 'Casos'])
areas = []
deptos = []
edades = []
casos = []


def limpiarCodArea(area:str):
    sacar = 'AREA #'
    return area.replace(sacar, '')

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

#%% modifico datos para que coincidan con las otras tablas


deptosSinTildes = upperSinTildes("Departamento")
consultaDeptosSinAcentos =  f"""
                                SELECT 
                                    Cod_Departamento,
                                    REPLACE({deptosSinTildes}, '1º DE MAYO', '1 DE MAYO') AS Departamento,
                                    Edad,
                                    Casos
                                FROM padron_pob_limpio
                            """
padron_pob_limpio = dd.sql(consultaDeptosSinAcentos).df()

#%% busco la cantidad de personas que hay respecto a cada nivel educativo
"""
maternal es [0, 2]
infantes es [3, 5]
primaria es [6, 12]
secundaria es [12, 18]
secuInet es [12, 19]
snu y snuInet > 18 años
"""
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
deptos = upperSinTildes("departamento")
provincia = upperSinTildes("provincia")
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
>>>>>>> rama_martin
                        """
tabla_deptos = dd.sql(consultaTablaDeptos).df()

#Resultado P2
consultaTotalEmpleados = """
                            SELECT DISTINCT Provincia, Departamento, COUNT(Empleo) AS 'Cantidad total de empleados en 2022'
                            FROM deptos_actividad_genero
                            GROUP BY Provincia, Departamento
                            ORDER BY Provincia ASC, "Cantidad total de empleados en 2022" DESC;
                            """
                            
empleados_por_departamento = dd.sql(consultaTotalEmpleados).df()
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

pob_maternal_depto = agregarColumnaProvincia("pob_maternal_depto", "Poblacion_Maternal")
pob_jardin_depto = agregarColumnaProvincia("pob_jardin_depto", "Poblacion_Jardin")
pob_primaria_depto = agregarColumnaProvincia("pob_primaria_depto", "Poblacion_Primaria")
pob_secu_depto = agregarColumnaProvincia("pob_secu_depto", "Poblacion_Secundaria")
pob_secuInet_depto = agregarColumnaProvincia("pob_secuInet_depto", "Poblacion_Secundaria_Inet")
pob_terciaria_joven = agregarColumnaProvincia("pob_terciaria_joven", "Poblacion_Terciaria_Joven")
pob_terciaria_mayor = agregarColumnaProvincia("pob_terciaria_mayor", "Poblacion_Terciaria_Mayor")

#%%Join de cant establecimientos por nivel por depto y su poblacion
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

#%% Ejercicio 3

ee = pd.read_excel("2022_padron_oficial_establecimientos_educativos.xlsx", 
                                 skiprows=6, usecols= columnas_ee)

consultaTotalEE =  """
                    SELECT DISTINC Jurisdicción, Departamento, COUNT (Departamento)
                    FROM ee
                    GROUP BY Jurisdicción, Departamento
                    WHERE Común='1'
                    """
total_establicimientos_departamento = dd.sql(consultaTotalEE).df()







