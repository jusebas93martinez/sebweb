"""sebweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from poligonal import views
from django.conf import settings
from django.conf.urls.static import static


'''handler404 = error_404'''
'''handler404 = 'poligonal.views.error_404'''


urlpatterns = [
    path('admin/', admin.site.urls),
    path('loadfile/', views.cargar_archivos_pol_cerrada, name='cargar_archivos_pol_cerrada'),
    path('loadfile_poldoble/', views.cargar_archivos_pol_cerrada_doble, name='cargar_pol'),
    path('pol_cerrada/', views.procesar_pol, name='procesar_pol_cerrada'),
    path('pol_cerrada_doble/', views.procesar_pol_doble, name='procesar_poligonal_doble'),
    path('grafica1/', views.procesar_archivos_pol_cerrada, name='grafica1'),
    path('grafica2/', views.procesar_archivos_pol_cerrada_doble,name='grafica2'),
    path('base/', views.index, name='index'),
    path('acercade/', views.acercade, name='acercade'),
    path('contacto/', views.contacto, name='contacto'),
    path('', views.inicio, name='inicio'),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

