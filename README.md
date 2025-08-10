# Guía de instalación del proyecto Django

## ¿De que se trata es proyecto?

ETIAC es un Sitio Web que permite la elaboracion y realizacion de examenes tipo Quiz/Seleccion Multiple y Verdadero y Falso, facilitando la creacion de examenes, la realizacion de los mismos y la evaluacion de los resultados de los estudiantes. Ademas permitiendo al docente agregar contenido a dicho Sitio Web.

## Instalaciones necesarias

- [Visual Studio Code](https://code.visualstudio.com/)
- [Python](https://www.python.org/downloads/)

## Antes de comenzar

Antes de comenzar a instalar las dependencias del proyecto es necesario verificar que tienes las dependencias necesarias instaladas.
Abre la terminal de comandos de tu sistema y sigue los siguientes pasos para asegurarte de que todo está correcto antes de comenzar.

### Verificar instalación de Python

```
python --v
```


### Comandos para instalar el backend


- Ejecuta el siguiente comando para instalar el proyecto:

## Si estas en Windows

```
py -m venv venv 
```

```
.\venv\Scripts\activate
```

```
pip install -r requirements.txt
```

## Si estas en una Distribucion Linux basada en Debian (Ubuntu, Linux Mint etc...)

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
pip3 install -r requirements.txt
```

## Levantar proyecto

Para ejecutar el servidor de desarrollo del proyecto debes ejecutar el siguiente comando:

## Si estas en Windows

```

python manage.py runserver
```

## Si estas en Linux

```

python3 manage.py runserver
```

Te diriges a la url localhost:8000 en el navegador


<h3 align="center">¡Y Listo! Has terminado de correr el proyecto 🥳</h3>
