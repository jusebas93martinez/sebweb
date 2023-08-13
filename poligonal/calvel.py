import pandas as pd
import math
from geopy.point import Point
import os
import django
from django.conf import settings
from django.shortcuts import render

def calcular_velocidades(lat,lng):

    # Cargar el DataFrame del modelo de velocidades
    vel = os.path.join(settings.MEDIA_ROOT,'vel2017.csv')
    vel = pd.read_csv(vel, sep=',', encoding='utf-8')

    # Coordenadas geográficas para la interpolación
    lat = lat
    lng = lng

    # Crear un objeto Point con las coordenadas ingresadas por el usuario
    user_point = Point(lat, lng)

    # Función para calcular la distancia entre dos puntos en grados
    def calculate_distance_meters(lat1, lng1, lat2, lng2):
        radius = 6371000  # Radio de la Tierra en metros
        distance = (
            radius * math.acos(
                math.cos(math.radians(90 - lat1)) * math.cos(math.radians(90 - lat2)) +
                math.sin(math.radians(90 - lat1)) * math.sin(math.radians(90 - lat2)) * math.cos(math.radians(lng1 - lng2))
            )
        )
        return distance

    # Crear una lista de puntos con atributos y sus distancias al punto del usuario
    points_with_distances = []
    for index, row in vel.iterrows():
        lat_point = row['latitud']
        lng_point = row['longitud']
        comp_n = row['comp_n']
        comp_e = row['comp_e']
        
        # Calcular la distancia al punto del usuario en metros
        distance_meters = calculate_distance_meters(lat, lng, lat_point, lng_point)
        
        # Agregar el punto con atributos y distancia a la lista
        points_with_distances.append((distance_meters, lat_point, lng_point, {'comp_n': comp_n, 'comp_e': comp_e}))

    # Ordenar los puntos por distancia en metros
    points_with_distances.sort(key=lambda x: x[0])

    # Verificar si el punto buscado coincide con alguno en los datos
    matching_point = None
    for distance, lat_point, lng_point, attributes in points_with_distances:
        if lat_point == lat and lng_point == lng:
            matching_point = (distance, lat_point, lng_point, attributes)
            break

    # Si se encontró una coincidencia, usar los valores directamente
    if matching_point:
        interp_comp_n = matching_point[3]['comp_n']
        interp_comp_e = matching_point[3]['comp_e']
    else:
        # Tomar los 4 puntos más cercanos
        nearest_points = points_with_distances[:4]

        # Realizar interpolación ponderada para obtener los valores de comp_n y comp_e en el punto del usuario
        total_weight_comp_n = 0
        total_weight_comp_e = 0
        interp_comp_n = 0
        interp_comp_e = 0

        for distance, _, _, attributes in nearest_points:
            if distance != 0:
                weight = 1 / distance
                total_weight_comp_n += weight
                total_weight_comp_e += weight
                interp_comp_n += attributes['comp_n'] * weight
                interp_comp_e += attributes['comp_e'] * weight

        if total_weight_comp_n != 0:
            interp_comp_n /= total_weight_comp_n
        if total_weight_comp_e != 0:
            interp_comp_e /= total_weight_comp_e

    componente_n = round(interp_comp_n, 4)
    componente_e = round(interp_comp_e, 4)

    # Tiempo en años
    tiempo_anos = 1  # Cambia si deseas calcular el desplazamiento para un período diferente
    # Coordenadas geográficas originales
    lat_original = lat
    lng_original = lng

    # Radio de la Tierra en metros
    radio_tierra = 6378137.0  # Valor para el elipsoide WGS-84

    # Cálculo de las nuevas coordenadas
    nueva_latitud = lat_original + (componente_n * tiempo_anos) / radio_tierra * (180.0 / math.pi)
    nueva_longitud = lng_original + (componente_e * tiempo_anos) / (radio_tierra * math.cos(math.radians(lat_original))) * (180.0 / math.pi)

    # Coordenadas elipsoidales actuales (latitud, longitud, altura)
    lat_actual = math.radians(lat)  # Cambia con el valor correcto en radianes
    lng_actual = math.radians(lng)  # Cambia con el valor correcto en radianes
    altura_actual = 0.0  # Cambia con la altura correcta en metros

    # Coordenadas elipsoidales un año después (latitud, longitud, altura)
    lat_nueva = math.radians(nueva_latitud)  # Cambia con el valor correcto en radianes (calculado anteriormente)
    lng_nueva = math.radians(nueva_longitud)  # Cambia con el valor correcto en radianes (calculado anteriormente)
    altura_nueva = altura_actual  # Suponemos que la altura no cambia significativamente en un año

    # Parámetros del elipsoide WGS-84
    semieje_mayor = 6378137.0  # Semieje mayor del elipsoide en metros
    aplanamiento = 1 / 298.257223563  # Aplanamiento del elipsoide

    # Cálculo de las coordenadas geocéntricas actuales (x, y, z)
    N_actual = semieje_mayor / math.sqrt(1 - (aplanamiento * math.sin(lat_actual))**2)
    x_actual = (N_actual + altura_actual) * math.cos(lat_actual) * math.cos(lng_actual)
    y_actual = (N_actual + altura_actual) * math.cos(lat_actual) * math.sin(lng_actual)
    z_actual = ((1 - aplanamiento)**2 * N_actual + altura_actual) * math.sin(lat_actual)

    # Cálculo de las coordenadas geocéntricas un año después (x, y, z)
    N_nueva = semieje_mayor / math.sqrt(1 - (aplanamiento * math.sin(lat_nueva))**2)
    x_nueva = (N_nueva + altura_nueva) * math.cos(lat_nueva) * math.cos(lng_nueva)
    y_nueva = (N_nueva + altura_nueva) * math.cos(lat_nueva) * math.sin(lng_nueva)
    z_nueva = ((1 - aplanamiento)**2 * N_nueva + altura_nueva) * math.sin(lat_nueva)

    # Calcular la diferencia en coordenadas geocéntricas
    vel_x =round( x_nueva - x_actual,4)
    vel_y =round(y_nueva - y_actual,4)
    vel_z =round( z_nueva - z_actual,4)

    return vel_x, vel_y, vel_z

