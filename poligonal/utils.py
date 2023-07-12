import pandas as pd
import numpy as np
import math
import os
from django.db import models
from django.conf import settings

def procesar_archivos():

    pol_file = 'media/pol.csv'
    bases_file = 'media/bases.csv'
    # Cargar datos de los archivos CSV
    pol_data = pd.read_csv(pol_file, sep=',')
    bases_data = pd.read_csv(bases_file, sep=',')
    # Corregir los valores cercanos a cero en el ángulo horizontal
    pol_data['angulo_horizontal'] = pol_data['angulo_horizontal'].apply(lambda x: 0 if abs(x) < 0.001 or abs(x-360) < 0.001 else x)

    def convertir_a_grados_minutos_segundos(angulo):
        grados = int(angulo)
        minutos_decimal = (angulo - grados) * 60
        minutos = int(minutos_decimal)
        segundos = math.ceil((minutos_decimal - minutos) * 60)
        return grados, minutos, segundos

    pol_data['angulos_horizontales_iniciales'] = ""

    for index, row in pol_data.iterrows():
        angulo_horizontal = row['angulo_horizontal']
        grados, minutos, segundos = convertir_a_grados_minutos_segundos(angulo_horizontal)
        angulo_completo = f"{grados}° {minutos}' {segundos}\""
        pol_data.at[index, 'angulos_horizontales_iniciales'] = angulo_completo

    pol_data['angulos_verticales_iniciales'] = ""

    for index, row in pol_data.iterrows():
        angulo_vertical = row['angulo_vertical']
        grados, minutos, segundos = convertir_a_grados_minutos_segundos(angulo_vertical)
        angulo_completo = f"{grados}° {minutos}' {segundos}\""
        pol_data.at[index, 'angulos_vertical_iniciales'] = angulo_completo

    # Calcular la sumatoria de los ángulos horizontales
    suma_angulos = pol_data['angulo_horizontal'].sum()

    grados, minutos, segundos = convertir_a_grados_minutos_segundos(suma_angulos)
    suma_angular = f"{grados}° {minutos}' {segundos}\""


    visado = pol_data['visado']

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
        if diferencia_externa > diferencia_interna:
            tipo_angulos = 'externos'
        else:
            tipo_angulos = 'internos'

        return tipo_angulos

    tipo_angulos = determinar_tipo_angulos(pol_data)
    if tipo_angulos == 'internos':
        error_total = suma_teorica_externa - suma_angulos
    else:
        error_total = suma_teorica_interna -suma_angulos 

    suma_teorica = determinar_tipo_angulos(pol_data)

    if tipo_angulos == 'Internos':
        suma_teorica = suma_teorica_externa
    else:
        suma_teorica = suma_teorica_interna
    
    grados, minutos, segundos = convertir_a_grados_minutos_segundos(suma_teorica)
    suma_teorica_a = f"{grados}° {minutos}' {segundos}\""

    error_angular = error_total / num_vertices

    grados = int(error_total)
    minutos = int((error_total - grados) * 60)
    segundos = round(((error_total - grados) * 60 - minutos) * 60)
    error_cierre_ang = f"{grados}° {minutos}' {segundos}\""

    pol_data['angulo_horizontal'] = np.where(pol_data['angulo_horizontal'] != 0, pol_data['angulo_horizontal'] + error_angular, pol_data['angulo_horizontal'])

    pol_data['anguloh_corr'] = ""

    for index, row in pol_data.iterrows():
        angulo_hc = row['angulo_horizontal']
        grados, minutos, segundos = convertir_a_grados_minutos_segundos(angulo_hc)
        angulo_ok = f"{grados}° {minutos}' {segundos}\""
        pol_data.at[index, 'anguloh_corr'] = angulo_ok

    # CALCULO DE AZIMUTS

    coordenadas_bases = bases_data[['este', 'norte']].values.tolist()

    Cor_arm = coordenadas_bases[0]
    Cor_vis = coordenadas_bases[1]

    este2, norte2 = Cor_vis
    este1, norte1 = Cor_arm

    dx = este2 - este1
    dy = norte2 - norte1

    rumbo_rad = math.atan(dx / dy)
    rumbo_deg = abs(rumbo_rad * 180 / math.pi)

    def validar_rumbo(dy, dx):
        if dy > 0 and dx > 0:
            return "Nor-Este"
        elif dy < 0 and dx < 0:
            return "Sur-Oeste"
        elif dy < 0 and dx > 0:
            return "Sur-Este"
        elif dy > 0 and dx < 0:
            return "Nor-Oeste"
        else:
            return "Rumbo inválido"

    def calcular_azimut(rumbo_deg):
        direccion = validar_rumbo(dy,dx)

        if direccion == "Nor-Este":
            azimut = rumbo_deg
        elif direccion == "Sur-Este":
            azimut = 180 - rumbo_deg
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
        angulo_actual = pol_data['angulo_horizontal'].iloc[i]
        
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

    pol_data['az'] = ""

    for index, row in pol_data.iterrows():
              azimuts = row['azimuts']
              grados, minutos, segundos = convertir_a_grados_minutos_segundos(azimuts)
              azz = f"{grados}° {minutos}' {segundos}\""
              pol_data.at[index, 'az'] = azz   

    suma_dish = pol_data['dis_h'].sum()

    # Convierte los ángulos a radianes y calcula el producto con 'dis_h'
    pol_data['proy_y'] = pol_data['dis_h'] * pol_data['azimuts'].apply(lambda x: math.cos(math.radians(x)))

    # Convierte los ángulos a radianes y calcula el producto con 'dis_h'
    pol_data['proy_x'] = pol_data['dis_h'] * pol_data['azimuts'].apply(lambda x: math.sin(math.radians(x)))

    suma_totaly = pol_data.iloc[:-1]['proy_y'].sum()
    suma_totalx = pol_data.iloc[:-1]['proy_x'].sum()

    suma_totaly1 = pol_data['proy_y'].sum()
    suma_totalx1 = pol_data['proy_x'].sum()

    norte1 = bases_data['norte'].iloc[0] + suma_totaly
    este1 = bases_data['este'].iloc[0] + suma_totalx


    error_norte =  bases_data['norte'].iloc[1] - norte1
    error_este =  bases_data['este'].iloc[1] - este1


    hip = math.sqrt(suma_totaly1**2 + suma_totalx1**2)

    precision = suma_dish / hip

    CorrY = error_norte /  suma_totaly
    CorrX = error_este / suma_totalx


    # Coordenadas de partida
    baseY = bases_data['norte'][0]
    baseX = bases_data['este'][0]

    pol_data['correcionY'] = pol_data['proy_y'] * CorrY
    pol_data['correcionX'] = pol_data['proy_x'] * CorrX

    for index, row in pol_data.iterrows():
        correccionY = row['correcionY']
        correccionX = row['correcionX']
        if correccionY > 0:
            pol_data.at[index, 'proy_y'] += correccionY
        else:
            pol_data.at[index, 'proy_y'] -= abs(correccionY)
        if correccionX > 0:
            pol_data.at[index, 'proy_x'] += correccionX
        else:
            pol_data.at[index, 'proy_x'] -= abs(correccionX)

    cnorte = []
    norte_actual = baseY

    for index, row in pol_data.iterrows():
        proyeccion_nor = row['proy_y']
        norte_actual += proyeccion_nor
        cnorte.append(norte_actual)

    pol_data['norte'] = cnorte

    ceste = []
    este_acual = baseX

    for index, row in pol_data.iterrows():
        proyeccion_est = row['proy_x']
        este_acual += proyeccion_est
        ceste.append(este_acual)

    pol_data['este'] = ceste


    # Calcular alturas - con angulo vertical y dist inclinada 
    pol_data['Corr_H'] = (pol_data['Dis_inc'] * pol_data['angulo_vertical'].apply(lambda x: math.cos(math.radians(x)))) - pol_data['baston'] + pol_data['alt_isn']

    suma_erroh = pol_data.iloc[:-1]['Corr_H'].sum()
    cota1 = bases_data['altura'].iloc[0] + suma_erroh


    error_cota =  bases_data['altura'].iloc[1] - cota1


    CorrZ = error_cota / suma_erroh

    baseZ = bases_data['altura'][0]

    pol_data['correcionZ'] = pol_data['Corr_H'] * CorrZ

    for index, row in pol_data.iterrows():
        correccionY = row['correcionZ']
        if correccionY > 0:
            pol_data.at[index, 'Corr_H'] += correccionY
        else:
            pol_data.at[index, 'Corr_H'] -= abs(correccionY)

    ccota = []
    cota_actual = baseZ

    for index, row in pol_data.iterrows():
        proyeccion_cot = row['Corr_H']
        cota_actual += proyeccion_cot
        ccota.append(cota_actual)

    pol_data['altura'] = ccota

    pol_data['ida'] = pol_data['id']
    pol_data['vis'] = pol_data['visado']
    pol_data['id'] = pol_data['visado']


    # Obtener las columnas requeridas de bases_data
    bases_subset = bases_data[['id', 'norte', 'este', 'altura']]

    # Obtener las columnas requeridas de pol_data
    pol_subset = pol_data[['id', 'norte', 'este', 'altura']]

    # Concatenar los subconjuntos en un nuevo DataFrame
    df_nuevo = pd.concat([bases_subset[::-1], pol_subset[:-1]], ignore_index=True)

    df_nuevo  = df_nuevo.dropna()
    df_nuevo = df_nuevo.reset_index(drop=True)

    resultados = pol_data.to_dict(orient='records')
    coor_arran = bases_data.to_dict(orient='records')
    coordenadas = df_nuevo.to_dict(orient='records')

    print(['id'])

    datos = {
        'coordenadas':coordenadas,
        'arranque': coor_arran,
        'resultados': resultados,
        'tipo_angulos': tipo_angulos,
        'dist_pol': suma_dish,
        'suma_teorica': suma_teorica_a,
        'suma_angular': suma_angular,
        'error_cierre':error_cierre_ang,
        'precision': precision,
        'error_angular': error_angular,
        'num_vertices': num_vertices,
        'suma_angulos': suma_angulos,
        'error_norte': suma_totaly1,
        'error_este': suma_totalx1,
        'Punto': visado,  
  
    }
    
    return datos

class Visit(models.Model):
    count = models.PositiveIntegerField(default=0)
