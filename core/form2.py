from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import Profile
from .models import *
from .forms import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django.core.exceptions import ValidationError

class LoginForm(AuthenticationForm):
    pass


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'cedula', 'telephone']

####

class MateriaForm(forms.ModelForm):
    titulo_materia = forms.CharField(max_length=200, label='Título de la materia')
    
    class UserChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.get_full_name()

    docente = UserChoiceField(queryset=User.objects.filter(groups__name='profesores'), label='Profesor')
    class Meta:
        model = Materia
        fields = ['titulo_materia', 'docente']


class EvaluacionForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Evaluacione.STATUS_CHOICES, initial='I', label='Estado')
    materia = forms.ModelChoiceField(queryset=Materia.objects.none(), label='Materia')

    class Meta:
        model = Evaluacione
        fields = ['titulo', 'materia', 'status']

    def __init__(self, *args, **kwargs): #######<<<<<-------- Este codigo es el que me muestra las materias del mismo profesor
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['materia'].queryset = Materia.objects.filter(docente=user)

    helper = FormHelper()
    helper.layout = Layout(
        Field('titulo'),
        Field('materia'),
        Field('status'),
        Submit('submit', 'Submit')
    )


class ExamenesForm(forms.ModelForm): 
    evaluacion = forms.ModelChoiceField(queryset=Evaluacione.objects.all(), label='Evaluacion') 
    texto_pregunta = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Pregunta') 
    
    class Meta: 
        model = examenes 
        fields =  ['evaluacion', 'texto_pregunta', 'max_puntaje' ]

    def clean_max_puntaje(self):
            max_puntaje = self.cleaned_data.get('max_puntaje')
            if max_puntaje > 20:
                raise forms.ValidationError('Error: No puede superar los 20 puntos')
            return max_puntaje        

         
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Puedes eliminar esta línea si no necesitas el argumento 'user'
        materia_id = kwargs.pop('materia_id', None)
        super().__init__(*args, **kwargs)
        if materia_id:
            self.fields['evaluacion'].queryset = Evaluacione.objects.filter(materia__id=materia_id, status__in=['E', 'R'])

        # Lógica adicional utilizando el argumento 'user' si es necesario

    helper = FormHelper() 
    helper.layout = Layout( 
        Field('evaluacion'), 
        Field('texto_pregunta'), 
        Field('max_puntaje'), 
        Submit('submit', 'Submit') 
    )
    
class ElegirRespuestaForm(forms.ModelForm):


    class Meta:
        model = ElegirRespuesta
        fields = ['texto', 'correcta']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3}),
            'correcta': forms.ChoiceField(choices=[(True, 'Correcta'), (False, 'Incorrecta')], label='¿Es esta la respuesta correcta?', initial=False)
        }
        required = {
        'texto': False
    }
    def __init__(self, *args, **kwargs):
        examen_id = kwargs.pop('examen_id', None)
        super().__init__(*args, **kwargs)
        if examen_id:
            self.fields['examenes'].queryset = examenes.objects.filter(id=examen_id)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('examenes'),
            Field('correcta', css_class='campo-en-linea'),
            Field('texto', css_class='campo-en-linea'),
            Submit('submit', 'Submit')
        )
    def clean(self):
        cleaned_data = super().clean()
        correcta = cleaned_data.get('correcta')

        if not correcta:
            raise ValidationError('Debes seleccionar al menos una respuesta correcta.')

        return 
    

#class ContenidoForm(forms.ModelForm): 
#    informacion = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}), label='Informacion', required=True) 
#    def __init__(self, *args, **kwargs): 
#        super().__init__(*args, **kwargs) 
  
#    class Meta: 
#        model = Contenido 
#        fields = ['archivo','informacion'] 
