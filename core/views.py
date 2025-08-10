from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView
from .forms import *
from .models import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import os 
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.urls import reverse
from django.template.response import TemplateResponse
from functools import wraps
from django.shortcuts import render
from django.forms import formset_factory, modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test  
from django.views import View 
from django.db import IntegrityError
from django.db.models import Q
import re
from django.contrib.auth.models import User
from accounts.models import Profile
from django.contrib.auth.models import Group
from django.db.models import Sum
from django.contrib.auth import login, logout, authenticate
##Supabase STORAGE

import uuid
from supabase import create_client, Client
# Inicializa el cliente de Supabase


url = settings.SUPABASE_URL
key = settings.SUPABASE_KEY
supabase: Client = create_client(url, key)

def logout(request):
    logout(request)
    return redirect('home')


class login(LoginRequiredMixin, TemplateView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

###################################################nuevo2
def plural_to_singular(plural):
    # Diccionario de palabras
    plural_singular = {
        "estudiantes": "estudiante",
        "profesores": "profesor",
        "administrativos": "administrativo",
    }

    return plural_singular.get(plural, "error")

# DECORADOR PERSONALIZADO PARA VISTAS BASADAS EN CLASES
def add_group_name_to_context(view_class):
    original_dispatch = view_class.dispatch

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        group = user.groups.first()
        group_name = None
        group_name_singular =None
        color = None
        if group:
            if group.name == 'estudiantes':
                color = 'bg-primary'
            elif group.name == 'profesores':
                color = 'bg-success'
            elif group.name == 'administrativos':
                color = 'bg-danger'

            group_name = group.name
            group_name_singular = plural_to_singular(group.name)

        context ={
            'group_name': group_name,
            'group_name_singular': group_name_singular,
            'color': color
        }

        self.extra_context = context
        return original_dispatch(self, request, *args, **kwargs)

    view_class.dispatch = dispatch
    return view_class

# DECORADOR PERSONALIZADO PARA VISTAS BASADAS EN FUNCIONES
def add_group_name_to_contextfunciones(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        group = user.groups.first()
        group_name = None
        group_name_singular = None
        color = None
        if group:
            if group.name == 'estudiantes':
                color = 'bg-primary'
            elif group.name == 'profesores':
                color = 'bg-success'
            elif group.name == 'administrativos':
                color = 'bg-danger'

            group_name = group.name
            group_name_singular = plural_to_singular(group.name)

        extra_context = {
            'group_name': group_name,
            'group_name_singular': group_name_singular,
            'color': color
        }

        response = view_func(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            response.context_data.update(extra_context)
            return render(request, response.template_name, response.context_data)
        else:
            return response

    return wrapper



############################################################nuevo2

@add_group_name_to_context
class HomeView(TemplateView):
    template_name = "home.html"

@add_group_name_to_context
class reglas(TemplateView):
    template_name = 'reglas.html'

@add_group_name_to_context
class errorexamenfinalizado(TemplateView):
    template_name = 'errorexamenfinalizado.html'    

@add_group_name_to_context
class errorelaborandoexamen(TemplateView):
    template_name = 'errorelaborandoexamen.html'    


@add_group_name_to_context
class error(TemplateView):
    template_name = 'error.html'   

@add_group_name_to_context
class MateriaVista(TemplateView):
    template_name = 'materia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name='profesores').exists():
            materias = Materia.objects.filter(docente=self.request.user)
        else:
            materias = Materia.objects.all()
        
        context['materias'] = materias
        return context
   
@add_group_name_to_context
class CrearMateria(UserPassesTestMixin, CreateView):
    model = Materia
    form_class = MateriaForm
    template_name = 'materia_crear.html'
    success_url = reverse_lazy('materia')

    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()
    ##Solamente puede entrar el administrativo
    
    def handle_no_permission(self):
        return redirect('error')


    def form_valid(self, form):
        messages.success(self.request, 'Se ha creado la materia correctamente')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al guardar la materia')
        return self.render_to_response(self.get_context_data(form=form))


@add_group_name_to_context
class EditarMateria(UserPassesTestMixin, UpdateView):
    model = Materia
    form_class = MateriaForm
    template_name = 'materia_editar.html'
    success_url = reverse_lazy('materia')

    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Se han guardado los cambios correctamente')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar los cambios')
        return self.render_to_response(self.get_context_data(form=form))


@add_group_name_to_context
class BorrarMateria(View):
    def post(self, request):
        materias_seleccionadas = request.POST.getlist('materias_seleccionadas[]')
        if not materias_seleccionadas:
            messages.warning(self.request, 'No se ha seleccionado ninguna materia')
            return redirect('materia')
        # Procesar la eliminación de las materias seleccionadas
        for materia_id in materias_seleccionadas:
            materia = Materia.objects.get(id=materia_id)
            materia.delete()

        messages.success(self.request, 'La materia se ha eliminado correctamente')   

        return redirect('materia') 


@add_group_name_to_context
class ErrorMateria(TemplateView):
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_image_path = os.path.join(settings.MEDIA_URL, 'error.png')
        context['error_image_path'] = error_image_path
        return context

###########################################################################


@add_group_name_to_context
class EvaluacionVista(UserPassesTestMixin, TemplateView):
    template_name = 'evaluacion.html'

    def test_func(self):
        materia_id = self.kwargs['materia_id']
        materia = Materia.objects.get(id=materia_id)
        docente = materia.docente
        user = self.request.user
        return user == docente or user.groups.filter(name__in=['estudiantes', 'administrativos']).exists()

    
    def handle_no_permission(self):
        return redirect('error')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        materia_id = self.kwargs['materia_id']
        if materia_id:
            materia = Materia.objects.get(id=materia_id)
            evaluaciones = Evaluacione.objects.filter(materia=materia)
        else:
            evaluaciones = Evaluacione.objects.all()
        context['evaluaciones'] = evaluaciones
        context['materia_id'] = materia_id 
        return context
    
   
    
@add_group_name_to_context
class CrearEvaluacion(UserPassesTestMixin, CreateView):
    model = Evaluacione
    form_class = EvaluacionForm
    template_name = 'evaluacion_crear.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materia_id'] = self.kwargs['materia']
        return context


    def get_success_url(self):
        materia_id = self.object.materia.id
        return reverse('evaluacion', args=[materia_id])

    def test_func(self):
        materia = Materia.objects.get(id=self.kwargs['materia'])
        docente = materia.docente
        return self.request.user == docente
    
    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        messages.success(self.request, 'Se ha creado la evaluacion correctamente')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al guardar la evaluacion')
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

@add_group_name_to_context
class EditarEvaluacion(UserPassesTestMixin, UpdateView):
    model = Evaluacione
    form_class = EvaluacionForm
    template_name = 'evaluacion_editar.html'

    

    def test_func(self):
        evaluacion = self.get_object()
        docente = evaluacion.materia.docente
        return self.request.user == docente
    
    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Los cambios se han guardado exitosamente')
        success_url = reverse_lazy('evaluacion', kwargs={'materia_id': self.object.materia.id})        
        return redirect(success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al guardar los cambios')
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_form_kwargs(self): ######### <<---------- Sin este codigo no puedo actualizar editar las evaluaciones 
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

@add_group_name_to_context
class BorrarEvaluacion(View):
    def post(self, request):
        evaluaciones_seleccionadas = request.POST.getlist('evaluaciones_seleccionadas[]')
        # Procesar la eliminación de las evaluaciones seleccionadas
        for evaluacion_id in evaluaciones_seleccionadas:
            evaluacion = Evaluacione.objects.get(id=evaluacion_id)
            evaluacion.delete()

         # Obtener el ID de la materia para redireccionar a la URL 
        materia_id = evaluacion.materia.id

        messages.success(self.request, 'La evaluacion se ha borrado exitosamente')
        
        return redirect(reverse('evaluacion', args=[materia_id]))
        
@add_group_name_to_context
class ErrorEvaluacion(TemplateView):
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_image_path = os.path.join(settings.MEDIA_URL, 'error.png')
        context['error_image_path'] = error_image_path
        return context

######################################################################################


@add_group_name_to_context
class ContenidoEstudiante(UserPassesTestMixin, TemplateView):
    template_name = 'contenidoestudiante.html'

    def test_func(self):
        evaluacion_id = self.kwargs['evaluacion_id']
        evaluacion = Evaluacione.objects.get(id=evaluacion_id)
        docente = evaluacion.materia.docente
        user = self.request.user
        return user == docente or user.groups.filter(name__in=['estudiantes', 'administrativos']).exists()
    
    def handle_no_permission(self):
        return redirect('error')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evaluacion_id = self.kwargs.get('evaluacion_id')
        evaluacion = Evaluacione.objects.get(id=evaluacion_id)
        contenidos = Contenido.objects.filter(evaluacion=evaluacion)
        context['evaluacion'] = evaluacion
        context['contenidos'] = contenidos
        context['contenidos_with_extension'] = [(contenido, contenido.archivo.url.split('.')[-1].lower()) if contenido.archivo else (contenido, '') for contenido in context['contenidos']]
        return context

@add_group_name_to_context
class CrearContenido(UserPassesTestMixin, CreateView): 
    model = Contenido
    template_name = 'crearcontenido.html' 
    form_class = ContenidoForm 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evaluacion_id'] = self.kwargs['evaluacion_id']
        return context
    def test_func(self):
        evaluacion_id = self.kwargs['evaluacion_id']
        evaluacion = Evaluacione.objects.get(id=evaluacion_id)
        docente = evaluacion.materia.docente
        return self.request.user == docente
    def handle_no_permission(self): 
        return redirect('error') 
    def form_valid(self, form): 
        evaluacion_id = self.kwargs['evaluacion_id'] 
        contenido = form.save(commit=False) 
        contenido.evaluacion_id = evaluacion_id 
        # Manejo del archivo subido
        if 'archivo' in self.request.FILES:  # Asegúrate de usar 'archivo'
            file = self.request.FILES['archivo']
            file_ext = file.name.split('.')[-1]
            filename = f"{uuid.uuid4()}.{file_ext}"
            # Subir el archivo a Supabase
            supabase.storage.from_('etiac').upload(
                path=filename,
                file=file.read(),
                file_options={"content-type": file.content_type}
            )
            # Almacenar la URL pública del archivo en el modelo
            contenido.archivo = supabase.storage.from_('etiac').get_public_url(filename)
        contenido.save() 
        messages.success(self.request, 'El contenido se ha guardado correctamente') 
        return redirect('contenidoestudiante', evaluacion_id=evaluacion_id)
    def form_invalid(self, form):
        print(form.errors)  # Imprime los errores en la consola para depurar 
        return self.render_to_response(self.get_context_data(form=form))
 
def clean_supabase_filename(url):
    """Extrae el nombre del archivo de una URL de Supabase."""
    clean_url = url.split('?')[0].split('#')[0]
    return clean_url.split('etiac/')[-1]

def delete_supabase_file(filename):
    """Elimina un archivo de Supabase Storage."""
    try:
        res = supabase.storage.from_('etiac').remove([filename])
        # Opcional: Agregar una verificación para asegurar que se eliminó
        return True
    except Exception as e:
        print(f"Error al eliminar el archivo {filename}: {str(e)}")
        return False

@add_group_name_to_context
class EditarContenido(UserPassesTestMixin, UpdateView):
    model = Contenido
    form_class = ContenidoForm
    template_name = 'contenidoeditar.html'

    def test_func(self):
        contenido_id = self.kwargs['pk']
        contenido = get_object_or_404(Contenido, id=contenido_id)
        docente = contenido.evaluacion.materia.docente
        return self.request.user == docente

    def handle_no_permission(self):
        return redirect('error')

    def get_success_url(self):
        evaluacion_id = self.object.evaluacion.id
        return reverse_lazy('contenidoestudiante', kwargs={'evaluacion_id': evaluacion_id})

    def form_valid(self, form):
        contenido = form.save(commit=False)
        evaluacion_id = contenido.evaluacion.id

        # Capturar el archivo antiguo ANTES de que el formulario lo modifique
        old_file_url = self.get_object().archivo
        old_file_name = clean_supabase_filename(str(old_file_url)) if old_file_url else None

        # Si se sube un nuevo archivo en el formulario
        if 'archivo' in self.request.FILES:
            new_file = self.request.FILES['archivo']
            file_ext = os.path.splitext(new_file.name)[1]
            filename = f"{uuid.uuid4()}{file_ext}"

            try:
                # Subir el nuevo archivo a Supabase
                supabase.storage.from_('etiac').upload(
                    path=filename,
                    file=new_file.read(),
                    file_options={"content-type": new_file.content_type}
                )
                contenido.archivo = supabase.storage.from_('etiac').get_public_url(filename)

                # Eliminar el archivo antiguo solo si existía
                if old_file_name:
                    delete_supabase_file(old_file_name)

                messages.success(self.request, 'El contenido se ha actualizado correctamente.')
                
            except Exception as e:
                messages.error(self.request, f"Error al subir el nuevo archivo: {e}")
                return self.form_invalid(form)
        else:
            # Si no se sube un nuevo archivo, mantener el antiguo
            contenido.archivo = self.get_object().archivo
            messages.success(self.request, 'El contenido se ha actualizado correctamente.')

        contenido.save()
        return redirect('contenidoestudiante', evaluacion_id=evaluacion_id)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el contenido.')
        return self.render_to_response(self.get_context_data(form=form))

class BorrarContenido(View):
    def post(self, request):
        contenidos_seleccionados = request.POST.getlist('contenidos_seleccionados[]')
        evaluacion_id = None

        for contenido_id in contenidos_seleccionados:
            contenido = get_object_or_404(Contenido, id=contenido_id)
            evaluacion_id = contenido.evaluacion_id

            if contenido.archivo:
                try:
                    # Obtener el nombre limpio del archivo
                    file_url = str(contenido.archivo)
                    file_name = self.clean_supabase_filename(file_url)
                    
                    # Intento de eliminación con verificación
                    if not self.delete_supabase_file(file_name):
                        raise Exception("Supabase no confirmó la eliminación")
                        
                except Exception as e:
                    print(f"Fallo al eliminar {file_name}: {str(e)}")
                    messages.warning(request, f"Error al eliminar archivo: {str(e)}")
                    continue  # Continuar con el siguiente archivo

            contenido.delete()

        messages.success(request, 'Contenido eliminado exitosamente')
        return redirect('contenidoestudiante', evaluacion_id=evaluacion_id)

    def clean_supabase_filename(self, url):
        """Limpia la URL para obtener solo el nombre del archivo"""
        # Elimina parámetros de consulta y fragmentos
        clean_url = url.split('?')[0].split('#')[0]
        # Extrae el nombre después de 'etiac/'
        return clean_url.split('etiac/')[-1]

    def delete_supabase_file(self, filename):
        """Intenta eliminar el archivo y verifica el resultado"""
        try:
            # Intento de eliminación
            res = supabase.storage.from_('etiac').remove([filename])
            
            # Verificación adicional listando los archivos
            files = supabase.storage.from_('etiac').list()
            if filename in [f['name'] for f in files]:
                print(f"Archivo {filename} aún existe después de eliminación")
                return False
                
            return True
        except Exception as e:
            print(f"Error en delete_supabase_file: {str(e)}")
            return False
###########################################################################################
@add_group_name_to_context
class ExamenProfesores(UserPassesTestMixin, TemplateView): ##Sin el UserPassesTestMixin no puedo dar permisos
    template_name = 'examenes_profesores.html'

    def test_func(self):
        evaluacion_id = self.kwargs['evaluacion_id']
        evaluacion = Evaluacione.objects.get(id=evaluacion_id)
        docente = evaluacion.materia.docente
        user = self.request.user
        return user == docente or user.groups.filter(name__in=['estudiantes', 'administrativos']).exists()
    
    def handle_no_permission(self):
        return redirect('error')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evaluacion_id = self.kwargs.get('evaluacion_id')
        examen = examenes.objects.filter(evaluacion_id=evaluacion_id).order_by('-id')##<-Con este codigo filtro los examenes de la mismas evaluaciones
        materia_id = None
        if examen:
            materia_id = examen[0].evaluacion.materia.id 
        context['examen'] = examen
        context['evaluacion_id'] = evaluacion_id
        context['materia_id'] = materia_id
        context['evaluacion'] = examen[0].evaluacion if examen else None
        return context

ElegirRespuestaFormset = formset_factory(ElegirRespuestaForm, extra=4)
@add_group_name_to_context
class CrearExamen(UserPassesTestMixin, CreateView):
    model = examenes
    form_class = ExamenesForm
    second_form_class = ElegirRespuestaForm
    template_name = 'examenes_crear.html'
    
    def get_success_url(self):
        evaluacion_id = self.object.evaluacion.id
        return reverse('examenes_profesores', kwargs={'evaluacion_id': evaluacion_id})
    ###CrearExamen tiene un id, por ejemplo CrearExamen/2 pues le estoy diciendo que me mande a la 
    ##vista examenes_profesores/2 el 2 es el id de la evaluacion

    def test_func(self):
        evaluacion_id = self.kwargs['pk']
        evaluacion = Evaluacione.objects.get(id=evaluacion_id)
        docente = evaluacion.materia.docente
        return self.request.user == docente
    
    def handle_no_permission(self):
        return redirect('error')
    
    def form_valid(self, form):
        formset = ElegirRespuestaFormset(self.request.POST)
        if form.is_valid() and formset.is_valid():
            # Contador para las respuestas correctas
            campos_llenos = 0
            correctas = 0

            for form_elegir_respuesta in formset:
                if form_elegir_respuesta.is_valid():
                    # Si la respuesta es correcta, incrementamos el contador
                    if form_elegir_respuesta.cleaned_data.get('correcta'):
                        correctas += 1
                        # Si hay más de una respuesta correcta, lanzamos un error
                        if correctas > 1:
                            messages.error(self.request, 'Error: Solo puede haber una respuesta correcta.')
                            return self.render_to_response(self.get_context_data(form=form, formset=formset))
                    # Si el campo de texto está vacío, pero la respuesta está marcada como correcta, lanzamos un error
                    if not form_elegir_respuesta.cleaned_data.get('texto') and form_elegir_respuesta.cleaned_data.get('correcta'):
                        messages.error(self.request, 'Error: El campo de texto no puede estar vacío si la respuesta es correcta.')
                        return self.render_to_response(self.get_context_data(form=form, formset=formset))
                    if form_elegir_respuesta.cleaned_data.get('texto'):
                        campos_llenos += 1
    
            evaluacion = form.cleaned_data['evaluacion']
            puntaje_total_evaluacion = evaluacion.calcular_puntaje_total()
            examen = form.save(commit=False)
            if puntaje_total_evaluacion + examen.max_puntaje > 20:
                messages.error(self.request, 'Error: El puntaje total de la evaluación no puede superar los 20 puntos.')
                return self.render_to_response(self.get_context_data(form=form, formset=formset))

            if campos_llenos < 2:
                messages.error(self.request, 'Error: Tiene que llenar mínimo dos campos de respuesta.')
                return self.render_to_response(self.get_context_data(form=form, formset=formset))

            if correctas == 0:
                messages.error(self.request, 'Error: Debes seleccionar al menos una respuesta correcta.')
                return self.render_to_response(self.get_context_data(form=form, formset=formset))

            examen = form.save()
            for form_elegir_respuesta in formset:
                elegir_respuesta = form_elegir_respuesta.save(commit=False)
                elegir_respuesta.examenes = examen
                elegir_respuesta.save()

            messages.success(self.request, 'La pregunta se ha guardado correctamente')
            return super().form_valid(form)
        else:
            if not form.is_valid():
                messages.error(self.request, 'Error: No se ha seleccionado una evaluación.')
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        evaluacion_id = self.kwargs.get('evaluacion_id')
        if evaluacion_id is not None:
            kwargs['evaluacion_id'] = evaluacion_id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   ##Context_Data se utiliza para agregar datos 
        
        evaluacion_id = self.kwargs.get('pk') ##Aqui se obtiene el valor de evaluacion_id
        materia_id = Evaluacione.objects.filter(id=evaluacion_id).values_list('materia', flat=True).first()
        ##la linea de arriba realiza consultas a la base de datos para obtener el id de la materia segun la evaluacion
        context['evaluacion_id'] = evaluacion_id
        if materia_id:
            context['form'] = self.form_class(materia_id=materia_id)
        #Aqui actualizamos el formulario para obtener  para tener las evaluaciones filtradas segun la materia
        if 'form_elegir_respuesta' not in context:
            context['form_elegir_respuesta'] = self.second_form_class(data=self.request.POST or None)
        if 'formset' not in context:
            context['formset'] = ElegirRespuestaFormset()
        return context

    def get_initial(self):
        initial = super().get_initial()
    # Establece los valores iniciales de los campos del formulario como vacíos
        initial['texto'] = ''
        initial['correcta'] = None
        return initial
    

from django.forms import modelformset_factory 
ElegirRespuestaFormSet = modelformset_factory( 
    model=ElegirRespuesta, 
    form=ElegirRespuestaForm, 
    extra=0 
)  
@add_group_name_to_context 
class EditarExamen(UserPassesTestMixin, UpdateView): 
    model = examenes 
    form_class = ExamenesForm 
    second_form_class = ElegirRespuestaForm 
    template_name = 'examenes_editar.html' 
    
    def test_func(self):
        examen_id = self.kwargs['pk']
        examen = examenes.objects.get(id=examen_id)
        docente = examen.evaluacion.materia.docente
        return self.request.user == docente
    
    def handle_no_permission(self): 
        return redirect('error') 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        examen_id = self.kwargs.get('pk')
        examen = examenes.objects.get(id=examen_id)
        evaluacion_id = self.object.evaluacion.id if self.object.evaluacion else None
        
        materia_id = examen.evaluacion.materia.id if examen.evaluacion else None
        if materia_id:
            context['form'] = self.form_class(materia_id=materia_id, instance=self.object)
        else:
            context['form'] = self.form_class(instance=self.object)
        formset = ElegirRespuestaFormSet(queryset=ElegirRespuesta.objects.filter(examenes=examen))
        context['formset'] = formset
        context['examen_id'] = examen_id
        context['evaluaciones'] = Evaluacione.objects.filter(materia=materia_id)
        elegirrespuesta_form = ElegirRespuestaForm(instance=None) 
        context['elegirrespuesta_form'] = elegirrespuesta_form
        return context
    
        
    
    
    def post(self, request, *args, **kwargs): 
        self.object = self.get_object() 
        examenes_form = ExamenesForm(request.POST, instance=self.object) 
        elegirrespuesta_formset = ElegirRespuestaFormSet(request.POST, queryset=ElegirRespuesta.objects.filter(examenes=self.object)) 

        if examenes_form.is_valid(): 
            evaluacion = examenes_form.cleaned_data['evaluacion'] 
            examen = examenes_form.save(commit=False) 
    
        # Calcula el puntaje total de todos los exámenes en la evaluación (excluyendo el examen actual)
            puntaje_total_evaluacion_actual = evaluacion.examenes_set.exclude(id=self.object.id).aggregate(total=Sum('max_puntaje'))['total'] or 0

            # Agrega el puntaje del examen actual
            puntaje_total_evaluacion_actual += examen.max_puntaje

            if puntaje_total_evaluacion_actual > 20: 
                messages.error(self.request, 'Error: El puntaje total de la evaluación no puede superar los 20 puntos.') 
                return self.render_to_response(self.get_context_data(examenes_form=examenes_form, elegirrespuesta_form=elegirrespuesta_formset)) 

            if examenes_form.is_valid() and elegirrespuesta_formset.is_valid():   
                campos_llenos = 0  
                correctas = 0 
                puntaje_total_evaluacion = evaluacion.calcular_puntaje_total()       
                for form in elegirrespuesta_formset:
                    if form.is_valid():
                        # Si la respuesta es correcta, incrementamos el contador
                        if form.cleaned_data.get('correcta'):
                            if not form.cleaned_data.get('texto'):
                                messages.error(self.request, 'Error: Debes escribir el texto de la respuesta correcta.')
                                return self.render_to_response(self.get_context_data(examenes_form=examenes_form, elegirrespuesta_form=elegirrespuesta_formset))
                            correctas += 1
                        if correctas > 1:
                            messages.error(self.request, 'Error: Solo puede haber una respuesta correcta.')
                            return self.render_to_response(self.get_context_data(examenes_form=examenes_form, elegirrespuesta_form=elegirrespuesta_formset))
                        if form.cleaned_data.get('texto'):
                           campos_llenos += 1
                    
                if campos_llenos < 2:
                    messages.error(self.request, 'Error: Tiene que llenar minimo dos campos de respuesta.')
                    return self.render_to_response(self.get_context_data(examenes_form=examenes_form, elegirrespuesta_form=elegirrespuesta_formset))      
    
                
                
                if correctas == 0:
                    messages.error(self.request, 'Error: Debes seleccionar al menos una respuesta correcta.')
                    return self.render_to_response(self.get_context_data(examenes_form=examenes_form, elegirrespuesta_form=elegirrespuesta_formset))         
                examen = examenes_form.save()
                elegirrespuesta_formset.save(commit=False)
                for form in elegirrespuesta_formset:
                    form.instance.examenes = examen
                    form.save()

            # Redireccionar a la página de perfil (con datos actualizados)
            messages.success(self.request, 'Los cambios se han guardado exitosamente')
            evaluacion_id = self.object.evaluacion.id
            success_url = reverse('examenes_profesores', kwargs={'evaluacion_id': evaluacion_id})
            return redirect(success_url)
        else:
            print(examenes_form.errors)
            print(elegirrespuesta_formset.errors)
        # Si alguno de los datos no es válido
        context = self.get_context_data()
        context['examenes_form'] = examenes_form
        context['elegirrespuesta_form'] = elegirrespuesta_formset
        evaluacion_id = self.object.evaluacion.id if self.object.evaluacion else None

        success_url = reverse('examenes_profesores', kwargs={'evaluacion_id': evaluacion_id})
        return redirect(success_url)
        
@add_group_name_to_context    
class BorrarExamen(View):
    def post(self, request):
        examenes_seleccionados = request.POST.getlist('examenes_seleccionados[]')
        # Procesar la eliminación de los exámenes seleccionados
        for examen_id in examenes_seleccionados:
            examen = examenes.objects.get(id=examen_id)
            examen.delete()
        # Obtengo el ID de la evaluación para redireccionar a la URL correcta
        evaluacion_id = examen.evaluacion.id
        messages.success(self.request, 'El examen se ha borrado exitosamente')       
        return redirect(reverse('examenes_profesores', args=[evaluacion_id]))
#############################################################################

def es_estudiante(user):
    return user.groups.filter(name='estudiantes').exists()
@login_required
@add_group_name_to_contextfunciones
@user_passes_test(es_estudiante, login_url='error')
def examen(request, evaluacion_id):
    Notas, created = Nota.objects.get_or_create(usuario=request.user)
    evaluacion = get_object_or_404(Evaluacione, id=evaluacion_id)
    context = {}  # Asignar un valor predeterminado a context
    if evaluacion.status == 'F':
            # Si el estado de la evaluación es "Examen Finalizado", mostrar un mensaje de error
        return TemplateResponse(request, 'errorexamenfinalizado.html', context)
    elif evaluacion.status == 'E':
            # Si el estado de la evaluación es "Elaborando examen", mostrar un mensaje de error
        return TemplateResponse(request, 'errorelaborandoexamen.html', context)     
        
    if request.method == 'POST':
   
        print(request.POST)  # Agregar esta línea para depurar
        examenes_id = request.POST.get('examenes_id')
        if examenes_id.isdigit():
            try:
                examenes_respondidos = Notas.intentos.select_related('examenes').filter(examenes__id=examenes_id).first()
            except ObjectDoesNotExist:
                raise Http404("La respuesta solicitada no existe")
            respuesta_id = request.POST.get('respuesta_id')
            try:
                opcion_seleccionada = examenes_respondidos.examenes.opciones.get(id=respuesta_id)
            except ObjectDoesNotExist:
                raise Http404("La opción seleccionada no existe")
            Notas.validar_intento(examenes_respondidos, opcion_seleccionada)
            return redirect('examenes', evaluacion_id=evaluacion_id)
            #return redirect('respuestas', examenes_respondidos_id=examenes_respondidos.id)
        else:
            # Manejo del caso cuando examenes_id no es un número válido
            error_message = "El ID del examen no es válido"
            # Puedes hacer algo con el mensaje de error, como mostrarlo en el contexto o enviarlo a la plantilla
            context['error_message'] = error_message
    else:
        examenes_respondidos = Notas.obtener_examenes_respondidos().values_list('examenes__id', flat=True)
        examenes = evaluacion.examenes_set.exclude(id__in=examenes_respondidos).order_by('?').first()
        if examenes is not None:
            Notas.crear_intentos([examenes])   
        context = {
            'evaluacion': evaluacion,
            'examen': examenes,
        }
    return TemplateResponse(request, 'examenes.html', context)

#################################################################################

@login_required
@add_group_name_to_contextfunciones
def respuesta(request, examenes_respondidos_id):
    respondida = get_object_or_404(
        respuestas, id=examenes_respondidos_id)
    context = {
        'respondida': respondida
    }
    if request.user == respondida.Notas.usuario: 
        # Mostrar las respuestas del examen al estudiante
        # Tu código para mostrar las respuestas aquí
        return TemplateResponse(request, 'respuesta.html', {'respondida': respondida})
    else:
        # Redirigir a una página de error o mostrar un mensaje de acceso denegado
     
        # El usuario actual no es el docente asignado, redirigir a la vista error
        return redirect('error')



##########################################################################################################################

def es_estudiante(user):
    return user.groups.filter(name='estudiantes').exists()
@login_required
@add_group_name_to_contextfunciones
@user_passes_test(es_estudiante, login_url='error')
def resultados(request, evaluacion_id):
    evaluacion = Evaluacione.objects.get(id=evaluacion_id)
    
    total_usuarios_examen = Nota.objects.filter(usuario=request.user)
    usuario_examen = []
    for nota in total_usuarios_examen:
        usuario_examen.append(nota)
    respuestas_usuario = respuestas.objects.filter(Notas__in=total_usuarios_examen, examenes__evaluacion__id=evaluacion_id)
    respuestas_usuario_evaluacion = respuestas_usuario.filter(examenes__evaluacion__id=evaluacion_id)
    for user_examen in usuario_examen:
        user_examen.respuestas_correctas = []
        user_examen.puntaje_total = 0  # Inicializar el puntaje total en 0
        
        for respuesta_usuario in respuestas_usuario_evaluacion:
            if respuesta_usuario.Notas == user_examen:
                # Verificar si la respuesta del usuario es correcta
                if respuesta_usuario.respuesta in respuesta_usuario.examenes.opciones.filter(correcta=True):
                    for respuesta_examen in respuesta_usuario.examenes.opciones.filter(correcta=True):
                        user_examen.puntaje_total += respuesta_examen.examenes.max_puntaje  # Sumar el puntaje de la respuesta correcta
                        user_examen.respuestas_correctas.append(respuesta_examen)
                # Agregar la respuesta correcta al objeto de respuesta del usuario
                respuesta_usuario.respuesta_correcta = respuesta_usuario.examenes.opciones.filter(correcta=True).first()
        user_examen.numero_respuestas_correctas = len(user_examen.respuestas_correctas)
    context = {
        'usuario_examen': usuario_examen,
        'respuestas_usuario': respuestas_usuario,
        'perfil_usuario': request.user.profile,
        'evaluacion': evaluacion,
        'materia': evaluacion.materia,
       
    }
    return TemplateResponse(request, 'resultados.html', context)

#############################################################################################################################################


@login_required
@add_group_name_to_contextfunciones
def resultadosprofesores(request, evaluacion_id): 
    evaluacion = Evaluacione.objects.get(id=evaluacion_id)
    evaluacione = get_object_or_404(Evaluacione, id=evaluacion_id)
    context = {}
    if evaluacion.status == 'R':
            # Si el estado de la evaluación es "Examen Finalizado", mostrar un mensaje de error
        return TemplateResponse(request, 'error_realizando_examen.html', context)
    elif evaluacion.status == 'E':
            # Si el estado de la evaluación es "Elaborando examen", mostrar un mensaje de error
        return TemplateResponse(request, 'errorresultadoelaborando.html', context) 
    todas_las_notas = Nota.objects.all() 
    materia = evaluacion.materia
    usuario_examen = [] 
    for nota in todas_las_notas: 
        usuario_examen.append(nota) 
    respuestas_usuario = respuestas.objects.filter(examenes__evaluacion__id=evaluacion_id) 
    respuestas_usuario_evaluacion = respuestas_usuario.filter(examenes__evaluacion__id=evaluacion_id) 
    for user_examen in usuario_examen: 
        user_examen.respuestas_correctas = [] 
        user_examen.puntaje_total = 0  # Inicializar el puntaje total en 0 
        for respuesta_usuario in respuestas_usuario_evaluacion: 
            if respuesta_usuario.Notas == user_examen: 
                # Verificar si la respuesta del usuario es correcta 
                if respuesta_usuario.respuesta in respuesta_usuario.examenes.opciones.filter(correcta=True): 
                    for respuesta_examen in respuesta_usuario.examenes.opciones.filter(correcta=True): 
                        user_examen.puntaje_total += respuesta_examen.examenes.max_puntaje  # Sumar el puntaje de la respuesta correcta 
                        user_examen.respuestas_correctas.append(respuesta_examen) 
                # Agregar la respuesta correcta al objeto de respuesta del usuario 
                respuesta_usuario.respuesta_correcta = respuesta_usuario.examenes.opciones.filter(correcta=True).first() 
        user_examen.numero_respuestas_correctas = len(user_examen.respuestas_correctas) 
    context = { 
        'usuario_examen': usuario_examen, 
        'respuestas_usuario': respuestas_usuario, 
        'evaluacione': evaluacione, 
        'evaluacion': evaluacion,
        'materia': evaluacion.materia,
        'perfil_usuario': request.user.profile,
        
    } 

    if request.user == materia.docente or request.user.groups.filter(name='administrativos').exists(): 
        # El usuario actual es el docente asignado, redirigir a la vista resultadosprofesores.html
        return TemplateResponse(request, 'resultadosprofesores.html', context) 

    else:
        # El usuario actual no es el docente asignado, redirigir a la vista error
        return redirect('error')

   

######################################################################################################################################################



@login_required
@add_group_name_to_contextfunciones
def resultadosdetallados(request, evaluacion_id): 
    evaluacion = Evaluacione.objects.get(id=evaluacion_id)
    materia = evaluacion.materia
    evaluacion = Evaluacione.objects.get(id=evaluacion_id)
    context = {}
    if evaluacion.status == 'R':
            # Si el estado de la evaluación es "Examen Finalizado", mostrar un mensaje de error
        return TemplateResponse(request, 'error_realizando_examen.html', context)
    elif evaluacion.status == 'E':
            # Si el estado de la evaluación es "Elaborando examen", mostrar un mensaje de error
        return TemplateResponse(request, 'errorresultadoelaborando.html', context) 
    todas_las_notas = Nota.objects.all() 
    materia = evaluacion.materia
    usuario_examen = [] 
    for nota in todas_las_notas: 
        usuario_examen.append(nota) 
    respuestas_usuario = respuestas.objects.filter(examenes__evaluacion__id=evaluacion_id) 
    respuestas_usuario_evaluacion = respuestas_usuario.filter(examenes__evaluacion__id=evaluacion_id) 
    for user_examen in usuario_examen: 
        user_examen.respuestas_correctas = [] 
        user_examen.puntaje_total = 0  # Inicializar el puntaje total en 0 
        for respuesta_usuario in respuestas_usuario_evaluacion: 
            if respuesta_usuario.Notas == user_examen: 
                # Verificar si la respuesta del usuario es correcta 
                if respuesta_usuario.respuesta in respuesta_usuario.examenes.opciones.filter(correcta=True): 
                    for respuesta_examen in respuesta_usuario.examenes.opciones.filter(correcta=True): 
                        user_examen.puntaje_total += respuesta_examen.examenes.max_puntaje  # Sumar el puntaje de la respuesta correcta 
                        user_examen.respuestas_correctas.append(respuesta_examen) 
                # Agregar la respuesta correcta al objeto de respuesta del usuarioasd 
                respuesta_usuario.respuesta_correcta = respuesta_usuario.examenes.opciones.filter(correcta=True).first() 
        user_examen.numero_respuestas_correctas = len(user_examen.respuestas_correctas) 
    context = { 
        'usuario_examen': usuario_examen, 
        'respuestas_usuario': respuestas_usuario,
        'evaluacion': evaluacion,
        'materia': materia,
        'perfil_usuario': request.user.profile,
        
    } 
    if request.user == materia.docente or request.user.groups.filter(name='administrativos').exists(): 
        # El usuario actual es el docente asignado, redirigir a la vista resultadosprofesores.html
        return TemplateResponse(request, 'resultadosdetallados.html', context) 
    else:
        # El usuario actual no es el docente asignado, redirigir a la vista error
        return redirect('error')

@add_group_name_to_contextfunciones
def validar_cedulacrear(request, cedula, cedula_estado):
    # Verificar si la cédula tiene solo números
    if not cedula.isdigit():
        messages.error(request, 'La cedula debe de contener solo numeros')
        return False
    # Verificar la longitud de la cédula según el valor de cedula_estado
    if cedula_estado == 'V' and len(cedula) > 8:
        messages.error(request, 'La cedula no puede pasar los 8 digitos')
        return False
    elif cedula_estado == 'E' and len(cedula) != 10:
        messages.error(request, 'La cedula debe de tener 10 digitos')
        return False
    elif cedula_estado == 'P' and len(cedula) != 11:
        messages.error(request, 'La cedula debe de tener 11 digitos')
        return False
    # Verificar si la cédula ya está en uso
    if User.objects.filter(profile__cedula=cedula).exists():
        messages.error(request, 'Ya existe esta cedula')
        return False
    return True

@add_group_name_to_contextfunciones
def validar_cedula(request, cedula, cedula_estado, user):
    # Verificar si la cédula tiene solo números
    if not cedula.isdigit():
        messages.error(request, 'La cedula debe de contener solo numeros')
        return False
    # Verificar la longitud de la cédula según el valor de cedula_estado
    if cedula_estado == 'V' and len(cedula) > 8:
        messages.error(request, 'La cedula no puede pasar los 8 digitos')
        return False
    elif cedula_estado == 'E' and len(cedula) != 10:
        messages.error(request, 'La cedula debe de tener 10 digitos')
        return False
    elif cedula_estado == 'P' and len(cedula) != 11:
        messages.error(request, 'La cedula debe de tener 11 digitos')
        return False
    # Verificar si la cédula ya está en uso
    if User.objects.filter(profile__cedula=cedula).exclude(id=user.id).exists():
        messages.error(request, 'Ya existe esta cedula')
        return False
    return True

def es_administrativo(user):
    return user.groups.filter(name='administrativos').exists()
@login_required
@user_passes_test(es_administrativo, login_url='error')    
@login_required
@add_group_name_to_contextfunciones
def usuario_crear(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        group_name = request.POST['group']
        cedula = request.POST['cedula']
        cedula_estado = request.POST['cedula_estado']
        
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('usuario_crear')
        
        # Validar que el nombre y apellido solo contengan letras
        if not re.match("^[a-zA-Z\s]+$", first_name) or not re.match("^[a-zA-Z\s]+$", last_name):
            messages.error(request, 'El nombre y apellido solo pueden contener letras')
            return redirect('usuario_crear')
        
        # Validar la cédula
        if cedula == '0':  # Verificar si la cédula es 0
            messages.error(request, 'La cédula no puede ser 0')
            return redirect('usuario_crear')
        
        if cedula.startswith('0'):  # Verificar si la cédula comienza con 0
            messages.error(request, 'La cédula no puede comenzar con 0')
            return redirect('usuario_crear')
        
        if not validar_cedulacrear(request, cedula, cedula_estado):
            return redirect('usuario_crear')
        
        # Validar la contraseña
        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return redirect('usuario_crear')
        
        try:
            # Crear el usuario
            user = User.objects.create(username=username, first_name=first_name, last_name=last_name)
            user.set_password(password)
            
            # Obtener el objeto Group correspondiente al nombre del grupo
            group = Group.objects.get(name=group_name)
            # Asignar el grupo al usuario
            user.groups.add(group)
            
            staff_superuser = request.POST.get('staff_superuser', False)
            if staff_superuser:
                user.is_staff = True
                user.is_superuser = True
            
            # Acceder al perfil relacionado o crear uno nuevo si no existe
            profile, created = Profile.objects.get_or_create(user=user)
            # Establecer los valores de cédula y cedula_estado
            profile.cedula = cedula
            profile.cedula_estado = cedula_estado
            
            # Guardar el usuario y el perfil
            user.save()
            profile.save()
            
            messages.success(request, 'El usuario ha sido creado con éxito')
            return redirect('usuarios')  # Redireccionar a la página de inicio
        except IntegrityError:
            messages.error(request, 'Error: el usuario ya existe')
            return redirect('usuario_crear')
    else:
        context = {
            'group_name': None,
            'group_name_singular': None,
            'user_id': None,
            'username': None,
            'first_name': None,
            'last_name': None,
            'cedula': None,
            'cedula_estado': None,
        }
        return TemplateResponse(request, 'usuario_crear.html', context)
def es_administrativo(user):
    return user.groups.filter(name='administrativos').exists()
@login_required
@user_passes_test(es_administrativo, login_url='error')    
@add_group_name_to_contextfunciones
def usuarios(request):

 
    totalusuarios = User.objects.all()
    query = request.GET.get('q')  # Obtén el valor de búsqueda ingresado por el usuario
    
    if query:
        totalusuarios = totalusuarios.filter(
            Q(username__icontains=query) |  # Busca por nombre de usuario que contenga el valor de búsqueda
            Q(profile__cedula__icontains=query) |  # Busca por cédula que contenga el valor de búsqueda
            Q(first_name__icontains=query) |  # Busca por nombres que contengan el valor de búsqueda
            Q(last_name__icontains=query) |  # Busca por apellidos que contengan el valor de búsqueda
            Q(groups__name__icontains=query)  # Busca por nombre de grupo que contenga el valor de búsqueda
        )
        return TemplateResponse(request, 'usuarios.html', {'totalusuarios': totalusuarios, 'query': query})
    else:
        return TemplateResponse(request, 'usuarios.html', {'totalusuarios': totalusuarios})

def es_administrativo(user):
    return user.groups.filter(name='administrativos').exists()
@login_required
@user_passes_test(es_administrativo, login_url='error')    
@add_group_name_to_contextfunciones
def usuario_editar(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Obtener los datos del formulario
       
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        group_name = request.POST['group']
        cedula = request.POST['cedula']
        cedula_estado = request.POST['cedula_estado']

       
        # Validar que el nombre y apellido solo contengan letras
        if not re.match("^[a-zA-Z\s]+$", first_name) or not re.match("^[a-zA-Z\s]+$", last_name):
            messages.error(request, 'El nombre y apellido solo pueden contener letras')
            return redirect('usuario_editar', user_id=user_id)

        # Validar la cédula
        if not validar_cedula(request, cedula, cedula_estado, user):
            return redirect('usuario_editar', user_id=user_id)
        
        if group_name == '-----':
            messages.error(request, 'Por favor, seleccione un grupo')
            return redirect('usuario_editar', user_id=user_id)
        try:
            # Actualizar los datos del usuario existente
            user.first_name = first_name
            user.last_name = last_name
            
            # Obtener el objeto Group correspondiente al nombre del grupo
    
            group = Group.objects.get(name=group_name) 
            # Asignar el grupo al usuario
            user.groups.clear()  # Eliminar todos los grupos existentes
            user.groups.add(group)  
            staff_superuser = request.POST.get('staff_superuser', False) 
            if staff_superuser:
                user.is_staff = True
                user.is_superuser = True
                
            else:
                user.is_staff = False
                user.is_superuser = False
            user.save()
            
            # Actualizar los datos del perfil asociado al usuario
            profile = user.profile
            profile.cedula = cedula
            profile.cedula_estado = cedula_estado
            profile.save()
            messages.success(request, 'El usuario ha sido actualizado con exito')
            return redirect('usuarios')  # Redireccionar a la página de inicio
        except IntegrityError:
            messages.error(request, 'Error ya existe este usuario')
            return redirect('usuario_editar', user_id=user_id)
    else:
        # Obtener los datos existentes del usuario y perfil para mostrar en el formulario
        username = user.username
        first_name = user.first_name
        last_name = user.last_name
        groups = Group.objects.all()
        cedula = user.profile.cedula
        cedula_estado = user.profile.cedula_estado
        context = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'groups': groups,
            'cedula': cedula,
            'cedula_estado': cedula_estado,
            'staff_superuser': user.is_staff and user.is_superuser
        }
        return TemplateResponse(request, 'usuario_editar.html', context) 
           
@add_group_name_to_context    
class BorrarUsuarios(View):
    def post(self, request):
        usuarios_seleccionados = request.POST.getlist('usuarios_seleccionados[]')
        # Procesar la eliminación de los usuarios seleccionados
        for usuario_id in usuarios_seleccionados:
            usuario = User.objects.get(id=usuario_id)
            usuario.delete()
        messages.success(request, 'Los usuarios se han eliminado correctamente')
        return redirect('usuarios')

def es_administrativo(user):
    return user.groups.filter(name='administrativos').exists()
@login_required
@user_passes_test(es_administrativo, login_url='error')    
@add_group_name_to_contextfunciones
def usuario_actualizar_contrasena_y_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('editar_usuario', user_id=user_id)
        try:
            # Actualizar los datos del usuario existente
            user.username = username
            user.set_password(password)
            user.save()
            messages.success(request, 'El usuario ha sido actualizado con exito')
            return redirect('usuarios')  # Redireccionar a la página de inicio
        except IntegrityError:
            messages.error(request, 'Error ya existe este usuario')
            return redirect('usuarios')
    else:
        # Obtener los datos existentes del usuario y perfil para mostrar en el formulario
        username = user.username
        context = {
            'user_id': user_id,
            'username': username,
           
        }
        return TemplateResponse(request, 'usuario_actualizar_contrasena_y_usuario.html', context) 
    
    