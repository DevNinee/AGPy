import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agpy.settings')
django.setup()

from django.test import Client
from django.urls import reverse

client = Client(HTTP_HOST='localhost')

endpoints = [
    '/',
    '/ranking/',
    '/comparar/',
    '/mapa/',
    '/historico/',
    '/classificacao/',
    '/graficos/',
    '/buscar/',
    '/exportar/excel/',
]

for url in endpoints:
    try:
        response = client.get(url)
        print(f"{url}: {response.status_code}")
    except Exception as e:
        print(f"{url}: ERROR - {str(e)}")
