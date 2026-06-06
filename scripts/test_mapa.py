import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agpy.settings')
django.setup()

from django.test import Client

client = Client(HTTP_HOST='localhost')
import time

t0 = time.time()
response = client.get('/mapa/')
t1 = time.time()
print(f"/mapa/: {response.status_code} em {t1-t0:.2f} segundos")
