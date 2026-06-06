from django.urls import path
# pyrefly: ignore [missing-import]
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ranking/', views.ranking, name='ranking'),
    path('comparar/', views.comparar, name='comparar'),
    path('mapa/', views.mapa, name='mapa'),
    path('graficos/', views.graficos, name='graficos'),
    path('historico/', views.historico, name='historico'),
    path('historico/dados/', views.historico_dados, name='historico_dados'),
    path('buscar/', views.buscar, name='buscar'),
    path('classificacao/', views.classificacao, name='classificacao'),
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
]