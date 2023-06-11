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
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker

from django.shortcuts import render, HttpResponseRedirect, reverse
from .utils import procesar_archivos

def error_404(request, exception):
    return render(request, '404.html', status=404)

def index(request):
    return render(request, 'base.html')

def inicio(request):
    return render(request, 'inicio.html')

def cargar_archivos(request):
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
        return HttpResponseRedirect(reverse('procesar_archivos') + f'?pol_file={pol_file.name}&bases_file={bases_file.name}')


    return render(request, 'loadfile.html')

def procesar_archivos_view(request):
    if request.method == 'GET':

        datos = procesar_archivos()

        # Generar el gráfico con Matplotlib
        fig, ax = plt.subplots(figsize=(8, 6))
        este_values = [resultado['Este'] for resultado in datos['resultados']]
        norte_values = [resultado['Norte'] for resultado in datos['resultados']]
        visados_values = [resultado['visado'] for resultado in datos['resultados']]
        ax.plot(este_values + [este_values[0]], norte_values + [norte_values[0]], marker='o')


        ax.set_xlabel('Este')
        ax.set_ylabel('Norte')
        ax.set_title('Poligonal')
        ax.grid(True)

        ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        ax.yaxis.get_major_formatter().set_scientific(False)
        ax.yaxis.get_major_formatter().set_useOffset(False)
        
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        ax.xaxis.get_major_formatter().set_scientific(False)
        ax.xaxis.get_major_formatter().set_useOffset(False)


        # Agregar etiquetas a los puntos
        for x, y, label in zip(este_values, norte_values, visados_values):
            ax.text(x, y, label, fontsize=8, ha='center', va='bottom')

        img_path = os.path.join(settings.MEDIA_ROOT, 'temporal.png')
        plt.savefig(img_path, format='png')
        plt.close()
        
        if os.path.exists(img_path):
          print("La imagen se ha creado correctamente.")
        else:
          print("Error al crear la imagen.")

        # Genera un valor aleatorio para evitar la caché de la imagen
        random_value = random.randint(1, 100000)

        # Construye la URL de la imagen con el valor aleatorio
        img_url = f"{settings.MEDIA_URL}temporal.png?{random_value}"

        datos['img_url'] = img_url

        return render(request, 'resultados.html',datos)
