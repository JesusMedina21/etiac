from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
# PERFIL DE USUARIO

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuario')
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name='Dirección')
    CEDULA_CHOICES = (
        ('V', 'V'),
        ('P', 'P'),
        ('E', 'E'),
    )
    cedula_estado = models.CharField(max_length=1, choices=CEDULA_CHOICES, default='V', verbose_name='Estado de Cedula')
    cedula = models.IntegerField(null=True, blank=False, verbose_name='Número de Cedula', unique=True)
    telephone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Teléfono')
  
   
    
    
    def clean(self):
        if self.cedula_estado == 'V' and len(str(self.cedula)) > 8:
            raise ValidationError('La cédula no puede tener más de 8 dígitos si el estado es "V".')
        
        if self.cedula_estado == 'P' and len(str(self.cedula)) > 10:
            raise ValidationError('La cédula no puede tener más de 10 dígitos si el estado es "P".')
        
        if self.cedula_estado == 'E' and len(str(self.cedula)) > 11:
            raise ValidationError('La cédula no puede tener más de 11 dígitos si el estado es "E".')
    
    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'
        ordering = ['-id']

    def __str__(self):
        return self.user.username

def validate_only_letters(value):
    if not value.isalpha():
        raise ValidationError('Solo se permiten letras en este campo.')

User._meta.get_field('first_name').validators.append(validate_only_letters)
User._meta.get_field('last_name').validators.append(validate_only_letters)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)