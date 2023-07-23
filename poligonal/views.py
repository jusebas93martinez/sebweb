from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import random
import numpy as np
import math
import os
from django.conf import settings
from .utils import procesar_archivos
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import matplotlib
from .poligonal2 import pol_cerrada2
from .poligonal3 import pol_cerrada3
from django.http import JsonResponse
from .cal_ondulacion import obtener_ondulacion


matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker

from django.shortcuts import render, HttpResponseRedirect, reverse
from .utils import procesar_archivos
from .utils import Visit


'''def error_404(request, exception):
    return render(request, '404.html', status=404)'''

def index(request):
    return render(request, 'base.html')

def inicio(request):
        # Obtener el objeto de contador de visitas existente o crear uno nuevo si no existe
    visit, created = Visit.objects.get_or_create(pk=1)
    
    # Incrementar el contador de visitas
    visit.count += 1
    visit.save()

    return render(request, 'inicio.html', {'visit': visit})

def acercade(request):
    return render(request, 'acercade.html')

def contacto(request):
    return render(request, 'contacto.html')

def cargar_archivos_pol_cerrada(request):
    if request.method == 'POST':
        pol_file = request.FILES['pol_file']
        bases_file = request.FILES['bases_file']

        # Guardar los archivos en las rutas especificadas
        with open('media/pol.csv', 'wb') as destination:
            for chunk in pol_file.chunks():
                destination.write(chunk)
        
        with open('media/bases.csv', 'wb') as destination:
            for chunk in bases_file.chunks():
                destination.write(chunk)

        # Redirigir a la vista de procesamiento de archivos
        return HttpResponseRedirect(reverse('procesar_pol_cerrada') + f'?pol_file={pol_file.name}&bases_file={bases_file.name}')
    
    return render(request, 'loadfile.html')
    
def cargar_archivos_pol_cerrada_doble(request):
    if request.method == 'POST':
        pol_file = request.FILES['pol_file']
        bases_file = request.FILES['bases_file']

        # Guardar los archivos en las rutas especificadas
        with open('media/pol.csv', 'wb') as destination:
            for chunk in pol_file.chunks():
                destination.write(chunk)
        
        with open('media/bases.csv', 'wb') as destination:
            for chunk in bases_file.chunks():
                destination.write(chunk)

        # Redirigir a la vista de procesamiento de archivos
        return HttpResponseRedirect(reverse('procesar_poligonal_doble') + f'?pol_file={pol_file.name}&bases_file={bases_file.name}')

    return render(request, 'loadfile_poldoble.html')

def cargar_archivos_pol_cerrada_ex(request):
    if request.method == 'POST':
        pol_file = request.FILES['pol_file']
        bases_file = request.FILES['bases_file']

        # Guardar los archivos en las rutas especificadas
        with open('media/pol.csv', 'wb') as destination:
            for chunk in pol_file.chunks():
                destination.write(chunk)
        
        with open('media/bases.csv', 'wb') as destination:
            for chunk in bases_file.chunks():
                destination.write(chunk)

        # Redirigir a la vista de procesamiento de archivos
        return HttpResponseRedirect(reverse('procesar_pol_ex') + f'?pol_file={pol_file.name}&bases_file={bases_file.name}')

    return render(request, 'loadfile_polex.html')

def procesar_pol(request):
    if request.method == 'GET':
        datos = procesar_archivos()
        return render(request, 'pol_cerrada.html',datos)
    
def procesar_pol_doble(request):
    if request.method == 'GET':
        datos = pol_cerrada2()
        return render(request, 'pol_doble_a.html',datos)
    
def procesar_pol_ex(request):
    if request.method == 'GET':
        datos = pol_cerrada3()
        return render(request, 'pol_cerrada_ex.html',datos)

