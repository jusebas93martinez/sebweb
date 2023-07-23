from django.shortcuts import render
import numpy as np
import math

def calcular_azimut(request):
    if request.method == 'POST':
        norte1 = float(request.POST.get('norte1'))
        este1 = float(request.POST.get('este1'))
        norte2 = float(request.POST.get('norte2'))
        este2 = float(request.POST.get('este2'))

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

        distancia = math.sqrt(dx ** 2 + dy ** 2)

        return render(request, 'resultado_azimut.html', {'azimut': azimut, 'distancia': distancia})

    return render(request, 'formulario_azimut.html')