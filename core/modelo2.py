from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import random

def validate_only_letters_and_spaces(value):
    if not value.replace(" ", "").isalpha():
        raise ValidationError(
            _('El campo título de la materia solo puede contener letras y espacios.'),
            code='invalid'
        )


##NUEVO2
class Materia(models.Model):
    titulo_materia = models.CharField(max_length=200, unique=True, validators=[validate_only_letters_and_spaces])
    docente = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'profesores'}, verbose_name='Profesor')

    def __str__(self) -> str:
        return self.titulo_materia

    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['-id']


class Evaluacione(models.Model):
    STATUS_CHOICES = (
        ('E', 'Elaborando examen'),
        ('R', 'Realizar examen'),
        ('F', 'Examen Finalizado'),
    )
    titulo = models.CharField(max_length=200, unique=True, validators=[validate_only_letters_and_spaces])
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='E', verbose_name='Estado')
   

    def calcular_puntaje_total_actual(self):
        return self.examenes_set.aggregate(total=models.Sum('max_puntaje'))['total'] or 0
    
    def max_puntaje(self):
        return self.examenes_set.aggregate(total=models.Sum('max_puntaje'))['total'] or 0

    def calcular_puntaje_total(self):
        return self.examenes_set.aggregate(total=models.Sum('max_puntaje'))['total'] or 0
    def __str__(self) -> str:
        return f"{self.titulo} - {self.get_status_display()}"

    class Meta:
        verbose_name = 'Evaluacion'
        verbose_name_plural = 'Evaluaciones'
        ordering = ['-id']

#class Contenido(models.Model):
#    evaluacion = models.ForeignKey(Evaluacione, on_delete=models.CASCADE)  
#    archivo = models.FileField(upload_to='archivos/', verbose_name='Subir Archivo', blank=True, null=True)
#    informacion = models.CharField(max_length=150, null=True, blank=True, verbose_name='Informacion')

#    class Meta:
#        verbose_name = 'Contenido'
#        verbose_name_plural = 'Contenidos'

# nuevo 2

# nuevo 1
def validar_max_puntaje(value):
    evaluacion = value.evaluacion
    puntaje_maximo_evaluacion = evaluacion.max_puntaje_evaluacion
    if value > puntaje_maximo_evaluacion:
        raise ValidationError('El puntaje máximo no puede ser mayor que el puntaje máximo de la evaluación.')


class examenes(models.Model):
    NUMERO_DE_RESPUESTAS_PERMITIDAS = 1
    evaluacion = models.ForeignKey(
        Evaluacione, on_delete=models.CASCADE, null=True)
    texto_pregunta = models.TextField(verbose_name='Pregunta:' )
    max_puntaje = models.DecimalField(
        verbose_name='Maximo Puntaje', default=2, decimal_places=1, max_digits=6)

    def __str__(self) -> str:
        return self.texto_pregunta

    class Meta:
        verbose_name = 'examen'
        verbose_name_plural = 'examenes'
        ordering = ['-id']
    



class ElegirRespuesta(models.Model):

    examenes = models.ForeignKey(
        examenes, related_name='opciones', on_delete=models.CASCADE, null=True)
    correcta = models.BooleanField(
        verbose_name='Respuesta correcta', default=False, null=False, blank=False)  # <<- El blank=False a juro se tenga que seleccionar
    texto = models.TextField(verbose_name='Respuesta', blank=True)

 

    def __str__(self):
        return self.texto


class ElegirRespuestaForm(forms.ModelForm):
    class Meta:
        model = ElegirRespuesta
        fields = ['texto', 'correcta']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3}),
            'correcta ': forms.BooleanField(widget=forms.CheckboxInput(), required=True) #<--Aqui es donde defino el cuadrito en la vista
        }
        labels = {
            'texto': 'Opciones', ####<<<-- Esto es lo que aparecera en mi formulario
            'correcta': '¿Es correcta?',##<<-- Esto tambien
        }
        required = [
            'correcta',
        ]


class Nota(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    puntaje_total = models.DecimalField(
        verbose_name='Puntaje Total', default=0, decimal_places=2, max_digits=10)
    
    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        ordering = ['-id']

    def crear_intentos(self, examenes):
        for examen in examenes:
            intento = respuestas(examenes=examen, Notas=self)
            intento.save()


    def obtener_nuevos_examenes(self):
        respondidos = respuestas.objects.filter(Notas=self).values_list('examenes__id', flat=True)
        examenes_restantes = examenes.objects.exclude(id__in=respondidos)
    
        if not examenes_restantes.exists():
            return None
        examenes_aleatorios = list(examenes_restantes)
        random.shuffle(examenes_aleatorios)
        return examenes_aleatorios


    def validar_intento(self, examenes_respondidos, respuesta_seleccionada):
        if examenes_respondidos.examenes_id != respuesta_seleccionada.examenes_id:
            return

        examenes_respondidos.respuesta_seleccionada = respuesta_seleccionada
        if respuesta_seleccionada.correcta is True:
            examenes_respondidos.correcta = True
            examenes_respondidos.puntaje_obtenido = respuesta_seleccionada.examenes.max_puntaje
            examenes_respondidos.respuesta = respuesta_seleccionada

        else:
            examenes_respondidos.respuesta = respuesta_seleccionada

        examenes_respondidos.save()

        self.actualizar_puntaje()

    def actualizar_puntaje(self):
        puntaje_actualizado = self.intentos.filter(correcta=True).aggregate(
            models.Sum('puntaje_obtenido'))['puntaje_obtenido__sum']

        if puntaje_actualizado is None:

            puntaje_actualizado = 0

        self.puntaje_total = puntaje_actualizado
        self.save()

    def ha_aprobado(self):
        if self.puntaje_total >= 10:
            return True
        else:
            return False

    def obtener_examenes_respondidos(self):
        return respuestas.objects.filter(Notas=self)



class respuestas(models.Model):
    Notas = models.ForeignKey(
        Nota, on_delete=models.CASCADE, related_name='intentos')
    examenes = models.ForeignKey(examenes, on_delete=models.CASCADE)
    respuesta = models.ForeignKey(
        ElegirRespuesta, on_delete=models.CASCADE, null=True)
    correcta = models.BooleanField(
        verbose_name='Respuesta Correcta', default=False, null=False)
    puntaje_obtenido = models.DecimalField(
        verbose_name='Puntaje Obtenido', default=0, decimal_places=2, max_digits=6)


# nuevo 1


