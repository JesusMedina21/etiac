from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', login_required(login.as_view()), name='login'),
    path('materia/', login_required(MateriaVista.as_view()), name='materia'),
    path('materia/crear/', login_required(CrearMateria.as_view()), name='materia_crear'),
    path('materia/<int:pk>/edit/', login_required(EditarMateria.as_view()), name='materia_editar'),
    path('materia/borrar', login_required(BorrarMateria.as_view()), name='materia_borrar'),
    path('evaluacion/<int:materia_id>/', login_required(EvaluacionVista.as_view()), name='evaluacion'),
    path('evaluacion/crear/<int:materia>/', login_required(CrearEvaluacion.as_view()), name='evaluacion_crear'),
    path('evaluacion/<int:pk>/edit/', login_required(EditarEvaluacion.as_view()), name='evaluacion_editar'),
    path('evaluacion/borrar', login_required(BorrarEvaluacion.as_view()), name='evaluacion_borrar'),
    path('contenidoestudiante/<int:evaluacion_id>/',login_required (ContenidoEstudiante.as_view()), name='contenidoestudiante'),  
    path('crearcontenido/<int:evaluacion_id>/',login_required (CrearContenido.as_view()), name='crearcontenido'),  
    path('contenidoeditar/<int:pk>/edit/', login_required(EditarContenido.as_view()), name='contenidoeditar'),
    path('contenidoborrar/borrar', login_required(BorrarContenido.as_view()), name='contenidoborrar'),
    path('examenes_profesores/<int:evaluacion_id>/', login_required(ExamenProfesores.as_view()), name='examenes_profesores'),
    path('examenes_crear/<int:pk>/', login_required(CrearExamen.as_view()), name='examenes_crear'), 
    ##Al colocar el pk que es como un id a examenes_crear puedo hacer el filtrado y al crear examenes solamente me muestra
    #la evaluacion de ese mismo examen
    path('examenes_editar/<int:pk>/edit/', login_required(EditarExamen.as_view()), name='examenes_editar'),
    path('examenes/borrar/', login_required(BorrarExamen.as_view()), name='examenes_borrar'),
    path('usuarios/borrar/', login_required(BorrarUsuarios.as_view()), name='usuarios_borrar'),
    path('error/', login_required(error.as_view()), name='error'),
    path('error_examenfinalizado/', login_required(errorexamenfinalizado.as_view()), name='errorexamenfinalizado'),
    path('error_examenfinalizado/', login_required(errorexamenfinalizado.as_view()), name='errorelaborandoexamen'),
    
]

