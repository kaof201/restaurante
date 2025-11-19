from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Autenticación
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Dashboards por Rol
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('mesero/dashboard/', views.mesero_dashboard, name='mesero_dashboard'),
    path('cajero/dashboard/', views.cajero_dashboard, name='cajero_dashboard'),
    path('chef/dashboard/', views.chef_dashboard, name='chef_dashboard'),  # ← AGREGA ESTA LÍNEA
    
    # Vistas compartidas
    path('menu/', views.menu, name='menu'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pedido/crear/', views.crear_pedido, name='crear_pedido'),
    path('mesas/', views.mesas, name='mesas'),
    path('factura/<int:pedido_id>/', views.generar_factura, name='generar_factura'),
    
    # Cambio de estados (si los necesitas, agrégalos también)
    path('pedido/<int:pedido_id>/chef/estado/', views.cambiar_estado_pedido_chef, name='cambiar_estado_pedido_chef'),
    path('pedido/<int:pedido_id>/mesero/estado/', views.cambiar_estado_pedido_mesero, name='cambiar_estado_pedido_mesero'),
    path('pedido/<int:pedido_id>/admin/estado/', views.cambiar_estado_pedido_admin, name='cambiar_estado_pedido_admin'),
]