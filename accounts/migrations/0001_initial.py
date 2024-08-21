# Generated by Django 4.2.6 on 2023-10-21 02:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=150, null=True, verbose_name='Dirección')),
                ('cedula_estado', models.CharField(choices=[('V', 'V'), ('P', 'P'), ('E', 'E')], default='V', max_length=1, verbose_name='Estado de Cedula')),
                ('cedula', models.IntegerField(null=True, unique=True, verbose_name='Número de Cedula')),
                ('telephone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'perfil',
                'verbose_name_plural': 'perfiles',
                'ordering': ['-id'],
            },
        ),
    ]