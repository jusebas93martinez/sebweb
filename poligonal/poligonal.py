import pandas as pd
import numpy as np
import math
import os
import django
from django.conf import settings
from django.shortcuts import render

media_root = os.path.join(settings.BASE_DIR, 'media')

# Cargar datos de los archivos CSV utilizando la ruta absoluta
pol_file = os.path.join(media_root, 'pol.csv')
bases_file = os.path.join(media_root, 'bases.csv')

pol_data = pd.read_csv(pol_file, sep=',')
bases_data = pd.read_csv(bases_file, sep=',')

# Corregir los valores cercanos a cero en el ángulo horizontal
pol_data['angulo_horizontal'] = pol_data['angulo_horizontal'].apply(lambda x: 0 if abs(x) < 0.001 or abs(x-360) < 0.001 else x)

# Calcular la sumatoria de los ángulos horizontales
suma_angulos = pol_data['angulo_horizontal'].sum()

num_vertices = len(pol_data['id'].unique())

# Calcular la suma teórica para ángulos externos
suma_teorica_externa = (num_vertices - 2) * 180
# Calcular la suma teórica para ángulos internos
suma_teorica_interna = (num_vertices + 2) * 180

def determinar_tipo_angulos(pol_data):

    # Calcular las diferencias
    diferencia_externa = abs(suma_angulos - suma_teorica_externa)
    diferencia_interna = abs(suma_angulos - suma_teorica_interna)

    # Comparar las diferencias y determinar si son ángulos internos o externos
    if diferencia_externa < diferencia_interna:
        tipo_angulos = 'externos'
    else:
        tipo_angulos = 'internos'

    return tipo_angulos

tipo_angulos = determinar_tipo_angulos(pol_data)
if tipo_angulos == 'internso':
    error_total = suma_teorica_externa - suma_angulos
else:
    error_total = suma_teorica_interna -suma_angulos 

suma_teorica = determinar_tipo_angulos(pol_data)
if tipo_angulos == 'internso':
    suma_teorica = suma_teorica_externa
else:
    suma_teorica = suma_teorica_interna

error_angular = error_total / num_vertices

pol_data['angulo_horizontal'] = np.where(pol_data['angulo_horizontal'] != 0, pol_data['angulo_horizontal'] + error_angular, pol_data['angulo_horizontal'])

# CALCULO DE AZIMUTS

coordenadas_bases = bases_data[['este', 'norte']].values.tolist()

Cor_arm = coordenadas_bases[0]
Cor_vis = coordenadas_bases[1]

este2, norte2 = Cor_vis
este1, norte1 = Cor_arm

dx = este2 - este1
dy = norte2 - norte1

rumbo_rad = np.arctan2(dx, dy)
rumbo_deg = math.degrees(rumbo_rad)

def validar_rumbo(rumbo_deg):
    if rumbo_deg >= 0 and rumbo_deg < 90:
        return "Nor-Este"
    elif rumbo_deg >= 90 and rumbo_deg < 180:
        return "Sur-Este"
    elif rumbo_deg >= 180 and rumbo_deg < 270:
        return "Sur-Oeste"
    elif rumbo_deg >= 270 and rumbo_deg < 360:
        return "Nor-Oeste"
    else:
        return "Rumbo inválido"
    
direccion = validar_rumbo(rumbo_deg)

def calcular_azimut(rumbo_deg):
    direccion = validar_rumbo(rumbo_deg)

    if direccion == "Nor-Este":
        azimut = rumbo_deg
    elif direccion == "Sur-Este":
        azimut = rumbo_deg + 90
    elif direccion == "Sur-Oeste":
        azimut = rumbo_deg + 180
    elif direccion == "Nor-Oeste":
        azimut = 360 - rumbo_deg
    else:
        azimut = None
    return azimut

azimut = calcular_azimut(rumbo_deg)

azimut1 = pol_data.loc[1, 'angulo_horizontal'] + azimut
if azimut1 >= 360:
    azimut1 -= 360
else:
    pol_data.loc[1, 'angulo_horizontal'] += azimut

suma_total = 0
resultados = []
iniciar_suma = False