def generar_grafico1(datos):
    fig, ax = plt.subplots(figsize=(8, 6))
    este_values = [coordenadas['este'] for coordenadas in datos['coordenadas']]
    norte_values = [coordenadas['norte'] for coordenadas in datos['coordenadas']]
    visados_values = [coordenadas['id'] for coordenadas in datos['coordenadas']]
    ax.plot(este_values, norte_values, linestyle='-', color='blue')  # Líneas azules
    ax.plot(este_values, norte_values, marker='o', markersize=5, markerfacecolor='red', markeredgecolor='red')  # Puntos rojos

    ax.fill_between(este_values, norte_values, color='lightblue', alpha=0.3)  # Resaltar el área bajo la curva (sombreado)    

    ax.set_xlabel('Este')
    ax.set_ylabel('Norte')
    ax.set_title('Poligonal Cerrada Brazo Interno')
    ax.grid(True)

    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.yaxis.get_major_formatter().set_scientific(False)
    ax.yaxis.get_major_formatter().set_useOffset(False)

    ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.xaxis.get_major_formatter().set_scientific(False)
    ax.xaxis.get_major_formatter().set_useOffset(False)

    # Agregar etiquetas a los puntos
    for x, y, label in zip(este_values, norte_values, visados_values):
            ax.text(x, y, label, fontsize=10, ha='left', va='bottom')

    # Ajustar límites del eje y
    min_y = min(norte_values)
    max_y = max(norte_values)
    y_margin = (max_y - min_y) * 0.1  # Margen del 10% en la parte superior e inferior
    ax.set_ylim(min_y - y_margin, max_y + y_margin)

    # Ajustar límites del eje x
    min_x = min(este_values)
    max_x = max(este_values)
    x_margin = (max_x - min_x) * 0.1  # Margen del 10% en la parte izquierda y derecha
    ax.set_xlim(min_x - x_margin, max_x + x_margin)

    return fig

def generar_grafico2(datos):
    fig, ax = plt.subplots(figsize=(8, 6))
    este_values = [coordenadas['este'] for coordenadas in datos['coordenadas']]
    norte_values = [coordenadas['norte'] for coordenadas in datos['coordenadas']]
    visados_values = [coordenadas['id'] for coordenadas in datos['coordenadas']]
    ax.plot(este_values, norte_values, linestyle='-', color='blue')  # Líneas azules
    ax.plot(este_values, norte_values, marker='o', markersize=5, markerfacecolor='red', markeredgecolor='red')  # Puntos rojos

    ax.set_xlabel('Este')
    ax.set_ylabel('Norte')
    ax.set_title('Poligonal Abierta con doble punto de apoyo')
    ax.grid(True)

    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.yaxis.get_major_formatter().set_scientific(False)
    ax.yaxis.get_major_formatter().set_useOffset(False)

    ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.xaxis.get_major_formatter().set_scientific(False)
    ax.xaxis.get_major_formatter().set_useOffset(False)

    # Agregar etiquetas a los puntos
    for x, y, label in zip(este_values, norte_values, visados_values):
        ax.text(x, y, label, fontsize=10, ha='left', va='bottom')

    return fig

def generar_grafico3(datos):
    fig, ax = plt.subplots(figsize=(8, 6))
    este_values = [coordenadas['este'] for coordenadas in datos['coordenadas']]
    norte_values = [coordenadas['norte'] for coordenadas in datos['coordenadas']]
    visados_values = [coordenadas['id'] for coordenadas in datos['coordenadas']]
    ax.plot(este_values, norte_values, linestyle='-', color='blue')  # Líneas azules
    ax.plot(este_values, norte_values, marker='o', markersize=5, markerfacecolor='red', markeredgecolor='red')  # Puntos rojos

    ax.fill_between(este_values, norte_values, color='lightblue', alpha=0.3)  # Resaltar el área bajo la curva (sombreado)    

    ax.set_xlabel('Este')
    ax.set_ylabel('Norte')
    ax.set_title('Poligonal Cerrada Brazo Externo')
    ax.grid(True)

    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.yaxis.get_major_formatter().set_scientific(False)
    ax.yaxis.get_major_formatter().set_useOffset(False)

    ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.xaxis.get_major_formatter().set_scientific(False)
    ax.xaxis.get_major_formatter().set_useOffset(False)

    # Agregar etiquetas a los puntos
    for x, y, label in zip(este_values, norte_values, visados_values):
        ax.text(x, y, label, fontsize=10, ha='left', va='bottom')

    # Ajustar límites del eje y
    min_y = min(norte_values)
    max_y = max(norte_values)
    y_margin = (max_y - min_y) * 0.1  # Margen del 10% en la parte superior e inferior
    ax.set_ylim(min_y - y_margin, max_y + y_margin)

    return fig

