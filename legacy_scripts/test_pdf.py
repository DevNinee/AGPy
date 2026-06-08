import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agpy.settings')
django.setup()

from django.test import Client

client = Client(HTTP_HOST='localhost')
try:
    response = client.get('/exportar/pdf/')
    print(f"/exportar/pdf/: {response.status_code}")
except Exception as e:
    print(f"/exportar/pdf/: ERROR - {str(e)}")
