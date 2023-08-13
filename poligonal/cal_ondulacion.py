import numpy as np
import pandas as pd
import os
import django
from django.conf import settings
from django.shortcuts import render

import pandas as pd

def obtener_ondulacion(lat, lng):
    file_path = os.path.join(settings.MEDIA_ROOT, 'gecol2004.csv')
    gecol = pd.read_csv(file_path, sep=',', encoding='utf-8')

    latitud_superior_izquierda = 14.983333
    longitud_superior_izquierda = -79.983333
    resolucion = 0.03333333333333333

    # Limitamos las coordenadas dentro de los límites conocidos
    lat = max(min(lat, latitud_superior_izquierda), -4.983333)
    lng = max(min(lng, -66.016667), longitud_superior_izquierda)

    # Cálculo de los índices de los puntos más cercanos
    fila = int((latitud_superior_izquierda - lat) / resolucion)
    columna = int((lng - longitud_superior_izquierda) / resolucion)

    lat1 = latitud_superior_izquierda - fila * resolucion
    lon1 = longitud_superior_izquierda + columna * resolucion
    lat2 = lat1 - resolucion
    lon2 = lon1 + resolucion

    val1 = gecol.iloc[fila - 1, columna]
    val2 = gecol.iloc[fila - 1, columna + 1]
    val3 = gecol.iloc[fila, columna]
    val4 = gecol.iloc[fila, columna + 1]

    interp_lat = ((lat - lat1) / (lat2 - lat1)) * (val3 - val1) + val1
    interp_lat2 = ((lat - lat1) / (lat2 - lat1)) * (val4 - val2) + val2
    interp_lon = ((lng - lon1) / (lon2 - lon1)) * (interp_lat2 - interp_lat) + interp_lat

    return interp_lon
