import pandas as pd
import numpy as np
import math
import os
import django
from django.conf import settings
from django.shortcuts import render

def pol_cerrada2():
    
    pd.options.display.float_format = '{:.4f}'.format

    pol_file = 'media/pol.csv'
    bases_file = 'media/bases.csv'
    # Cargar datos de los archivos CSV
    pol_data = pd.read_csv(pol_file, sep=',')
    bases_data = pd.read_csv(bases_file, sep=',')

    # Corregir los valores cercanos a cero en el ángulo horizontal
    pol_data['angulo_horizontal'] = pol_data['angulo_horizontal'].apply(lambda x: 0 if abs(x) < 0.001 or abs(x-360) < 0.001 else x)

    filtro = pol_data['angulo_vertical'] < 140
    pol_data = pol_data[filtro]
    visado = pol_data['visado']
    num_vertices = len(pol_data['id'].unique())

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
        
    direccion = validar_rumbo(dy, dx)

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

    azimut0 = calcular_azimut(rumbo_deg)



    azimut1 = pol_data.loc[2, 'angulo_horizontal'] + azimut0
    if azimut1 >= 360:
        azimut1 -= 360
    else:
        pol_data.loc[2, 'angulo_horizontal'] += azimut0

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

    pol_data['az_init'] = ""

    for index, row in pol_data.iterrows():
              azimuts = row['azimuts']
              grados, minutos, segundos = convertir_a_grados_minutos_segundos(azimuts)
              azz = f"{grados}° {minutos}' {segundos}\""
              pol_data.at[index, 'az_init'] = azz   

    # CALCULO DE AZIMUTS DE LLEGADA 

    coordenadas_bases = bases_data[['este', 'norte']].values.tolist()

    Cor_arm = coordenadas_bases[2]
    Cor_vis = coordenadas_bases[3]
    este2, norte2 = Cor_vis
    este1, norte1 = Cor_arm
    dx = este2 - este1
    dy = norte2 - norte1
    rumbo_rad = math.atan(dx / dy)
    rumbo_deg = abs(rumbo_rad * 180 / math.pi)
    direccion = validar_rumbo(dy, dx)
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

    ultimo_azimut = pol_data['azimuts'].iloc[-1]

    error_az = azimut - ultimo_azimut

    az_correction = abs(error_az/ num_vertices)

    grados, minutos, segundos = convertir_a_grados_minutos_segundos(azimut)
    azimut = f"{grados}° {minutos}' {segundos}\""

    grados, minutos, segundos = convertir_a_grados_minutos_segundos(ultimo_azimut)
    ultimo_azimut = f"{grados}° {minutos}' {segundos}\""

    if error_az >= 0:
        pol_data['angulo_horizontal'] = np.where(pol_data['angulo_horizontal'] != 0, pol_data['angulo_horizontal'] + az_correction, pol_data['angulo_horizontal'])
    else:
        pol_data['angulo_horizontal'] = np.where(pol_data['angulo_horizontal'] != 0, pol_data['angulo_horizontal'] - az_correction, pol_data['angulo_horizontal'])

    grados, minutos, segundos = convertir_a_grados_minutos_segundos(error_az)
    error_az = f"{grados}° {minutos}' {segundos}\""



    #----------------------------

    primer_azimut = pol_data['angulo_horizontal'].iloc[0]

    suma_total = 0
    resultados = []
    iniciar_suma = False

    for i in range(len(pol_data['angulo_horizontal'])):
        angulo_actual = pol_data['angulo_horizontal'].iloc[i]
        
        if angulo_actual != 0:
            if angulo_actual == primer_azimut:  # Si el valor actual es igual a azimut1, se mantiene sin cambios
                suma_total = primer_azimut 
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

    pol_data['az_corr'] = ""

    for index, row in pol_data.iterrows():
              azimuts = row['azimuts']
              grados, minutos, segundos = convertir_a_grados_minutos_segundos(azimuts)
              azz = f"{grados}° {minutos}' {segundos}\""
              pol_data.at[index, 'az_corr'] = azz   

    suma_dish = pol_data.iloc[:-1]['dis_h'].sum()

    # Convierte los ángulos a radianes y calcula el producto con 'dis_h'
    pol_data['proy_y'] = pol_data['dis_h'] * pol_data['azimuts'].apply(lambda x: math.cos(math.radians(x)))

    # Convierte los ángulos a radianes y calcula el producto con 'dis_h'
    pol_data['proy_x'] = pol_data['dis_h'] * pol_data['azimuts'].apply(lambda x: math.sin(math.radians(x)))

    suma_totaly = pol_data.iloc[:-1]['proy_y'].sum()
    suma_totalx = pol_data.iloc[:-1]['proy_x'].sum()

    norte1 = bases_data['norte'].iloc[0] + suma_totaly
    este1 = bases_data['este'].iloc[0] + suma_totalx

    error_norte =  bases_data['norte'].iloc[2] - norte1
    error_este =  bases_data['este'].iloc[2] - este1

    hip = math.sqrt(error_norte**2 + error_este**2)

    precision = suma_dish / hip

    CorrY = error_norte / suma_totaly
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
    pol_data['Dist_v'] = ((pol_data['Dis_inc'] * pol_data['angulo_vertical'].apply(lambda x: math.cos(math.radians(x)))) - pol_data['baston']) + pol_data['alt_isn']

    suma_totalz = pol_data.iloc[:-1]['Dist_v'].sum()

    cota1 = bases_data['altura'].iloc[0] + suma_totalz

    error_cota =  bases_data['altura'].iloc[2] - cota1

    CorrZ = error_cota / suma_totalz

    baseZ = bases_data['altura'][0]

    pol_data['correcionZ'] = pol_data['Dist_v'] * CorrZ

    for index, row in pol_data.iterrows():
        correccionY = row['correcionZ']
        if correccionY > 0:
            pol_data.at[index, 'Dist_v'] += correccionY
        else:
            pol_data.at[index, 'Dist_v'] -= abs(correccionY)

    ccota = []
    cota_actual = baseZ

    for index, row in pol_data.iterrows():
        proyeccion_cot = row['Dist_v']
        cota_actual += proyeccion_cot
        ccota.append(cota_actual)

    pol_data['cota'] = ccota

    print(pol_data['cota'])
    
    resultados = pol_data.to_dict(orient='records')
    coor_arran = bases_data.to_dict(orient='records')


    datos = {
    'errorn': error_norte,
    'errore': error_este,
    'arranque': coor_arran,
    'azimut2': ultimo_azimut,
    'err_az': error_az,
    'azimut1': azimut,
    'resultados': resultados,
    'dist_pol': suma_dish,
    'precision': precision,
    'num_vertices': num_vertices,
    'error_norte': suma_totaly,
    'error_este': suma_totalx,
    'Punto': visado,  
    }
    return datos