for i in range(len(pol_data['angulo_horizontal'])):
    angulo_actual = pol_data['angulo_horizontal'][i]
    
    if angulo_actual != 0:
        if angulo_actual == azimut1:  # Si el valor actual es igual a azimut1, se mantiene sin cambios
            suma_total = azimut1
        else:
            suma_total += angulo_actual

            if suma_total >= 540:
                suma_total -= 540
            elif suma_total >= 180:
                suma_total -= 180
            elif suma_total < 180:
                suma_total += 180
        
        resultados.append(suma_total)

pol_data = pol_data[pol_data['angulo_horizontal'] != 0]

pol_data = pol_data.assign(azimuts=resultados)

# Convierte los ángulos a radianes y calcula el producto con 'dis_h'
pol_data['proy_y'] = pol_data['dis_h'] * pol_data['azimuts'].apply(lambda x: math.cos(math.radians(x)))

# Convierte los ángulos a radianes y calcula el producto con 'dis_h'
pol_data['proy_x'] = pol_data['dis_h'] * pol_data['azimuts'].apply(lambda x: math.sin(math.radians(x)))

suma_totaly = pol_data['proy_y'].sum()
suma_totalx = pol_data['proy_x'].sum()
suma_dish = pol_data['dis_h'].sum()

hip = math.sqrt(suma_totaly**2 + suma_totalx**2)

precision = suma_dish / hip

CorrY = suma_totaly / suma_dish
CorrX = suma_totalx / suma_dish

pol_data['correcionY'] = pol_data['dis_h'] * CorrY
pol_data['correcionX'] = pol_data['dis_h'] * CorrX


# Coordenadas de partida
baseY = bases_data['norte'][0]
baseX = bases_data['este'][0]

# Suma de las proyecciones y correcciones
pol_data['ProN'] = pol_data['correcionY'] + pol_data['proy_y']
pol_data['ProE'] = pol_data['correcionX'] + pol_data['proy_x']

# Cálculo de las coordenadas absolutas
coordenadas_absolutas = []
coordenada_actual = (baseX, baseY)
for index, row in pol_data.iterrows():
    # Obtener las proyecciones de la fila actual
    proyeccion_norte = row['ProN']
    proyeccion_este = row['ProE']
    
    # Calcular la coordenada absoluta sumando las proyecciones a la coordenada actual
    coordenada_actual = (coordenada_actual[0] + proyeccion_este, coordenada_actual[1] + proyeccion_norte)
    
    # Agregar la coordenada absoluta a la lista
    coordenadas_absolutas.append(coordenada_actual)

# Agregar las coordenadas absolutas al DataFrame pol_data
pol_data['Coordenadas'] = coordenadas_absolutas

# Definir listas para almacenar las coordenadas de norte y este
norte = []
este = []

# Recorrer cada fila del dataframe
for index, row in pol_data.iterrows():
    # Extraer las coordenadas de la fila actual
    coordenadas = row['Coordenadas']
    
    # Obtener los valores de norte y este de la tupla de coordenadas
    norte.append(coordenadas[1])
    este.append(coordenadas[0])

pol_data['Norte'] = norte
pol_data['Este'] = este

# Calcular alturas - con angulo vertical y dist inclinada 
pol_data['Corr_H'] = (pol_data['Dis_inc'] * pol_data['angulo_vertical'].apply(lambda x: math.cos(math.radians(x)))) - pol_data['baston'] + pol_data['alt_isn']

suma_erroh = pol_data['Corr_H'].sum()
CorrH = suma_erroh / suma_dish
pol_data['correcionH'] = pol_data['dis_h'] * CorrH

pol_data['correcionH'] =  pol_data['correcionH'] + pol_data['Corr_H']

baseZ = bases_data['altura'][0]

cota = []
cota_actual = baseZ

for index, row in pol_data.iterrows():
    proyeccion_alt = row['correcionH']
    cota_actual += proyeccion_alt
    cota.append(cota_actual)

pol_data['Cota'] = cota


print(pol_data['id'])
print(pol_data['visado'])

for index, row in pol_data.iterrows():
    norte = row['Norte']
    este = row['Este']
    cota = row['Cota']