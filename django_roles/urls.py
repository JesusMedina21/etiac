"""django_roles URL Configuration

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
from django.urls import path, include
from django.conf import settings
from core import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('login/', views.login, name='login'),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('examenes/<int:evaluacion_id>/', views.examen, name='examenes'),
    path('resultados/<int:evaluacion_id>/', views.resultados, name='resultados'),
    path('resultadosprofesores/<int:evaluacion_id>/', views.resultadosprofesores, name='resultadosprofesores'),
    path('resultadosdetallados/<int:evaluacion_id>/', views.resultadosdetallados, name='resultadosdetallados'),
    path('usuario_crear/', views.usuario_crear, name='usuario_crear'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuario_editar/<int:user_id>/', views.usuario_editar, name='usuario_editar'),
    path('usuario_actualizar_contrasena_y_usuario/<int:user_id>/', views.usuario_actualizar_contrasena_y_usuario, name='usuario_actualizar_contrasena_y_usuario'),
  

]


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()