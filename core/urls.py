from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pedido/crear/', views.crear_pedido, name='crear_pedido'),
    path('mesas/', views.mesas, name='mesas'),
    path('factura/<int:pedido_id>/', views.generar_factura, name='generar_factura'),
]