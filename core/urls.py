from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Autenticación
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Dashboards por Rol (CORREGIDO)
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/mesero/', views.mesero_dashboard, name='mesero_dashboard'),
    path('dashboard/cajero/', views.cajero_dashboard, name='cajero_dashboard'),
    path('dashboard/chef/', views.chef_dashboard, name='chef_dashboard'),
    
    # Vistas compartidas
    path('menu/', views.menu, name='menu'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pedido/crear/', views.crear_pedido, name='crear_pedido'),
    path('mesas/', views.mesas, name='mesas'),
    path('factura/<int:pedido_id>/', views.generar_factura, name='generar_factura'),
    
    # Cambio de estado de pedidos
    path('pedido/<int:pedido_id>/estado/chef/', views.cambiar_estado_pedido_chef, name='cambiar_estado_chef'),
    path('pedido/<int:pedido_id>/estado/mesero/', views.cambiar_estado_pedido_mesero, name='cambiar_estado_mesero'),
    path('pedido/<int:pedido_id>/estado/admin/', views.cambiar_estado_pedido_admin, name='cambiar_estado_admin'),
]