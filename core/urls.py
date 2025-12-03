"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from apps.informacion.views import register_client, update_client,types_account, open_account, transfer, pay_service, show_account, types_services

urlpatterns = [
    path('cliente/',register_client, name="registrar-cliente"),
    path('cliente/<int:pk>/',update_client,name="actualizar-cliente"),
    path('tipo-cuenta/',types_account,name="tipo-cuenta"),
    path('tipo-servicio/',types_services, name="tipo-servicio"),
    path('open-account/',open_account,name="abrir-cuenta"),
    path('transferir/',transfer,name="transferir"),
    path('pago-servicio/',pay_service, name="pago-servicios"),
    path('mostrar-cuenta/<int:pk>/',show_account,name="mostrar-cuenta"),
    path('admin/', admin.site.urls),
]
