"""
URL configuration for mi_proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from Ecomedic import views  # Asegúrate de que el nombre de la aplicación sea correcto

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_page, name='login_page'),
    path('signup/', views.signup, name='signup'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('get-equipos/', views.get_equipos, name='get_equipos'),
    path('generar-reporte/', views.generar_reporte, name='generar_reporte'),
    path('report/', views.view_report, name='view_report'),
    # Rutas para gestionar Usuarios
    path('usuarios/', views.manage_users, name='manage_users'),
    path('api/edit-user/', views.edit_user, name='edit_user'),
    path('api/delete-user/', views.delete_user, name='delete_user'),
    path('api/delete-all-users/', views.delete_all_users, name='delete_all_users'),
    # Rutas para gestionar Salas
    path('salas/', views.manage_salas, name='manage_salas'),
    path('api/add-sala/', views.add_sala, name='add_sala'),
    path('api/edit-sala/', views.edit_sala, name='edit_sala'),
    path('api/delete-sala/', views.delete_sala, name='delete_sala'),
    path('api/delete-all-salas/', views.delete_all_salas, name='delete_all_salas'),
    # Rutas para Equipos Biomédicos
    path('equipos/', views.manage_equipos, name='manage_equipos'),
    path('api/get-equipos-by-sala/', views.get_equipos_by_sala, name='get_equipos_by_sala'),
    path('api/add-equipo/', views.add_equipo, name='add_equipo'),
    path('api/edit-equipo/', views.edit_equipo, name='edit_equipo'),
    path('api/delete-equipo/', views.delete_equipo, name='delete_equipo'),
    path('api/delete-all-equipos/', views.delete_all_equipos, name='delete_all_equipos'),
    # Rutas para Gestionar Clasificación de Residuos
    path('residuos/', views.manage_clasificacion_residuos, name='manage_clasificacion_residuos'),
    path('api/get-clasificacion-residuos/', views.get_clasificacion_residuos, name='get_clasificacion_residuos'),
    path('api/add-clasificacion-residuo/', views.add_clasificacion_residuo, name='add_clasificacion_residuo'),
    path('api/edit-clasificacion-residuo/', views.edit_clasificacion_residuo, name='edit_clasificacion_residuo'),
    path('api/delete-clasificacion-residuo/', views.delete_clasificacion_residuo, name='delete_clasificacion_residuo'),
    path('api/delete-all-clasificacion-residuos/', views.delete_all_clasificacion_residuos, name='delete_all_clasificacion_residuos'),

    path('manage_pconsumo/', views.manage_pconsumo, name='manage_pconsumo'),
    path('api/update-pconsumo/', views.update_pconsumo, name='update_pconsumo'),

]
