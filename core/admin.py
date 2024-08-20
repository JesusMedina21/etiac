from django.contrib import admin
from .models import *

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

# Nuevo2
admin.site.site_header = 'ETIAC'
admin.site.index_title = 'SISTEMA'
admin.site.site_title = 'ETIAC'
# Nuevo2
# NUEVO1

from django.contrib import admin

#admin.site.unregister(User)


#admin.site.unregister(Group)


# NUEVO1


class ElegirRespuestaInline(admin.TabularInline):
      model = ElegirRespuesta
      can_delete = False


class examenesAdmin(admin.ModelAdmin):
      model = examenes
      inlines = [ElegirRespuestaInline]
      list_display = ['texto',]
      search_fields = ['texto', 'exameness__texto']


class respuestasAdmin(admin.ModelAdmin):
      list_display = ['examenes', 'respuesta',
                      'correcta', 'calificacion_obtenida']

      class Meta:
          model = respuestas


class respuestasInline(admin.TabularInline):
      model = respuestas


class NotaAdmin(admin.ModelAdmin):
      inlines = [respuestasInline]


#admin.site.register(Nota, NotaAdmin)
#admin.site.register(Materia)
#admin.site.register(Evaluacione)


class RespuestaAdmin (admin.StackedInline):
    model = ElegirRespuesta


class examenesAdmin(admin.ModelAdmin):
    inlines = [RespuestaAdmin]


#admin.site.register(examenes, examenesAdmin)