def guardar_grafico(fig):
    img_path = os.path.join(settings.MEDIA_ROOT, 'temporal.png')
    fig.savefig(img_path, format='png')
    plt.close(fig)
    return img_path

def procesar_archivos_pol_cerrada(request):
    if request.method == 'GET':
        datos = procesar_archivos()
        fig = generar_grafico1(datos)
        img_path = guardar_grafico(fig)

        if os.path.exists(img_path):
            print("La imagen se ha creado correctamente.")
        else:
            print("Error al crear la imagen.")

        # Genera un valor aleatorio para evitar la caché de la imagen
        random_value = random.randint(1, 100000)

        # Construye la URL de la imagen con el valor aleatorio
        img_url = f"{settings.MEDIA_URL}temporal.png?{random_value}"

        datos['img_url'] = img_url

        return render(request, 'grafico1.html', datos)

def procesar_archivos_pol_cerrada_doble(request):
    if request.method == 'GET':
        datos = pol_cerrada2()
        fig = generar_grafico2(datos)
        img_path = guardar_grafico(fig)

        if os.path.exists(img_path):
            print("La imagen se ha creado correctamente.")
        else:
            print("Error al crear la imagen.")

        # Genera un valor aleatorio para evitar la caché de la imagen
        random_value = random.randint(1, 100000)

        # Construye la URL de la imagen con el valor aleatorio
        img_url = f"{settings.MEDIA_URL}temporal.png?{random_value}"

        datos['img_url'] = img_url

        return render(request, 'grafico2.html', datos)
    
def procesar_archivos_pol_cerrada_ex(request):
    if request.method == 'GET':
        datos = pol_cerrada3()
        fig = generar_grafico3(datos)
        img_path = guardar_grafico(fig)

        if os.path.exists(img_path):
            print("La imagen se ha creado correctamente.")
        else:
            print("Error al crear la imagen.")

        # Genera un valor aleatorio para evitar la caché de la imagen
        random_value = random.randint(1, 100000)

        # Construye la URL de la imagen con el valor aleatorio
        img_url = f"{settings.MEDIA_URL}temporal.png?{random_value}"

        datos['img_url'] = img_url

        return render(request, 'grafico3.html', datos)

from django.shortcuts import redirect

def calcular_ondulacion(request):
    if request.method == 'POST':
        # Obtener coordenadas y calcular ondulación
        lat = float(request.POST.get('lat'))
        lng = float(request.POST.get('lng'))
        resultado = obtener_ondulacion(lat, lng)

        # Devolver el resultado como una respuesta JSON
        return JsonResponse({'ondulacion': resultado})

    return render(request, 'mapa.html')


def mostrar_ond(request):
    ondulacion = request.GET.get('ondulacion')
    return render(request, 'mostrar_ond.html', {'ondulacion': ondulacion})


def calcular_azimut(request):
    if request.method == 'POST':
        norte1 = float(request.POST.get('norte1'))
        este1 = float(request.POST.get('este1'))
        norte2 = float(request.POST.get('norte2'))
        este2 = float(request.POST.get('este2'))

        dx = este2 - este1
        dy = norte2 - norte1

        print(dx, dy)

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
        direccion = validar_rumbo(dy,dx)
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

        azimut_grados = int(azimut)
        azimut_minutos = int((azimut - azimut_grados) * 60)
        azimut_segundos = (azimut - azimut_grados - azimut_minutos / 60) * 3600


        rumbo_grados = int(rumbo_deg)
        rumbo_minutos = int(((rumbo_deg) - rumbo_grados) * 60)
        rumbo_segundos = (rumbo_deg - rumbo_grados - rumbo_minutos/60) * 3600

        cuadrante = direccion

        distancia = math.sqrt(dx ** 2 + dy ** 2)

        punto1 = {'norte': norte1, 'este': este1}
        punto2 = {'norte': norte2, 'este': este2}

        return render(request, 'formulario_azimut.html', {
            'azimut_grados': azimut_grados,
            'azimut_minutos': azimut_minutos,
            'azimut_segundos': azimut_segundos,
            'rumbo_grados': rumbo_grados,
            'rumbo_minutos': rumbo_minutos,
            'rumbo_segundos': rumbo_segundos,
            'cuadrante': cuadrante,
            'distancia': distancia,
            'punto1': punto1,
            'punto2': punto2,
        })

    return render(request, 'formulario_azimut.html')