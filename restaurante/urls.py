
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Primero las rutas de la aplicación core (ANTES del admin)
    path('', include('core.urls')),
    
    # Después el admin de Django
    path('admin/', admin.site.urls),
]