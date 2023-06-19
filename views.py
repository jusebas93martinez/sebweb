from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
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
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker

from django.shortcuts import render, HttpResponseRedirect, reverse
from .utils import procesar_archivos

'''def error_404(request, exception):
    return render(request, '404.html', status=404)'''

def index(request):
    return render(request, 'base.html')

def inicio(request):
    return render(request, 'inicio.html')

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
    ax.set_title('Poligonal Cerrada con doble punto de apoyo')
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

